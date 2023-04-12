def recursive_factorial(n):
    if n == 0:
        return 1
    else:
        return n * recursive_factorial(n)

# Example usage
n = 5
result = recursive_factorial(n)
print(f"The factorial of {n} is {result}")
