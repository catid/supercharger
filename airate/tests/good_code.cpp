#include <vector>
#include <string>
#include <algorithm>
#include <cmath>
using namespace std;

// (1) Function to calculate the factorial of a positive integer using recursion
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

// (2) Merges two sorted input vectors into a single sorted output vector.
std::vector<int> merge_sorted_arrays(const std::vector<int>& arr1, const std::vector<int>& arr2) {
    std::vector<int> result;
    size_t i = 0, j = 0;

    while (i < arr1.size() && j < arr2.size()) {
        if (arr1[i] < arr2[j]) {
            result.push_back(arr1[i]);
            i++;
        } else {
            result.push_back(arr2[j]);
            j++;
        }
    }

    while (i < arr1.size()) {
        result.push_back(arr1[i]);
        i++;
    }

    while (j < arr2.size()) {
        result.push_back(arr2[j]);
        j++;
    }

    return result;
}

// (3) Counts the number of words in a given string, where words are separated by spaces.
int count_words(const std::string& str) {
    int word_count = 0;
    bool in_word = false;

    for (char c : str) {
        if (isspace(c)) {
            in_word = false;
        } else {
            if (!in_word) {
                word_count++;
                in_word = true;
            }
        }
    }

    return word_count;
}

// (4) Performs binary search on a sorted input vector for a given target value.
int binary_search(const std::vector<int>& nums, int target) {
    int left = 0;
    int right = nums.size() - 1;

    while (left <= right) {
        int mid = left + (right - left) / 2;

        if (nums[mid] == target) {
            return mid;
        } else if (nums[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }

    return -1;
}

// (5) Checks if a given positive integer is a prime number.
bool is_prime(int n) {
    if (n <= 1) {
        return false;
    }

    for (int i = 2; i <= std::sqrt(n); ++i) {
        if (n % i == 0) {
            return false;
        }
    }

    return true;
}

// (6) Calculates the greatest common divisor (GCD) of two non-negative integers using the Euclidean algorithm.
int gcd(int a, int b) {
    while (b != 0) {
        int temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}

// (7) Converts all characters in a given string to lowercase.
std::string string_to_lower(const std::string& str) {
    std::string result = str;
    for (size_t i = 0; i < result.size(); ++i) {
        result[i] = std::tolower(result[i]);
    }
    return result;
}

// (8) Rotates a given vector of integers to the right by 'k' steps.
std::vector<int> rotate_vector(const std::vector<int>& nums, int k) {
    int n = nums.size();
    k %= n;
    std::vector<int> result(n);

    for (int i = 0; i < n; ++i) {
        result[(i + k) % n] = nums[i];
    }

    return result;
}

// (9) Finds the length of the longest increasing subsequence in a given vector of integers.
int longest_increasing_subsequence(const std::vector<int>& nums) {
    std::vector<int> lis(nums.size(), 1);

    for (size_t i = 1; i < nums.size(); ++i) {
        for (size_t j = 0; j < i; ++j) {
            if (nums[i] > nums[j]) {
                lis[i] = std::max(lis[i], lis[j] + 1);
            }
        }
    }

    return *std::max_element(lis.begin(), lis.end());
}

// (10a) Partition function for the Quick Sort algorithm.
int partition(std::vector<int>& nums, int low, int high) {
    int pivot = nums[high];
    int i = low - 1;

    for (int j = low; j < high; ++j) {
        if (nums[j] < pivot) {
            i++;
            std::swap(nums[i], nums[j]);
        }
    }

    std::swap(nums[i + 1], nums[high]);
    return i + 1;
}

// (10b) Sorts a given vector of integers using the Quick Sort algorithm.
void quicksort(std::vector<int>& nums, int low, int high) {
    if (low < high) {
        int pivot = partition(nums, low, high);
        quicksort(nums, low, pivot - 1);
        quicksort(nums, pivot + 1, high);
    }
}

// (11) Encrypts a given string using the Caesar Cipher algorithm with a specified shift value.
std::string caesar_cipher(const std::string& str, int shift) {
    std::string encrypted_str;

    for (char c : str) {
        if (std::isalpha(c)) {
            char base = std::islower(c) ? 'a' : 'A';
            c = static_cast<char>((c - base + shift) % 26 + base);
        }
        encrypted_str.push_back(c);
    }

    return encrypted_str;
}

// (12) Sorts a given vector of integers using the Bubble Sort algorithm.
void bubble_sort(std::vector<int>& nums) {
    bool swapped;

    for (size_t i = 0; i < nums.size() - 1; ++i) {
        swapped = false;

        for (size_t j = 0; j < nums.size() - i - 1; ++j) {
            if (nums[j] > nums[j + 1]) {
                std::swap(nums[j], nums[j + 1]);
                swapped = true;
            }
        }

        if (!swapped) {
            break;
        }
    }
}

// (13) Calculates the power of a given base raised to a given exponent using a recursive approach.
double power(double base, int exponent) {
    if (exponent == 0) {
        return 1;
    }

    double half_power = power(base, exponent / 2);
    if (exponent % 2 == 0) {
        return half_power * half_power;
    } else {
        return (exponent > 0 ? base : 1 / base) * half_power * half_power;
    }
}

// (14) Checks if two given strings are anagrams.
bool is_anagram(const std::string& str1, const std::string& str2) {
    if (str1.size() != str2.size()) {
        return false;
    }

    std::string sorted_str1 = str1;
    std::string sorted_str2 = str2;

    std::sort(sorted_str1.begin(), sorted_str1.end());
    std::sort(sorted_str2.begin(), sorted_str2.end());

    return sorted_str1 == sorted_str2;
}

// (15) Finds all prime numbers up to a given limit using the Sieve of Eratosthenes algorithm.
std::vector<int> sieve_of_eratosthenes(int limit) {
    std::vector<bool> is_prime(limit + 1, true);
    is_prime[0] = is_prime[1] = false;

    for (int i = 2; i * i <= limit; ++i) {
        if (is_prime[i]) {
            for (int j = i * i; j <= limit; j += i) {
                is_prime[j] = false;
            }
        }
    }

    std::vector<int> primes;
    for (int i = 2; i <= limit; ++i) {
        if (is_prime[i]) {
            primes.push_back(i);
        }
    }

    return primes;
}
