function reverseString(str: string): string {
    return str.split("").reverse().join("");
  }
  
  // Usage:
  console.log(reverseString("hello world")); // "dlrow olleh"
  
  function rectangleArea(width: number, height: number): number {
    return width * height;
  }
  
  // Usage:
  console.log(rectangleArea(4, 6)); // 24
  
  function capitalizeWords(str: string): string {
    const words = str.split(" ");
    const capitalizedWords = words.map(word => {
      const firstLetter = word.charAt(0);
      const restOfWord = word.slice(1);
      return firstLetter.toUpperCase() + restOfWord;
    });
    return capitalizedWords.join(" ");
  }
  
  // Usage:
  console.log(capitalizeWords("hello world")); // "Hello World"
  

function divide(a: number, b: number): number {
    return a / b;
  }