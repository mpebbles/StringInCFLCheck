# StringInCFLCheck

usage: string_in_grammar_check.py [-h] S [S ...] grammar_file
string_in_grammar_check.py: error: the following arguments are required: S, grammar_file

Program takes string(s) and file containing CFG as input. The input file does not need to be in
Compsky normal form. Program puts input grammar into CNF and uses the CKY algorithm. Prints yes/no 
(answering if string is in CFL produced by given CFG) for each input string. 

For examples of how to format CFG file, see .txt files. 
