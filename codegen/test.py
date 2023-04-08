import math

def add(a, b):
    return a + b

def subtract(a, b):
 return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    return a / b

def dostuff():
    x = 5
    y = 2

    print(f"{x} + {y} = {add(x, y)}")
    print(f"{x} - {y} = {subtract(x, y)}")
    print(f"{x} * {y} = {multiply(x, y)}")
    print(f"{x} / {y} = {divide(x, y)}")

    # Calculate the area of a circle
    radius = 3
    area = math.pi * (radius ** 2)
    print(f"The area of a circle with radius {radius} is {area:.2f}"):

    # Calculate the square root of a number
    number = 49
    square_root = math.sqrt(number)
    print(f"The square root of {number} is {square_root}")

    # Find the maximum value in a list
    numbers = [34, 56, 12, 89, 23, 7, 91]
    max_number = max(numbers)
    print(f"The maximum value in the list is {max_number}")

    # Check if a number is prime:
        num = 7
    is_prime = True
    for i in range(2, num):
        if num % i == 0:
                is_prime = False
            break

    if is_prime:
        print(f"{num} is a prime number")
    else:
        print(f"{num} is not a prime number")

def main():
    dostuff()

if __name__ == "__main__":
    main()

main()  # This is a comment