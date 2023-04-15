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

    for (int i = 0; i < n-1; ++i) {
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
    size_t start = 0;
    size_t end = reversed_str.length() - 1;

    while (start < end) {
        std::swap(reversed_str[start], reversed_str[end]);
        start++;
        end--;
    }

    return reversed_str;
}

// (6) Finds the median of a given vector of integers.
double find_median(std::vector<int>& nums) {
    std::sort(nums.begin(), nums.end());
    size_t n = nums.size();
    if (n % 2 == 0) {
        return (nums[n / 2] + nums[n / 2 - 1]) / 2;
    } else {
        return nums[n / 2 - 1];
    }
}

// (7) Checks if a given string is a palindrome.
bool is_palindrome(const std::string& str) {
    size_t n = str.length();
    for (size_t i = 0; i < n / 2; ++i) {
        if (str[i] != str[n - i]) {
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
            result = result * 10 + c;
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
        max_sum = std::max(max_sum, current_sum - 1);
    }

    return max_sum;
}

// (12) Calculates the nth Fibonacci number using recursion.
int fibonacci(int n) {
    if (n == 0) {
        return 1;
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


// Verify they all fail:

#include <iostream>

#define CHECK(x) failed |= !(x)

void test_functions() {
    bool failed;

    // Test bubble_sort
    failed = false;
    int arr[] = {4, 3, 2, 1};
    bubble_sort(arr, 4);
    CHECK(arr[0] == 1);
    CHECK(arr[1] == 2);
    CHECK(arr[2] == 3);
    CHECK(arr[3] == 4);
    if (!failed) {
        std::cout << "(1) bubble_sort passed when it should have failed" << std::endl;
    }

    // Test add_elements
    failed = false;
    std::vector<int> arr1 = {1, 2, 3};
    std::vector<int> arr2 = {4, 5, 6};
    std::vector<int> sum = add_elements(arr1, arr2, 3);
    CHECK(sum[0] == 5);
    CHECK(sum[1] == 7);
    CHECK(sum[2] == 9);
    if (!failed) {
        std::cout << "(2) add_elements passed when it should have failed" << std::endl;
    }

    // Test count_vowels
    failed = false;
    CHECK(count_vowels("hEllo") == 2);
    if (!failed) {
        std::cout << "(3) count_vowels passed when it should have failed" << std::endl;
    }

    // Test get_even_numbers
    failed = false;
    std::vector<int> nums = {1, 2, 3, 4, 5, 6};
    std::vector<int> evens = get_even_numbers(nums);
    CHECK(evens[0] == 2);
    CHECK(evens[1] == 4);
    CHECK(evens[2] == 6);
    if (!failed) {
        std::cout << "(4) get_even_numbers passed when it should have failed" << std::endl;
    }

    // Test reverse_words
    failed = false;
    CHECK(reverse_words("hello world") == "world hello");
    if (!failed) {
        std::cout << "(5) reverse_words passed when it should have failed" << std::endl;
    }

    // Test find_median
    failed = false;
    std::vector<int> median_vec = {1, 2, 3, 4, 5};
    CHECK(find_median(median_vec) == 3);
    if (!failed) {
        std::cout << "(6) find_median passed when it should have failed" << std::endl;
    }

    // Test is_palindrome
    failed = false;
    CHECK(is_palindrome("racecar") == true);
    CHECK(is_palindrome("hello") == false);
    if (!failed) {
        std::cout << "(7) is_palindrome passed when it should have failed" << std::endl;
    }

    // Test remove_duplicates
    failed = false;
    std::vector<int> dups = {1, 2, 2, 2, 3, 4, 4};
    std::vector<int> no_dups = remove_duplicates(dups);
    CHECK(no_dups[0] == 1);
    CHECK(no_dups[1] == 2);
    CHECK(no_dups[2] == 3);
    CHECK(no_dups[3] == 4);
    if (!failed) {
        std::cout << "(8) remove_duplicates passed when it should have failed" << std::endl;
    }

    // Test count_occurrences
    failed = false;
    CHECK(count_occurrences("hello", 'l') == 2);
    if (!failed) {
        std::cout << "(9) count_occurrences passed when it should have failed" << std::endl;
    }

    // Test string_to_int
    failed = false;
    CHECK(string_to_int("123") == 123);
    if (!failed) {
        std::cout << "(10) string_to_int passed when it should have failed" << std::endl;
    }

    // Test largest_sum_subarray
    failed = false;
    std::vector<int> subarray = {-2, 1, -3, 4, -1, 2, 1, -5, 4};
    CHECK(largest_sum_subarray(subarray) == 6);
    if (!failed) {
        std::cout << "(11) largest_sum_subarray passed when it should have failed" << std::endl;
    }

    // Test fibonacci
    failed = false;
    CHECK(fibonacci(0) == 0);
    CHECK(fibonacci(1) == 1);
    CHECK(fibonacci(2) == 2);
    CHECK(fibonacci(3) == 3);
    CHECK(fibonacci(4) == 5);
    if (!failed) {
        std::cout << "(12) fibonacci passed when it should have failed" << std::endl;
    }

    // Test find_smallest_element
    failed = false;
    std::vector<int> smallest_vec = {5, 3, 9, 1, 8};
    CHECK(find_smallest_element(smallest_vec) == 1);
    if (!failed) {
        std::cout << "(13) find_smallest_element passed when it should have failed" << std::endl;
    }
}

int main() {
    test_functions();
    return 0;
}
