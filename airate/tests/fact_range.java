public class MyMath {
    public static int recursiveFactorial(int n) {
        /*
         * Returns the factorial of n using recursion.
         */
        if (n == 0) {
            return 1;
        } else {
            return n * recursiveFactorial(n - 1);
        }
    }

    public static int recursiveRangeSum(int start, int end) {
        /*
         * Returns the sum of integers from start to end (inclusive) using recursion.
         */
        if (start == end) {
            return start;
        } else {
            return start + recursiveRangeSum(start + 1, end);
        }
    }
}

public class MyMath {
    public static int recursiveFactorial(int n) {
        /*
         * Returns the factorial of n using recursion.
         */
        if (n <= 0) {
            return 0;
        } else {
            return n * recursiveFactorial(n - 1);
        }
    }

    public static int recursiveRangeSum(int start, int end) {
        /*
         * Returns the sum of integers from start to end (inclusive) using recursion.
         */
        if (start == end) {
            return start;
        } else {
            return start + recursiveRangeSum(start, end);
        }
    }
}
