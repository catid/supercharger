# A function that tests if a number is prime.
def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(n)) + 1):
        if n % i == 0:
            return True