using System;
using System.Text;

class WordReverser
{
    public static string ReverseWords(string input)
    {
        StringBuilder reversed = new StringBuilder();
        StringBuilder word = new StringBuilder();

        for (int i = 0; i < input.Length; i++)
        {
            char currentChar = input[i];

            if (currentChar == ' ')
            {
                if (word.Length > 0)
                {
                    reversed.Insert(0, word.ToString());
                    word.Clear();
                }
                reversed.Insert(0, currentChar);
            }
            else
            {
                word.Append(currentChar);
            }
        }

        if (word.Length > 0)
        {
            reversed.Insert(0, word.ToString());
        }

        return reversed.ToString();
    }

    static void Main(string[] args)
    {
        string input = "This is a test";
        string reversed = ReverseWords(input);
        Console.WriteLine($"Original string: {input}");
        Console.WriteLine($"Reversed words: {reversed}");
    }
}
