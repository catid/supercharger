def gcd_lcm(a, b):
    def euclidean_algorithm(x, y):
        while y != 0:
            x, y = y, x % y
        return x

    if a == 0 or b == 0:
        raise ValueError("Both input numbers must be non-zero")

    gcd = euclidean_algorithm(abs(a), abs(b))
    lcm = abs(a * b) // gcd

    return gcd, lcm

# Example usage
a = 56
b = 48
result_gcd, result_lcm = gcd_lcm(a, b)
print(f"The GCD of {a} and {b} is {result_gcd}")
print(f"The LCM of {a} and {b} is {result_lcm}")
