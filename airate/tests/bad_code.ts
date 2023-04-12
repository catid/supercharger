
  
  // Usage:
  console.log(divide(10, "5")); // Should be 2, but throws a type error
  

function fibonacci(n: number): number {
    if (n === 0) {
      return 1;
    } else if (n === 1) {
      return 1;
    } else {
      return fibonacci(n - 1) + fibonacci(n - 2);
    }
  }
  
  // Usage:
  console.log(fibonacci(5)); // Should be 5, but returns 8
  

function findMax(nums: number[]): number {
    let max = null;
    for (let i = 0; i < nums.length; i++) {
      if (nums[i] > max) {
        max = nums[i];
      }
    }
    return max;
  }
  
  // Usage:
  console.log(findMax([1, 2, 3, 4, 5])); // Should throw a runtime error, but returns null
  