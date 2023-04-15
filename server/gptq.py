# Copied from https://github.com/catid/GPTQ-for-LLaMa-65B-2GPU

import torch
import torch.nn as nn
import numpy as np
from torch.cuda.amp import custom_bwd, custom_fwd
import builtins
import math
import time
from transformers.models.llama.modeling_llama import LlamaAttention, apply_rotary_pos_emb
from transformers import AutoTokenizer
import transformers
import triton
import triton.language as tl
from typing import Dict

torch.backends.cuda.matmul.allow_tf32 = False
torch.backends.cudnn.allow_tf32 = False

class Autotuner(triton.KernelInterface):
	def __init__(self, fn, arg_names, configs, key, reset_to_zero, prune_configs_by: Dict = None, nearest_power_of_two: bool = False):
		'''
		:param prune_configs_by: a dict of functions that are used to prune configs, fields:
			'perf_model': performance model used to predicate running time with different configs, returns running time
			'top_k': number of configs to bench
			'prune_num_stages_by'(optional): a function used to prune num_stages. It take configs:List[Config] as its input, and returns pruned configs.
			'nearest_power_of_two'(optional): whether to round key arguments to the nearest power of two when caching tuning results
		'''
		if not configs:
			self.configs = [triton.Config({}, num_warps=4, num_stages=2)]
		else:
			self.configs = configs
		self.key_idx = [arg_names.index(k) for k in key]
		self.nearest_power_of_two = nearest_power_of_two
		self.cache = {}
		# hook to reset all required tensor to zeros before relaunching a kernel
		self.hook = lambda args: 0
		if reset_to_zero is not None:
			self.reset_idx = [arg_names.index(k) for k in reset_to_zero]

			def _hook(args):
				for i in self.reset_idx:
					args[i].zero_()
			self.hook = _hook
		self.arg_names = arg_names
		# prune configs
		if prune_configs_by:
			perf_model, top_k = prune_configs_by['perf_model'], prune_configs_by['top_k']
			if 'early_config_prune' in prune_configs_by:
				early_config_prune = prune_configs_by['early_config_prune']
		else:
			perf_model, top_k, early_config_prune = None, None, None
		self.perf_model, self.configs_top_k = perf_model, top_k
		self.early_config_prune = early_config_prune
		self.fn = fn

	def _bench(self, *args, config, **meta):
		# check for conflicts, i.e. meta-parameters both provided
		# as kwargs and by the autotuner
		conflicts = meta.keys() & config.kwargs.keys()
		if conflicts:
			raise ValueError(
				f"Conflicting meta-parameters: {', '.join(conflicts)}."
				" Make sure that you don't re-define auto-tuned symbols."
			)
		# augment meta-parameters with tunable ones
		current = dict(meta, **config.kwargs)

		def kernel_call():
			if config.pre_hook:
				config.pre_hook(self.nargs)
			self.hook(args)
			self.fn.run(*args, num_warps=config.num_warps, num_stages=config.num_stages, **current)
		try:
			# In testings using only 40 reps seems to be close enough and it appears to be what PyTorch uses
			# PyTorch also sets fast_flush to True, but I didn't see any speedup so I'll leave the default
			return triton.testing.do_bench(kernel_call, percentiles=(0.5, 0.2, 0.8), rep=40)
		except triton.compiler.OutOfResources:
			return (float('inf'), float('inf'), float('inf'))	

	def run(self, *args, **kwargs):
		self.nargs = dict(zip(self.arg_names, args))
		if len(self.configs) > 1:
			key = tuple(args[i] for i in self.key_idx)

			# This reduces the amount of autotuning by rounding the keys to the nearest power of two
			# In my testing this gives decent results, and greatly reduces the amount of tuning required
			if self.nearest_power_of_two:
				key = tuple([2 ** int(math.log2(x) + 0.5) for x in key])
			
			if key not in self.cache:
				# prune configs
				pruned_configs = self.prune_configs(kwargs)
				bench_start = time.time()
				timings = {config: self._bench(*args, config=config, **kwargs)
							for config in pruned_configs}
				bench_end = time.time()
				self.bench_time = bench_end - bench_start
				self.cache[key] = builtins.min(timings, key=timings.get)
				self.hook(args)
				self.configs_timings = timings
			config = self.cache[key]
		else:
			config = self.configs[0]
		self.best_config = config
		if config.pre_hook is not None:
			config.pre_hook(self.nargs)
		return self.fn.run(*args, num_warps=config.num_warps, num_stages=config.num_stages, **kwargs, **config.kwargs)

	def prune_configs(self, kwargs):
		pruned_configs = self.configs
		if self.early_config_prune:
			pruned_configs = self.early_config_prune(self.configs, self.nargs)
		if self.perf_model:
			top_k = self.configs_top_k
			if isinstance(top_k, float) and top_k <= 1.0:
				top_k = int(len(self.configs) * top_k)
			if len(pruned_configs) > top_k:
				est_timing = {
					config: self.perf_model(**self.nargs, **kwargs, **config.kwargs, num_stages=config.num_stages,
											num_warps=config.num_warps)
					for config in pruned_configs
				}
				pruned_configs = sorted(est_timing.keys(), key=lambda x: est_timing[x])[:top_k]
		return pruned_configs

	def warmup(self, *args, **kwargs):
		self.nargs = dict(zip(self.arg_names, args))
		for config in self.prune_configs(kwargs):
			self.fn.warmup(
				*args,
				num_warps=config.num_warps,
				num_stages=config.num_stages,
				**kwargs,
				**config.kwargs,
			)
		self.nargs = None

def autotune(configs, key, prune_configs_by=None, reset_to_zero=None, nearest_power_of_two=False):
	"""
	Decorator for auto-tuning a :code:`triton.jit`'d function.
	.. highlight:: python
	.. code-block:: python
		@triton.autotune(configs=[
			triton.Config(meta={'BLOCK_SIZE': 128}, num_warps=4),
			triton.Config(meta={'BLOCK_SIZE': 1024}, num_warps=8),
			],
			key=['x_size'] # the two above configs will be evaluated anytime
							# the value of x_size changes
		)
		@triton.jit
		def kernel(x_ptr, x_size, **META):
			BLOCK_SIZE = META['BLOCK_SIZE']
	:note: When all the configurations are evaluated, the kernel will run multiple time.
			This means that whatever value the kernel updates will be updated multiple times.
			To avoid this undesired behavior, you can use the `reset_to_zero` argument, which
			reset the value of the provided tensor to `zero` before running any configuration.
	:param configs: a list of :code:`triton.Config` objects
	:type configs: list[triton.Config]
	:param key: a list of argument names whose change in value will trigger the evaluation of all provided configs.
	:type key: list[str]
	:param prune_configs_by: a dict of functions that are used to prune configs, fields:
		'perf_model': performance model used to predicate running time with different configs, returns running time
		'top_k': number of configs to bench
		'early_config_prune'(optional): a function used to do early prune (eg, num_stages). It take configs:List[Config] as its input, and returns pruned configs.
	:param reset_to_zero: a list of argument names whose value will be reset to zero before evaluating any configs.
	:type reset_to_zero: list[str]
	"""
	def decorator(fn):
		return Autotuner(fn, fn.arg_names, configs, key, reset_to_zero, prune_configs_by, nearest_power_of_two)

	return decorator

def matmul4_kernel_config_pruner(configs, nargs):
    """
    The main purpose of this function is to shrink BLOCK_SIZE_* when the corresponding dimension is smaller.
    """
    m = max(2 ** int(math.ceil(math.log2(nargs['M']))), 16)
    n = max(2 ** int(math.ceil(math.log2(nargs['N']))), 16)
    k = max(2 ** int(math.ceil(math.log2(nargs['K']))), 16)

    used = set()
    for config in configs:
        block_size_m = min(m, config.kwargs['BLOCK_SIZE_M'])
        block_size_n = min(n, config.kwargs['BLOCK_SIZE_N'])
        block_size_k = min(k, config.kwargs['BLOCK_SIZE_K'])
        group_size_m = config.kwargs['GROUP_SIZE_M']

        if (block_size_m, block_size_n, block_size_k, group_size_m, config.num_stages, config.num_warps) in used:
            continue

        used.add((block_size_m, block_size_n, block_size_k, group_size_m, config.num_stages, config.num_warps))
        yield triton.Config({'BLOCK_SIZE_M': block_size_m, 'BLOCK_SIZE_N': block_size_n, 'BLOCK_SIZE_K': block_size_k, 'GROUP_SIZE_M': group_size_m}, num_stages=config.num_stages, num_warps=config.num_warps)

# code based https://github.com/fpgaminer/GPTQ-triton
@autotune(
    configs=[
        triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 256, 'BLOCK_SIZE_K': 32, 'GROUP_SIZE_M': 8}, num_stages=4, num_warps=4),
        triton.Config({'BLOCK_SIZE_M': 128, 'BLOCK_SIZE_N': 128, 'BLOCK_SIZE_K': 32, 'GROUP_SIZE_M': 8}, num_stages=4, num_warps=4),
        triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 128, 'BLOCK_SIZE_K': 32, 'GROUP_SIZE_M': 8}, num_stages=4, num_warps=4),
        triton.Config({'BLOCK_SIZE_M': 128, 'BLOCK_SIZE_N': 32, 'BLOCK_SIZE_K': 32, 'GROUP_SIZE_M': 8}, num_stages=4, num_warps=4),
        triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 64, 'BLOCK_SIZE_K': 32, 'GROUP_SIZE_M': 8}, num_stages=4, num_warps=4),
        triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 128, 'BLOCK_SIZE_K': 32, 'GROUP_SIZE_M': 8}, num_stages=2, num_warps=8),
        triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 64, 'BLOCK_SIZE_K': 64, 'GROUP_SIZE_M': 8}, num_stages=3, num_warps=8),
        triton.Config({'BLOCK_SIZE_M': 32, 'BLOCK_SIZE_N': 32, 'BLOCK_SIZE_K': 128, 'GROUP_SIZE_M': 8}, num_stages=2, num_warps=4),
    ],
    key=['M', 'N', 'K'],
    nearest_power_of_two=True,
    prune_configs_by={
        'early_config_prune': matmul4_kernel_config_pruner,
        'perf_model': None,
        'top_k': None,
    },
)

@triton.jit
def matmul_248_kernel(a_ptr, b_ptr, c_ptr,
                        scales_ptr, zeros_ptr, g_ptr,
                        M, N, K, bits, maxq,
                        stride_am, stride_ak,
                        stride_bk, stride_bn,
                        stride_cm, stride_cn,
                        stride_scales, stride_zeros,
                        BLOCK_SIZE_M: tl.constexpr, BLOCK_SIZE_N: tl.constexpr, BLOCK_SIZE_K: tl.constexpr,
                        GROUP_SIZE_M: tl.constexpr):
    """
    Compute the matrix multiplication C = A x B.
    A is of shape (M, K) float16
    B is of shape (K//8, N) int32
    C is of shape (M, N) float16
    scales is of shape (G, N) float16
    zeros is of shape (G, N) float16
    g_ptr is of shape (K) int32 
    """
    infearure_per_bits = 32 // bits

    pid = tl.program_id(axis=0)
    num_pid_m = tl.cdiv(M, BLOCK_SIZE_M)
    num_pid_n = tl.cdiv(N, BLOCK_SIZE_N)
    num_pid_k = tl.cdiv(K, BLOCK_SIZE_K)
    num_pid_in_group = GROUP_SIZE_M * num_pid_n
    group_id = pid // num_pid_in_group
    first_pid_m = group_id * GROUP_SIZE_M
    group_size_m = min(num_pid_m - first_pid_m, GROUP_SIZE_M)
    pid_m = first_pid_m + (pid % group_size_m)
    pid_n = (pid % num_pid_in_group) // group_size_m

    offs_am = pid_m * BLOCK_SIZE_M + tl.arange(0, BLOCK_SIZE_M)
    offs_bn = pid_n * BLOCK_SIZE_N + tl.arange(0, BLOCK_SIZE_N)
    offs_k = tl.arange(0, BLOCK_SIZE_K)
    a_ptrs = a_ptr + (offs_am[:, None] * stride_am + offs_k[None, :] * stride_ak)   # (BLOCK_SIZE_M, BLOCK_SIZE_K)
    a_mask = (offs_am[:, None] < M)
    # b_ptrs is set up such that it repeats elements along the K axis 8 times
    b_ptrs = b_ptr + ((offs_k[:, None] // infearure_per_bits) * stride_bk + offs_bn[None, :] * stride_bn)   # (BLOCK_SIZE_K, BLOCK_SIZE_N)
    g_ptrs = g_ptr + offs_k
    # shifter is used to extract the N bits of each element in the 32-bit word from B
    scales_ptrs = scales_ptr + offs_bn[None, :]
    zeros_ptrs = zeros_ptr + (offs_bn[None, :]// infearure_per_bits) 
    
    shifter = (offs_k % infearure_per_bits) * bits
    zeros_shifter = (offs_bn % infearure_per_bits) * bits
    accumulator = tl.zeros((BLOCK_SIZE_M, BLOCK_SIZE_N), dtype=tl.float32)
            
    for k in range(0, num_pid_k):
        g_idx = tl.load(g_ptrs)

        # Fetch scales and zeros; these are per-outfeature and thus reused in the inner loop
        scales = tl.load(scales_ptrs + g_idx[:, None] * stride_scales)  # (BLOCK_SIZE_K, BLOCK_SIZE_N,)
        zeros = tl.load(zeros_ptrs + g_idx[:, None] * stride_zeros)  # (BLOCK_SIZE_K, BLOCK_SIZE_N,)
        
        zeros = (zeros >> zeros_shifter[None, :]) & maxq
        zeros = (zeros + 1)
        
        a = tl.load(a_ptrs, mask=a_mask, other=0.)   # (BLOCK_SIZE_M, BLOCK_SIZE_K)
        b = tl.load(b_ptrs)   # (BLOCK_SIZE_K, BLOCK_SIZE_N), but repeated

        # Now we need to unpack b (which is N-bit values) into 32-bit values
        b = (b >> shifter[:, None]) & maxq  # Extract the N-bit values
        b = (b - zeros) * scales  # Scale and shift

        accumulator += tl.dot(a, b)
        a_ptrs += BLOCK_SIZE_K
        b_ptrs += (BLOCK_SIZE_K // infearure_per_bits) * stride_bk
        g_ptrs += BLOCK_SIZE_K

    c = accumulator.to(tl.float16)
    c_ptrs = c_ptr + stride_cm * offs_am[:, None] + stride_cn * offs_bn[None, :]
    c_mask = (offs_am[:, None] < M) & (offs_bn[None, :] < N)
    tl.store(c_ptrs, accumulator, mask=c_mask)

# code based https://github.com/fpgaminer/GPTQ-triton
def transpose_matmul4_kernel_config_pruner(configs, nargs):
    """
    The main purpose of this function is to shrink BLOCK_SIZE_* when the corresponding dimension is smaller.
    """
    m = max(2 ** int(math.ceil(math.log2(nargs['M']))), 16)
    n = max(2 ** int(math.ceil(math.log2(nargs['N']))), 16)
    k = max(2 ** int(math.ceil(math.log2(nargs['K']))), 16)

    used = set()
    for config in configs:
        block_size_m = min(m, config.kwargs['BLOCK_SIZE_M'])
        block_size_n = min(n, config.kwargs['BLOCK_SIZE_N'])
        block_size_k = min(k, config.kwargs['BLOCK_SIZE_K'])
        group_size_m = config.kwargs['GROUP_SIZE_M']

        if (block_size_m, block_size_n, block_size_k, group_size_m, config.num_stages, config.num_warps) in used:
            continue

        used.add((block_size_m, block_size_n, block_size_k, group_size_m, config.num_stages, config.num_warps))
        yield triton.Config({'BLOCK_SIZE_M': block_size_m, 'BLOCK_SIZE_N': block_size_n, 'BLOCK_SIZE_K': block_size_k, 'GROUP_SIZE_M': group_size_m}, num_stages=config.num_stages, num_warps=config.num_warps)

@autotune(
    configs=[
        triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 32, 'BLOCK_SIZE_K': 256, 'GROUP_SIZE_M': 8}, num_stages=4, num_warps=4),
        triton.Config({'BLOCK_SIZE_M': 128, 'BLOCK_SIZE_N': 32, 'BLOCK_SIZE_K': 128, 'GROUP_SIZE_M': 8}, num_stages=4, num_warps=4),
        triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 32, 'BLOCK_SIZE_K': 128, 'GROUP_SIZE_M': 8}, num_stages=4, num_warps=4),
        triton.Config({'BLOCK_SIZE_M': 128, 'BLOCK_SIZE_N': 32, 'BLOCK_SIZE_K': 32, 'GROUP_SIZE_M': 8}, num_stages=4, num_warps=4),
        triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 32, 'BLOCK_SIZE_K': 64, 'GROUP_SIZE_M': 8}, num_stages=4, num_warps=4),
        triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 32, 'BLOCK_SIZE_K': 128, 'GROUP_SIZE_M': 8}, num_stages=2, num_warps=8),
        triton.Config({'BLOCK_SIZE_M': 64, 'BLOCK_SIZE_N': 64, 'BLOCK_SIZE_K': 64, 'GROUP_SIZE_M': 8}, num_stages=3, num_warps=8),
        triton.Config({'BLOCK_SIZE_M': 32, 'BLOCK_SIZE_N': 128, 'BLOCK_SIZE_K': 32, 'GROUP_SIZE_M': 8}, num_stages=2, num_warps=4),
    ],
    key=['M', 'N', 'K'],
    nearest_power_of_two=True,
    prune_configs_by={
        'early_config_prune': transpose_matmul4_kernel_config_pruner,
        'perf_model': None,
        'top_k': None,
    },
)

@triton.jit
def transpose_matmul_248_kernel(a_ptr, b_ptr, c_ptr,
                                scales_ptr, zeros_ptr, g_ptr,
                                M, N, K, bits, maxq,
                                stride_am, stride_ak,
                                stride_bk, stride_bn,
                                stride_cm, stride_cn,
                                stride_scales, stride_zeros,
                                BLOCK_SIZE_M: tl.constexpr, BLOCK_SIZE_N: tl.constexpr, BLOCK_SIZE_K: tl.constexpr,
                                GROUP_SIZE_M: tl.constexpr):
    """
    Compute the matrix multiplication C = A x B.
    A is of shape (M, N) float16
    B is of shape (K//8, N) int32
    C is of shape (M, K) float16
    scales is of shape (G, N) float16
    zeros is of shape (G, N) float16
    g_ptr is of shape (K) int32 
    """
    infearure_per_bits = 32 // bits

    pid = tl.program_id(axis=0)
    num_pid_m = tl.cdiv(M, BLOCK_SIZE_M)
    num_pid_k = tl.cdiv(K, BLOCK_SIZE_K)
    num_pid_n = tl.cdiv(N, BLOCK_SIZE_N)
    num_pid_in_group = GROUP_SIZE_M * num_pid_k
    group_id = pid // num_pid_in_group
    first_pid_m = group_id * GROUP_SIZE_M
    group_size_m = min(num_pid_m - first_pid_m, GROUP_SIZE_M)
    pid_m = first_pid_m + (pid % group_size_m)
    pid_k = (pid % num_pid_in_group) // group_size_m

    offs_am = pid_m * BLOCK_SIZE_M + tl.arange(0, BLOCK_SIZE_M)
    offs_bk = pid_k * BLOCK_SIZE_K + tl.arange(0, BLOCK_SIZE_K)
    offs_n = tl.arange(0, BLOCK_SIZE_N)
    a_ptrs = a_ptr + (offs_am[:, None] * stride_am + offs_n[None, :] * stride_ak)   # (BLOCK_SIZE_M, BLOCK_SIZE_N)
    a_mask = (offs_am[:, None] < M)
    # b_ptrs is set up such that it repeats elements along the K axis 8 times
    b_ptrs = b_ptr + ((offs_bk[:, None] // infearure_per_bits) * stride_bk + offs_n[None, :] * stride_bn)   # (BLOCK_SIZE_K, BLOCK_SIZE_N)
    g_ptrs = g_ptr + offs_bk
    g_idx = tl.load(g_ptrs)
    
    # shifter is used to extract the N bits of each element in the 32-bit word from B
    scales_ptrs = scales_ptr + offs_n[None, :]  + g_idx[:, None] * stride_scales
    zeros_ptrs = zeros_ptr + (offs_n[None, :]// infearure_per_bits) + g_idx[:, None] * stride_zeros
    
    shifter = (offs_bk % infearure_per_bits) * bits
    zeros_shifter = (offs_n % infearure_per_bits) * bits
    accumulator = tl.zeros((BLOCK_SIZE_M, BLOCK_SIZE_K), dtype=tl.float32)
    
    for k in range(0, num_pid_n):
        # Fetch scales and zeros; these are per-outfeature and thus reused in the inner loop
        scales = tl.load(scales_ptrs)  # (BLOCK_SIZE_K, BLOCK_SIZE_N,)
        zeros = tl.load(zeros_ptrs)  # (BLOCK_SIZE_K, BLOCK_SIZE_N,)
        
        zeros = (zeros >> zeros_shifter[None, :]) & maxq
        zeros = (zeros + 1)
        
        a = tl.load(a_ptrs, mask=a_mask, other=0.)   # (BLOCK_SIZE_M, BLOCK_SIZE_N)
        b = tl.load(b_ptrs)   # (BLOCK_SIZE_K, BLOCK_SIZE_N), but repeated

        # Now we need to unpack b (which is N-bit values) into 32-bit values
        b = (b >> shifter[:, None]) & maxq  # Extract the N-bit values
        b = (b - zeros) * scales  # Scale and shift
        b = tl.trans(b)

        accumulator += tl.dot(a, b)
        a_ptrs += BLOCK_SIZE_N
        b_ptrs += BLOCK_SIZE_N
        scales_ptrs += BLOCK_SIZE_N
        zeros_ptrs += (BLOCK_SIZE_N // infearure_per_bits)
        
    c = accumulator.to(tl.float16)
    c_ptrs = c_ptr + stride_cm * offs_am[:, None] + stride_cn * offs_bk[None, :]
    c_mask = (offs_am[:, None] < M) & (offs_bk[None, :] < K)
    tl.store(c_ptrs, accumulator, mask=c_mask)

def matmul248(input, qweight, scales, qzeros, g_idx, bits, maxq):
    with torch.cuda.device(input.device):
        output = torch.empty((input.shape[0], qweight.shape[1]), device='cuda', dtype=torch.float16)
        grid = lambda META: (triton.cdiv(input.shape[0], META['BLOCK_SIZE_M']) * triton.cdiv(qweight.shape[1], META['BLOCK_SIZE_N']),)
        matmul_248_kernel[grid](input, qweight, output,
                                scales, qzeros, g_idx,
                                input.shape[0], qweight.shape[1], input.shape[1], bits, maxq,
                                input.stride(0), input.stride(1),
                                qweight.stride(0), qweight.stride(1),
                                output.stride(0), output.stride(1),
                                scales.stride(0), qzeros.stride(0))
        return output

def transpose_matmul248(input, qweight, scales, qzeros, g_idx, bits, maxq):
    with torch.cuda.device(input.device):
        output_dim = (qweight.shape[0] * 32) // bits
        output = torch.empty((input.shape[0], output_dim), device='cuda', dtype=torch.float16)
        grid = lambda META: (triton.cdiv(input.shape[0], META['BLOCK_SIZE_M']) * triton.cdiv(output_dim, META['BLOCK_SIZE_K']),)
        transpose_matmul_248_kernel[grid](input, qweight, output,
                                        scales, qzeros, g_idx,
                                        input.shape[0], qweight.shape[1], output_dim, bits, maxq,
                                        input.stride(0), input.stride(1),
                                        qweight.stride(0), qweight.stride(1),
                                        output.stride(0), output.stride(1),
                                        scales.stride(0), qzeros.stride(0))
        return output

class QuantLinearFunction(torch.autograd.Function):
    @staticmethod
    @custom_fwd(cast_inputs=torch.float16)
    def forward(ctx, input, qweight, scales, qzeros, g_idx, bits, maxq):
        output = matmul248(input, qweight, scales, qzeros, g_idx, bits, maxq)
        ctx.save_for_backward(qweight, scales, qzeros, g_idx)
        ctx.bits,ctx.maxq = bits, maxq
        return output
    
    @staticmethod
    @custom_bwd
    def backward(ctx, grad_output):
        qweight, scales, qzeros, g_idx = ctx.saved_tensors
        bits, maxq = ctx.bits, ctx.maxq
        grad_input = None

        if ctx.needs_input_grad[0]:
            grad_input = transpose_matmul248(grad_output, qweight, scales, qzeros, g_idx, bits, maxq)
        return grad_input, None, None, None, None, None, None
    
class QuantLinear(nn.Module): 
    def __init__(self, bits, groupsize, infeatures, outfeatures, bias):
        super().__init__()
        if bits not in [2,4,8]:
            raise NotImplementedError("Only 2,4,8 bits are supported.")
        self.infeatures = infeatures
        self.outfeatures = outfeatures
        self.bits = bits
        self.maxq = 2 ** self.bits - 1
        self.groupsize = groupsize if groupsize != -1 else infeatures
        
        self.register_buffer('qweight', torch.zeros((infeatures // 32 * self.bits, outfeatures), dtype=torch.int32))
        self.register_buffer('qzeros', torch.zeros((math.ceil(infeatures / self.groupsize), outfeatures // 32 * self.bits), dtype=torch.int32))
        self.register_buffer('scales', torch.zeros((math.ceil(infeatures / self.groupsize), outfeatures), dtype=torch.float16))
        self.register_buffer('g_idx', torch.tensor([i // self.groupsize  for i in range(infeatures)], dtype = torch.int32))
        if bias:
            self.register_buffer('bias', torch.zeros((outfeatures),dtype=torch.float16))
        else:
            self.bias = None
        
    def pack(self, linear, scales, zeros, g_idx = None):
        self.g_idx = g_idx.clone() if g_idx is not None else self.g_idx
        
        scales = scales.t().contiguous()
        zeros = zeros.t().contiguous()
        scale_zeros = zeros * scales
        self.scales = scales.clone().half()
        if linear.bias is not None:
            self.bias = linear.bias.clone().half()
            
        intweight = []
        for idx in range(self.infeatures):
            intweight.append(torch.round((linear.weight.data[:,idx] + scale_zeros[self.g_idx[idx]]) / self.scales[self.g_idx[idx]]).to(torch.int)[:,None])
        intweight = torch.cat(intweight,dim=1)
        intweight = intweight.t().contiguous()
        intweight = intweight.numpy().astype(np.uint32)
        qweight = np.zeros((intweight.shape[0] // 32 * self.bits, intweight.shape[1]), dtype=np.uint32)
        i = 0
        row = 0
        while row < qweight.shape[0]:
            if self.bits in [2,4,8]:
                for j in range(i, i + (32//self.bits)):
                    qweight[row] |= intweight[j] << (self.bits * (j - i))
                i += 32//self.bits
                row += 1
            else:
                raise NotImplementedError("Only 2,4,8 bits are supported.")
                
        qweight = qweight.astype(np.int32)
        self.qweight = torch.from_numpy(qweight) 
        
        zeros -= 1;
        zeros = zeros.numpy().astype(np.uint32)
        qzeros = np.zeros((zeros.shape[0], zeros.shape[1] // 32 * self.bits), dtype=np.uint32)
        i = 0
        col = 0
        while col < qzeros.shape[1]:
            if self.bits in [2,4,8]:
                for j in range(i, i + (32//self.bits)):
                    qzeros[:, col] |= zeros[:, j] << (self.bits * (j - i))
                i += 32//self.bits
                col += 1
            else:
                raise NotImplementedError("Only 2,4,8 bits are supported.")
                
        qzeros = qzeros.astype(np.int32)
        self.qzeros = torch.from_numpy(qzeros) 
        
    def forward(self, x):
        out_shape = x.shape[:-1] + (self.outfeatures, )
        out = QuantLinearFunction.apply(x.reshape(-1,x.shape[-1]), self.qweight, self.scales, 
                                        self.qzeros, self.g_idx, self.bits, self.maxq)
        out = out + self.bias if self.bias is not None else out  
        return out.reshape(out_shape)
        
def make_quant_attn(model):
    """
    Replace all LlamaAttention modules with QuantLlamaAttention modules, fusing the q, k, v projections.
    """
    for name, m in model.named_modules():
        if not isinstance(m, LlamaAttention):
            continue

        q_proj = m.q_proj
        k_proj = m.k_proj
        v_proj = m.v_proj

        qweights = torch.cat([q_proj.qweight, k_proj.qweight, v_proj.qweight], dim=1)
        qzeros = torch.cat([q_proj.qzeros, k_proj.qzeros, v_proj.qzeros], dim=1)
        scales = torch.cat([q_proj.scales, k_proj.scales, v_proj.scales], dim=1)
        g_idx = torch.cat([q_proj.g_idx, k_proj.g_idx, v_proj.g_idx], dim=0)
        bias = torch.cat([q_proj.bias, k_proj.bias, v_proj.bias], dim=0) if q_proj.bias is not None else None

        qkv_layer = QuantLinear(q_proj.bits, q_proj.groupsize, q_proj.infeatures, q_proj.outfeatures + k_proj.outfeatures + v_proj.outfeatures, True if q_proj.bias is not None else False)
        qkv_layer.qweight = qweights
        qkv_layer.qzeros = qzeros
        qkv_layer.scales = scales
        qkv_layer.g_idx = g_idx
        qkv_layer.bias = bias

        attn = QuantLlamaAttention(m.hidden_size, m.num_heads, qkv_layer, m.o_proj, m.rotary_emb)

        if '.' in name:
            parent_name = name.rsplit('.', 1)[0]
            child_name = name[len(parent_name) + 1:]
            parent = model.get_submodule(parent_name)
        else:
            parent_name = ''
            parent = model
            child_name = name

        #print(f"Replacing {name} with quant_attn; parent: {parent_name}, child's name: {child_name}")

        setattr(parent, child_name, attn)


class QuantLlamaAttention(nn.Module):
    """Multi-headed attention from 'Attention Is All You Need' paper"""

    def __init__(self,hidden_size,num_heads,qkv_proj,o_proj,rotary_emb,):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_heads = num_heads
        self.head_dim = hidden_size // num_heads

        if (self.head_dim * num_heads) != self.hidden_size:
            raise ValueError(f"hidden_size must be divisible by num_heads (got `hidden_size`: {self.hidden_size}"f" and `num_heads`: {num_heads}).")
        self.qkv_proj = qkv_proj
        self.o_proj = o_proj
        self.rotary_emb = rotary_emb

    def _shape(self, tensor, seq_len, bsz):
        return tensor.view(bsz, seq_len, self.num_heads, self.head_dim).transpose(1, 2).contiguous()

    def forward(self,hidden_states,past_key_value = None,attention_mask = None,position_ids = None, output_attentions = False,use_cache= False):
        """Input shape: Batch x Time x Channel"""

        bsz, q_len, _ = hidden_states.size()

        qkv_states = self.qkv_proj(hidden_states)
        query_states, key_states, value_states = torch.split(qkv_states, self.hidden_size, dim=2)

        query_states = query_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)
        key_states = key_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)
        value_states = value_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)

        kv_seq_len = key_states.shape[-2]
        if past_key_value is not None:
            kv_seq_len += past_key_value[0].shape[-2]
        cos, sin = self.rotary_emb(value_states, seq_len=kv_seq_len)
        query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin, position_ids)
        # [bsz, nh, t, hd]

        if past_key_value is not None:
            # reuse k, v, self_attention
            key_states = torch.cat([past_key_value[0], key_states], dim=2)
            value_states = torch.cat([past_key_value[1], value_states], dim=2)

        past_key_value = (key_states, value_states) if use_cache else None

        attn_weights = torch.matmul(query_states, key_states.transpose(2, 3)) / math.sqrt(self.head_dim)

        if attn_weights.size() != (bsz, self.num_heads, q_len, kv_seq_len):
            raise ValueError(
                f"Attention weights should be of size {(bsz * self.num_heads, q_len, kv_seq_len)}, but is"
                f" {attn_weights.size()}"
            )

        if attention_mask is not None:
            if attention_mask.size() != (bsz, 1, q_len, kv_seq_len):
                raise ValueError(
                    f"Attention mask should be of size {(bsz, 1, q_len, kv_seq_len)}, but is {attention_mask.size()}"
                )
            attn_weights = attn_weights + attention_mask
            attn_weights = torch.max(attn_weights, torch.tensor(torch.finfo(attn_weights.dtype).min))

        # upcast attention to fp32
        attn_weights = nn.functional.softmax(attn_weights, dim=-1, dtype=torch.float32).to(query_states.dtype)
        attn_output = torch.matmul(attn_weights, value_states)

        if attn_output.size() != (bsz, self.num_heads, q_len, self.head_dim):
            raise ValueError(
                f"`attn_output` should be of size {(bsz, self.num_heads, q_len, self.head_dim)}, but is"
                f" {attn_output.size()}"
            )

        attn_output = attn_output.transpose(1, 2)
        attn_output = attn_output.reshape(bsz, q_len, self.hidden_size)

        attn_output = self.o_proj(attn_output)

        if not output_attentions:
            attn_weights = None

        return attn_output, attn_weights, past_key_value
        
def autotune_warmup(model, transpose = False):
    """
    Pre-tunes the quantized kernel
    """
    from tqdm import tqdm

    kn_values  = {}

    for _, m in model.named_modules():
        if not isinstance(m, QuantLinear):
            continue

        k = m.infeatures
        n = m.outfeatures
        
        if (k, n) not in kn_values:
            kn_values[(k, n)] = (m.qweight.cuda(), m.scales.cuda(), m.qzeros.cuda(), m.g_idx.cuda(), m.bits, m.maxq)

    print(f'Found {len(kn_values)} unique KN values.')

    print('Warming up autotune cache ...')
    with torch.no_grad():
        for m in tqdm(range(0, 12)):
            m = 2 ** m   # [1, 2048]
            for (k, n), (qweight, scales, qzeros, g_idx, bits, maxq) in kn_values.items():
                a = torch.randn(m, k, dtype=torch.float16, device='cuda')
                matmul248(a, qweight, scales, qzeros, g_idx, bits, maxq)
                if transpose:
                    a = torch.randn(m, n, dtype=torch.float16, device='cuda')
                    transpose_matmul248(a, qweight, scales, qzeros, g_idx, bits, maxq)
    del kn_values
        
def make_quant(module, names, bits, groupsize, name=''):
    if isinstance(module, QuantLinear):
        return
    for attr in dir(module):
        tmp = getattr(module, attr)
        name1 = name + '.' + attr if name != '' else attr
        if name1 in names:
            delattr(module, attr)
            setattr(module, attr, QuantLinear(bits, groupsize, tmp.in_features, tmp.out_features, tmp.bias is not None))
    for name1, child in module.named_children():
        make_quant(child, names, bits, groupsize, name + '.' + name1 if name != '' else name1)

def find_layers(module, layers=[nn.Conv2d, nn.Linear], name=''):
    if type(module) in layers:
        return {name: module}
    res = {}
    for name1, child in module.named_children():
        res.update(find_layers(
            child, layers=layers, name=name + '.' + name1 if name != '' else name1
        ))
    return res

def load_quant(model, checkpoint, wbits, groupsize, device, warmup_autotune = True):
    from transformers import LlamaConfig, LlamaForCausalLM 
    config = LlamaConfig.from_pretrained(model)
    def noop(*args, **kwargs):
        pass
    torch.nn.init.kaiming_uniform_ = noop 
    torch.nn.init.uniform_ = noop 
    torch.nn.init.normal_ = noop 

    torch.set_default_dtype(torch.half)
    transformers.modeling_utils._init_weights = False
    torch.set_default_dtype(torch.half)
    model = LlamaForCausalLM(config)
    torch.set_default_dtype(torch.float)
    model = model.eval()
    layers = find_layers(model)
    for name in ['lm_head']:
        if name in layers:
            del layers[name]
    make_quant(model, layers, wbits, groupsize)

    print('Loading model ...')
    if checkpoint.endswith('.safetensors'):
        from safetensors.torch import load_file as safe_load
        if device == -1:
            device = "cpu"
        model.load_state_dict(safe_load(checkpoint, device))
    else:
        model.load_state_dict(torch.load(checkpoint))
        
    make_quant_attn(model)

    if warmup_autotune:
        autotune_warmup(model)
    model.seqlen = 2048
    print('Done.')

    return model
