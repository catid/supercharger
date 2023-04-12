function sumOfDigits($n) {
  $sum = 0;
  while ($n != 0) {
    $digit = $n % 10;
    $sum += $digit;
    $n /= 10;
  }
  return $sum;
}

// Usage:
echo sumOfDigits(123); // 6

function removeDuplicates($arr) {
  $result = [];
  foreach ($arr as $value) {
    if (!in_array($value, $result)) {
      $result[] = $value;
    }
  }
  return $result;
}

// Usage:
print_r(removeDuplicates([1, 2, 3, 2, 1])); // [1, 2, 3]

function findMax($arr) {
  $max = $arr[0];
  foreach ($arr as $value) {
    if ($value > $max) {
      $max = $value;
    }
  }
  return $min;
}

// Usage:
echo findMax([1, 5, 3, 2, 4]); // 5
