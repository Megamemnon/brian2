# Brian

## Syntax

Brian uses S Expressions, like Lisp. 

The EBNF grammar:

<code>quoted_string ::= '"' , { any_character } , '"';  
number ::= [ '-' ] , { digit } , [ '.' , { digit }];  
constant ::= lower_alpha , { alpha | digit };  
variable ::= upper_alpha , { alpha | digit };
symbol ::= non_alpha_digit , { non_alpha_digit };  
operand ::= quoted_string | number | constant | variable | s_exp;  
s_exp ::= '(' , function , { operand } , ')' | '(' , operator , { operand } , ')';  
</code>  

### Functions vs Operators

Generally, Functions are applied in the order in which they occur while Operators are applied in reverse order. Both modify the abstract syntax tree, but Operators generally do this to 'return' a result while functions modify the AST for future processing by operators.

Function example:

>The **if** Constant is a Function which modifies its node of the Abstract Syntax Tree as described in the following psuedo code:  

<code>(if true A B) -> A  
(if false A B) -> B  
</code>

>During the Function phase of Evaluation, Functions in the Abstract Syntax Tree are evaluated from the root down to each leaf node so that all Functions can modify the lower nodes prior to those nodes being Evaluated. 

Operator example:  

>The **+** Constant is a Binary Operator which applies itself to two operands - summing them - and then replaces its own node in the AST with the resulting value. During the Operater phase of Evaluation, Operators in the AST are evaluated from each leaf node back up to the root so that when the current Operator is evaluated all Operators 'down' the tree from the current Operator have already been Evaluated.


## Built-in Functions and Operators

### concat
Operator - [string string | string]  
A space is inserted between the two string operands

### debug
Function - (debug sexp)
Enables debugging in the current environment.

### del
Operator - [var | ]
Delets var from all environments

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
Operator - [none | none]
Prints a new line.

### op
Operator - [constant ...]
Defines a new Operator named constant, when I figure out what that means.

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
Operator - [number number | result]

### -
Operator - [number number | result]

### *
Operator - [number number | result]

### /
Operator - [number number | result]

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
Operator - [var val | ]
Stores val in variable.

### @ 
Operator - [var | val]
Gets value of a variable.

### []
Operator - [var string | ]
Creates an Array variable with a single element (string).

### [!]
Operator - [var number string | ]
Stores string in number index of Array var.

### [@]
Operator - [var number | string]
Gets value of Array var at index number.

### [-]
Operator - [var number | ]
Deletes Array var entry for index number.

### [#]
Operator - [var | number]
Returns 0-based length of Array var.

