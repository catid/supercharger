#include <iostream>

using namespace std;

// Function to sort an array of integers using the bubble sort algorithm
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

int main() {
    // Test the bubble_sort function with a sample array
    int arr[] = { 64, 34, 25, 12, 22, 11, 90 };
    int n = sizeof(arr) / sizeof(arr[0]);
    bubble_sort(arr, n);
    
    // Print the sorted array to the console
    cout << "Sorted array: ";
    for (int i = 0; i < n; i++) {
        cout << arr[i] << " ";
    }
    
    return 0;
}
