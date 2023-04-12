function recursiveRangeSum(start, end) {
    if (start === end) {
        return start;
    } else {
        return start + recursiveRangeSum(start, end - 1);
    }
}

const start = 1;
const end = 5;
const result = recursiveRangeSum(start, end);
console.log(`The sum of integers from ${start} to ${end} is ${result}`);
