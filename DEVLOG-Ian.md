# Dev Log:

This document must be updated daily every time you finish a work session.

## Ian Buchanan

### 2024-05-21 Start defining variables in tokenization 
Began defining variables and their valid aliases such as booleans and the null type in the tokenization function. 

### 2024-05-22 Word on defining variables functionality 
Worked on progress for 'put' option for defining variables while using the helper function to grab quote indexes. 

### 2024-05-23 Finish 'put' for variable defining, get_word() 
Finished testing and debuggin the 'put' keyword code and made small changes to get_word() functionality for usage.

### 2024-5-27 FLOW CONTROL Progress 
1-Created the skeleton in generate_trees() of flow control including if statements, loops, and end statements. 
Began to research and create parseConditional() to return booleans from conditionals. 

2- Started working on parseConditional() function by tokenizing the rest of a statement and appending values of T/F to them with binary operators. 

### 2024-5-28 Parse Conditional Progress for Flow Control 
Wrote most of conditional statements alternatives to append to token list. Researched how to parse token array of conditional information into final interpretation. 

### 2024-5-29 Tokenize condition finished 
Finished conditionalToArray() function to tokenize conditional statements with final code and debugged and tested function. 

### 2024-5-30 ABSENT 

### 2024-6-2 Worked on expression evaluation from tokenized arrays 
1- Began and almost completed writing parseConditionalArray() function to evaluate boolean expressions inside of 'if'/'while' statements. Function uses context dictionary 
as input in order to refer to previously defined variables and takes an array of tokens taken from the conditionalToArray() function. 

2- Completed conditionalToArray() function to evaluate expressions by implementing decisions based on variable and queued actions tokens (expression evaluated strictly from left to right). 
Also implemented working around type coercion in equality and comparison cases. 
Ran a couple test cases to debug both expression evaluation functions. 