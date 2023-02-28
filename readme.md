# bsx

## Syntax

bsx is a programming language and also an interpreter for that language. bsx uses S Expressions, like Lisp. 

The EBNF grammar:

<code>quoted_string ::= '"' , { any_character } , '"';  
number ::= [ '-' ] , { digit } , [ '.' , { digit }];  
constant ::= lower_alpha , { alpha | digit };  
variable ::= upper_alpha , { alpha | digit };
symbol ::= non_alpha_digit , { non_alpha_digit };  
operand ::= quoted_string | number | constant | variable | s_exp;  
s_exp ::= '(' , function , { operand } , ')' | '(' , operator , { operand } , ')';  
</code>  

## Language Interpretation
The reference interpreter is written in Python and interprets bsx source code in text form as follows:

### Tokenization
Text of each 'line' of the bsx source code is tokenized into the following types:  

**Open Paren** - "("  
**Close Paren** - ")"  
**String** - any text surrounded by double-quotes. Double-quotes within the string must be preceded by a backslash.
**Number** - any sequence of characters beginning with "-" or a digit with zero or more digits optionally followed by "." and one or more digits.
**Constant** - any other sequence of characters but not including whitespace or parenthesis.

Currently, a 'line' is a single actual line (terminated by a Carriage Return/Line Feed per your OS) in the source file. Lines that end with " -" will also include the following line; a simple mechanism for line continuation. 

### Parsing
The token stream is parsed into an Abstract Syntax Tree (AST) where each Node contains a pointer to Data and a pointer to Next. The Data pointer may point to nother AST Node OR a Data node, but the Next pointer always points to another AST Node.

Data nodes contain the token type, symbol and floating point value (in the case of numbers).

### Transformation

Any defined Functions are applied to the AST, replacing the matching AST nodes with the function implementation nodes.  

An example is a function to perform double addition. In bsx, this function may be defined as:  
<code>
(func (++ A B C) (+ A (+ B C)) )
</code>  
...where constants beginning with upper case letters are considered variables. Any node matching "(++ A B C)" is unified with "(++ A B C)" and the resulting variable bindings for A, B, and C are applied to the node for "(+ A (+ B C))" which then replaces the matched node in the AST.

### Evaluation
The AST is evaluated beginning with the root to the leaf nodes and back to the root. Functions are implemented in the order in which they occur, allowing Functions to modify the AST prior to it being evaluated. Operators are implemented after each Leaf node has been reached so that as each Operator is evaluated, it is guaranteed that all operators 'down stream' have already been evaluated.

## Builtin Functions and Operators
Functions vs Operators  

### debug
Function - (debug sexp)  
Enables debugging in the current environment.  

### del
Operator - [string | ]  
Delets var (identified by string) from all environments  

### do
Function - (do sexp sexp ...)  
All included S Expressions are Evaluated with a shared Environment  

### eval
Operator [string | ]  
Eval evaluates a string containing bsx source code with the current environment. Eval does Tokenize, Parse, and Transform the source code into an AST but doesn't return the new AST nodes to the current tree. Instead it evaluates them separately, but with the current Environment. Compare with Parse.  

### func
Function - (func search_node replace_node)  
Adds a function to the dictionary. If search_node is found, variables in search_node are bound with the matched node. replace_node is updated with the variable bindings and inserted into the AST, replacing the matched node.  

### if
Function - (if condition result_if_true result_if_false)  

### include
Operator - [string | ]  
Includes file named string and evalulates that file as a bsx file with the current environment.  

### loop
Function - (loop start end step sexp sexp ...)  
Evaluates all contained S Expressions in order where an iteration counter starts with the value start, increments by step after each complete evaluation and stops when the counter reaches or exceeds stop.  

### nl
Operator - [ | ]  
Prints a new line.  

### op
Operator - [string ...]  
Defines a new Operator named string, when I figure out what that means.  

### parse
Function - (parse "bsx source code")  
Tokenizes, Parses, and Transforms the source code, then replaces its node in the AST with the new AST nodes that were generated. Parse doesn't explicitly Evalutate the new AST nodes, but they will be evalulated next. Compare with eval.  

### print
Operator - [any | ]  
Prints the entire stack to standard out.  

### #
Operator - [any | number]  
Converts a single data node to a number, even if that means the number 0 (because it wasn't a legitimate number).  

### +
Operator - [number number | number]  

### -
Operator - [number number | number]  

### *
Operator - [number number | number]  

### /
Operator - [number number | number]  

### =  
Operator - [number number | boolean]  
Note that boolean is simply a number, 0 or 1. 1 represents True and 0 False. When evaluating numbers as a boolean, any non-zero value will evaluate to True.  

### >=  
Operator - [number number | boolean]  

### <=  
Operator - [number number | boolean]  

### >  
Operator - [number number | boolean]  

### <  
Operator - [number number | boolean]  

### $_
Operator - [any any any ... | string]  
Concatenates all contained nodes as strings separated by spaces.  

### $
Operator - [any any any ... | string]  
Concatenates all contained nodes as strings but without any separating spaces.  
 
### !
Operator - [string any | ]  
Stores val (any) in variable (string).  

### @ 
Operator - [string | any]  
Gets value of a variable.  

### []
Operator - [string string | ]  
Creates an List variable (named with first string) with a single element (second string).  

### [!]
Operator - [string number string | ]  
Stores string in number index of List (named by first string).  

### [@]
Operator - [string number | string]  
Gets value of List at index number.  

### [-]
Operator - [string number | ]  
Deletes List entry for index number.  

### [#]
Operator - [string | number]  
Returns 0-based length of List.  

