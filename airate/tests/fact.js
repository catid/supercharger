function recursiveFactorial(n) {
    if (n === 0) {
        return 1;
    } else {
        return n * recursiveFactorial(n - 1);
    }
}

const inputNumber = 5;
const result = recursiveFactorial(inputNumber);
console.log(`The factorial of ${inputNumber} is ${result}`);
