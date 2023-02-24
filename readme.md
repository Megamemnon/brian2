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

>The **if** Constant is a Function which modifies its node of the Abstract Syntax Tree as follows:  

<code>(if true A B) -> A  
(if false A B) -> B  
</code>

>During the Function phase of Evaluation, Functions in the Abstract Syntax Tree are evaluated from the root down to each leaf node so that all Functions can modify the lower nodes prior to those nodes being Evaluated. 

Operator example:  

>The **+** Constant is a Binary Operator which applies itself to two operands - summing them - and then replaces itself with the resulting value. During the Operater phase of Evaluation, Operators in the Abstract Syntax Tree is evaluated from each leaf node back up to the root so that all Operators 'down' the tree from the current Operator have already been Evaluated.


## Built-in Functions and Operators

### concat
Operator - [string string | string]  
A space is inserted between the two string operands

### debug
Function - (debug sexp)
Enables debugging in the current environment.

### func
Function - (func search_node replace_node)
Adds a function to the dictionary. If search_node is found, variables in search_node are bound with the matched node. replace_node is updated with the variable bindings and inserted into the AST, replacing the matched node.

### if
Function - (if condition result_if_true result_if_false)

### print
Operator - [any | ]
Prints the entire stack to standard out.

### +
Operator - [number number | result]

### -
Operator - [number number | result]

### *
Operator - [number number | result]

### /
Operator - [number number | result]

### ==  
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