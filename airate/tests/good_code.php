function factorial($n) {
  if ($n == 0) {
    return 1;
  } else {
    return $n * factorial($n - 1);
  }
}

// Usage:
echo factorial(5); // 120

function reverseString($str) {
  return strrev($str);
}

// Usage:
echo reverseString("hello world"); // "dlrow olleh"

function isPalindrome($str) {
  $str = strtolower($str);
  $str = preg_replace("/[^A-Za-z0-9]/", '', $str);
  return $str == strrev($str);
}

// Usage:
echo isPalindrome("A man, a plan, a canal, Panama!"); // true
echo isPalindrome("hello world"); // false
