import multiprocessing
import logging
import time
from queue import Empty
from typing import List, Tuple, Any

from autopy import autopy_func, autopy_func_improve, autopy_test, autopy_test_improve, autopy_code_judge, autopy_test_judge

class JobWorkers:
    def __init__(self, args):
        self.workers = []
        self.args = args
        self.active_workers = multiprocessing.Value('i', 0)

    def process_next(self, args, task_op, task_id, code, test, result_queue):
        if task_op == "code":
            #logging.info("Generating code...")
            t0 = time.time()
            code = autopy_func(args.comments, args.prototype, node=args.node, port=args.port, temperature=args.temperature, max_tokens=args.max_tokens)
            t1 = time.time()

            if len(code) > 0:
                score = autopy_code_judge(code, args.function_name, node=args.node, port=args.port)
            else:
                score = 0
            t2 = time.time()

            logging.info(f"Generated code len={len(code)} in {t1 - t0} seconds, with score {score} (scored in {t2 - t1} seconds)")

            result_queue.put((task_op, task_id, score, code))

        elif task_op == "test":
            #logging.info("Generating test...")
            t0 = time.time()
            test = autopy_test(args.comments, args.prototype, args.function_name, node=args.node, port=args.port, temperature=args.temperature, max_tokens=args.max_tokens)
            t1 = time.time()

            logging.info(f"Generated test len={len(test)} in {t1 - t0} seconds")
            result_queue.put((task_op, task_id, None, test))

        elif task_op == "improve_code":
            #logging.info("Improving code...")
            t0 = time.time()
            improved_code = autopy_func_improve(args.comments, code, node=args.node, port=args.port, temperature=args.temperature, max_tokens=args.max_tokens)
            t1 = time.time()

            if len(improved_code) > 0:
                score = autopy_code_judge(improved_code, args.function_name, node=args.node, port=args.port)
            else:
                score = 0
            t2 = time.time()

            logging.info(f"Generated improved code input len={len(code)} output len={len(improved_code)} in {t1 - t0} seconds, with new score {score} (scored in {t2 - t1} seconds)")
            result_queue.put(("improve_code", task_id, score, improved_code))

        elif task_op == "improve_test":
            #logging.info("Improving test...")
            t0 = time.time()
            improved_test = autopy_test_improve(args.comments, args.prototype, args.function_name, test, node=args.node, port=args.port, temperature=args.temperature, max_tokens=args.max_tokens)
            t1 = time.time()

            logging.info(f"Generated improved test input len={len(test)} output len={len(improved_test)} in {t1 - t0} seconds")
            result_queue.put((task_op, task_id, None, improved_test))

        elif task_op == "judge_pair":
            #logging.info("Judging pair...")
            t0 = time.time()
            score = autopy_test_judge(code, args.function_name, test, node=args.node, port=args.port)
            t1 = time.time()

            logging.info(f"Judged code/test pair with score {score} in {t1 - t0} seconds")
            result_queue.put((task_op, task_id, score, None))

    def worker(self, work_queue, result_queue, worker_id):
        args = self.args

        while True:
            try:
                (task_op, task_id, code, test) = work_queue.get(timeout=2.0)
            except Empty:
                logging.info(f"Worker {worker_id} idle... (2 seconds)")
                continue

            with self.active_workers.get_lock():
                self.active_workers.value += 1

            try:
                self.process_next(args, task_op, task_id, code, test, result_queue)
            except Exception as e:
                logging.error(f"Worker {worker_id} error: {e}")

            with self.active_workers.get_lock():
                self.active_workers.value -= 1

    def launch(self, work_queue, result_queue):
        for worker_id in range(self.args.workers):
            p = multiprocessing.Process(target=self.worker, args=(work_queue, result_queue, worker_id))
            p.start()
            self.workers.append(p)

    def terminate(self):
        for worker in self.workers:
            worker.terminate()

class JobManager:
    def __init__(self, args):
        self.past_jobs = []
        self.work_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()
        self.next_job_id = 0
        self.args = args
        self.workers = JobWorkers(args)
        self.workers.launch(self.work_queue, self.result_queue)

    def _add_job(self, task_op, code = None, test = None):
        job_id = self.next_job_id
        job = (task_op, job_id, code, test)
        self.past_jobs.append(job)
        self.next_job_id += 1

        self.work_queue.put(job)

        return job_id

    def add_code_job(self):
        return self._add_job("code")

    def add_test_job(self):
        return self._add_job("test")

    def add_improve_code_job(self, code):
        return self._add_job("improve_code", code=code)

    def add_improve_test_job(self, test):
        return self._add_job("improve_test", test=test)

    def add_judge_pair_job(self, code, test):
        return self._add_job("judge_pair", code=code, test=test)

    def get_results(self, timeout: float = 1.0) -> List[Tuple[str, int, Any, Any]]:
        results = []
        try:
            results.append(self.result_queue.get(timeout=timeout))
            while not self.result_queue.empty():
                results.append(self.result_queue.get(timeout=timeout))
        except Empty:
            pass
        return results

    def active_workers(self):
        return self.workers.active_workers.value

    def approx_queue_depth(self):
        return self.work_queue.qsize()

    def terminate(self):
        self.workers.terminate()
