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

Operators are applied to a stack of terms and return a stack of terms while functions modify the abstract syntax tree.

Operator example:  

>The **+** Constant is a Binary Operator which applies itself to the two top-most entries of the stack - summing them - and then places the resulting value on the top of the stack. During the Operater phase of Evaluation, Operators in the Abstract Syntax Tree is evaluated from each leaf node back up to the root so that all Operators 'down' the tree from the current Operator have already been Evaluated.

Function example:

>The **if** Constant is a Function which modifies its node of the Abstract Syntax Tree as follows:  

<code>(if true A B) -> A  
(if false A B) -> B  
</code>

>During the Function phase of Evaluation, Functions in the Abstract Syntax Tree are evaluated from the root down to each leaf node so that all Functions can modify the lower nodes prior to those nodes being Evaluated. 

## Built-in Functions and Operators

### concat
Operator - [quoted_text quoted_text | quoted_text]  
A space is inserted between the two quoted_text operands

### debug
Function - (debug true|false)
Enables debugging in the current environment.

### func
Function - (func search_node replace_node)
Adds a function to the dictionary. If search_node is found, variables in search_node are bound with the matched node. replace_node is updated with the variable bindings and inserted into the AST, replacing the matched node.

### if
Function - (if condition result_if_true result_if_false)

### op
Operator - (op quoted_string)
quoted_string is the new operator's symbol and a space-delimited list of operators. A new Operator is defined to be the provided symbol and execution is successive application of the identified list of operators.

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

