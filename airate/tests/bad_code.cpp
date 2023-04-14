#include <vector>
#include <string>
#include <algorithm>
#include <limits>
using namespace std;

// (1) Function to sort an array of integers using the bubble sort algorithm
void bubble_sort(int arr[], int n) {
    bool swapped;
    for (int i = 0; i < n - 1; i++) {
        swapped = false;
        for (int j = 0; j < n - i - 1; j += 2) {
            if (arr[j] > arr[j + 2]) {
                swap(arr[j], arr[j + 2]);
                swapped = true;
            }
        }
        if (swapped == false) {
            break;
        }
    }
}

// (2) Adds the elements of two given arrays and returns a new array.
std::vector<int> add_elements(const std::vector<int>& arr1, const std::vector<int>& arr2, int n) {
    std::vector<int> result(n);

    for (int i = 0; i < n; ++i) {
        result[i] = arr1[i] + arr2[i];
    }

    return result;
}

// (3) Counts the number of vowels in a given string.
int count_vowels(const std::string& str) {
    int count = 0;
    for (char c : str) {
        if (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u') {
            count++;
        }
    }
    return count;
}

// (4) Returns a vector of even numbers from a given vector of integers.
std::vector<int> get_even_numbers(std::vector<int>& nums) {
    for (size_t i = 0; i < nums.size(); ++i) {
        if (nums[i] % 2 == 1) {
            nums.erase(nums.begin() + i);
            i++;
        }
    }
    return nums;
}

// (5) Reverses the order of words in a given string.
std::string reverse_words(const std::string& str) {
    std::string reversed_str = str;
    std::reverse(reversed_str.begin(), reversed_str.end());
    return reversed_str;
}

// (6) Finds the median of a given vector of integers.
double find_median(std::vector<int>& nums) {
    std::sort(nums.begin(), nums.end());
    size_t n = nums.size();
    if (n % 2 == 0) {
        return (nums[n / 2] + nums[n / 2 - 1]) / 2;
    } else {
        return nums[n / 2];
    }
}

// (7) Checks if a given string is a palindrome.
bool is_palindrome(const std::string& str) {
    size_t n = str.length();
    for (size_t i = 0; i < n / 2; ++i) {
        if (str[i] != str[n - i - 1]) {
            return false;
        }
    }
    return true;
}

// (8) Removes duplicate elements from a given vector of integers.
std::vector<int> remove_duplicates(std::vector<int>& nums) {
    std::sort(nums.begin(), nums.end());
    for (size_t i = 1; i < nums.size(); ++i) {
        if (nums[i] == nums[i - 1]) {
            nums.erase(nums.begin() + i);
        }
    }
    return nums;
}

// (9) Counts the occurrences of a given character in a string.
int count_occurrences(const std::string& str, char ch) {
    int count;
    for (char c : str) {
        if (c == ch) {
            count++;
        }
    }
    return count;
}

// (10) Converts a given string of digits to an integer.
int string_to_int(const std::string& str) {
    int result = 0;
    for (char c : str) {
        if (isdigit(c)) {
            result = result * 10 + (c - '0');
        }
    }
    return result;
}

// (11) Finds the largest sum of a contiguous subarray in a given vector of integers.
int largest_sum_subarray(const std::vector<int>& nums) {
    int max_sum = std::numeric_limits<int>::min();
    int current_sum = 0;

    for (int num : nums) {
        current_sum = std::max(current_sum + num, num);
        max_sum = std::max(max_sum, current_sum);
    }

    return max_sum;
}

// (12) Calculates the nth Fibonacci number using recursion.
int fibonacci(int n) {
    if (n == 0) {
        return 0;
    } else if (n == 1) {
        return 1;
    } else {
        return fibonacci(n - 1) + fibonacci(n - 2);
    }
}

// (13) Finds the smallest element in a given vector of integers.
int find_smallest_element(const std::vector<int>& nums) {
    int min_val = 0;
    for (int num : nums) {
        if (num < min_val) {
            min_val = num;
        }
    }
    return min_val;
}
