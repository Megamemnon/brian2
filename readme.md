# Brian

## Syntax

<code>quoted_string ::= '"' , { any_character } , '"';  
number ::= [ '-' ] , { digit } , [ '.' , { digit }];  
constant ::= lower_alpha , { alpha | digit };  
variable ::= upper_alpha , { alpha | digit };  
sexp ::= '(' , constant , { operand } , ')';  
</code>  

### Functions vs Operators

Operators are applied to a stack of terms and return a stack of terms while functions modify the abstract syntax tree.

For example:  

>The <b>+</b> Constant is a Binary Operator which applies itself to the two top-most entries of the stack - summing them - and then places the resulting value on the top of the stack. During the Operater phase of Evaluation, Operators in the Abstract Syntax Tree is evaluated from each leaf node back up to the root so that all Operators 'down' the tree from the current Operator have already been Evaluated.

>The <b>if</b> Constant is a Function which modifies its node of the Abstract Syntax Tree as follows:  
<code>(if true A B) -> A  
(if false A B) -> B  
</code>  
>During the Function phase of Evaluation, Functions in the Abstract Syntax Tree are evaluated from the root down to each leaf node so that all Functions can modify the lower nodes prior to those nodes being Evaluated. 