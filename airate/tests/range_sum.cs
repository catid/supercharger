using System;

class RangeSum
{
    public static int RecursiveRangeSum(int start, int end)
    {
        if (start == end)
        {
            return start;
        }
        else
        {
            return start + RecursiveRangeSum(start, end - 1);
        }
    }

    static void Main(string[] args)
    {
        int start = 1;
        int end = 5;
        int result = RecursiveRangeSum(start, end);
        Console.WriteLine($"The sum of integers from {start} to {end} is {result}");
    }
}
