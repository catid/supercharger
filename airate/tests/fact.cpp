#include <iostream>

using namespace std;

// Function to calculate the factorial of a positive integer using recursion
int factorial(int n) {
    // Base case: If n is 0 or 1, the factorial is 1
    if (n == 0 || n == 1) {
        return 1;
    }
    // Recursive case: Calculate the factorial of (n-1) and multiply it by n
    else {
        return n * factorial(n-1);
    }
}

int main() {
    // Call the factorial function with a test input
    int n = 5;
    int result = factorial(n);
    
    // Print the result to the console
    cout << "The factorial of " << n << " is: " << result << endl;
    
    return 0;
}