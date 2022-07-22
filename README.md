# TreeComparison

A lightweight tool for comparing AST for Automated Code Editing.
The two functions implemented in this code are 

1. [`compute_tree_distance`](compute_distance.py#L113) :  It computes the tree edit distance between buggy code and fixed code ignoring any identifiers or literals. More precisely,  it computes the structural difference between buggy code and fixed code. 
2. [`number_of_new_identifiers_in_fixed_code`](compute_distance.py#L113) : It counts the number of new identifiers or literals in the fixed code those were not present in the buggy code.

## To setup
Run the `setup.sh` to setup the environment.
It will create a file `parser/languages.so` which is essential for both the functions implemented here. 
 

## For a demo
Run ```python compute_distance.py``` showing [how to use](compute_distance.py#L134-L164) the abovementioned functions. 
