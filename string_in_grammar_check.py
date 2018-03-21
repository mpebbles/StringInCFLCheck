import argparse

def make_non_terminal(num):
    """For putting CGF into CNF.
       Produces new non-terminal.
    """ 
    return "_" + str(num)

def contains_unit_productions(list_of_keys, productions):
    """Returns True if unit production found in grammar.
    """
    for x in list_of_keys:
        if productions[x][0][0] in list_of_keys:
            return True
    return False

# returns tuple 
# [0] is replaceable rule found
# [1] key containing rule, [2] index in key
def replaceable_rule_exists(cnf):
    """" Returns tuple. 
         [0] is replaceable rule found.
         [1] key containing rule; [2] index in key.
    """
    for k,v in cnf.items():
        for i in range(len(v)):
            if len(v[i]) > 2 or \
                len(v[i]) == 2 and (v[i][0] not in cnf or v[i][1] not in cnf):
                return (True, k, i)
    return (False, 'fake_key', 0)

# gets grammar from file, puts into CNF
def get_cnf(cfg_str):
    """ Gets grammar from file and puts it into CNF.
    """
    # get grammar from file
    cfg_str_no_comments = ""
    first_rule = True
    for l in cfg_str.splitlines():
        if len(l) > 0 and l[0] != "#":
            cfg_str_no_comments += l
            if first_rule:
                if '->' in l:
                    temp = l.split('->')
                    start = l[0].strip()
                    first_rule = False
    production_sections = [a.strip() for a in cfg_str_no_comments.split(';') if len(a) > 0]
    productions = {}
    for p in production_sections:
        # rule[0] non-terminal, rule[1] terms/non-terms
        rule = [a.strip() for a in p.split('->')]
        b = [a.strip() for a in rule[1].split('|')]
        c = []
        for x in b:
            c.append([a for a in x.split('\\') if len(a) > 0])
        productions[rule[0]] = c
    productions_without_e = {}
    vars_going_to_e = []
    # remove empty
    for k, v in productions.items():
        productions_without_e[k] = []
        for x in v:
            if 'empty' in x:
                vars_going_to_e.append(k)
                if len(v) == 1:
                    del productions_without_e[k]
            else:
                productions_without_e[k].append(x)
    productions_without_e2 = {}
    # add rule with empty removed 
    for k, v in productions_without_e.items():
        productions_without_e2[k] = []
        for x in v:
            productions_without_e2[k].append(x)
            for sym in x:
                if sym in vars_going_to_e:
                    to_append = []
                    for s in x:
                        if s != sym:
                            to_append.append(s)
                    if len(to_append) > 0:
                        productions_without_e2[k].append(to_append)
    # remove unit productions
    len_one_rules = [k for k,v in productions_without_e2.items() if len(v) == 1]
    while(contains_unit_productions(len_one_rules, productions_without_e2)):
        break_flag = False
        for i in range(len(len_one_rules)):
            for j in range(len(len_one_rules)):
                if i != j and not break_flag:
                    if productions_without_e2[len_one_rules[i]][0][0] == len_one_rules[j]:
                        productions_without_e2[len_one_rules[i]] = \
                        productions_without_e2[len_one_rules[j]]
                        del productions_without_e2[len_one_rules[j]]
                        break_flag = True 
        len_one_rules = [k for k,v in productions_without_e2.items() if len(v) == 1]
    # make productions have 2 non terminals or 1 terminal only
    cnf = productions_without_e2
    num = 0
    # (bool, key, index)
    temp = replaceable_rule_exists(cnf)
    while(temp[0]):
        for i in range(len(cnf[temp[1]][temp[2]])):
            if cnf[temp[1]][temp[2]][i] not in cnf:
                # search for terminal
                key = None
                done = False
                for k,v in cnf.items():
                    if done:
                        break
                    for x in v:
                        if len(v) == 1 and len(x) == 1:
                            if cnf[temp[1]][temp[2]][i] in x:
                                key = k
                                done = True
                                break
                if key is not None:
                    cnf[temp[1]][temp[2]][i] = key
                else:
                    num += 1
                    new_sym = make_non_terminal(num)
                    sym = cnf[temp[1]][temp[2]][i]
                    cnf[temp[1]][temp[2]][i] = new_sym
                    cnf[new_sym] = [[sym]]
                    break
        if len(cnf[temp[1]][temp[2]]) > 2:
            num+= 1
            new_sym = make_non_terminal(num)
            cnf[new_sym] = [cnf[temp[1]][temp[2]][1:]]
            cnf[temp[1]][temp[2]] = cnf[temp[1]][temp[2]][0:1] + [new_sym]
        temp = replaceable_rule_exists(cnf)
    return (start, cnf)
 
def reverse_grammar(gram):
    """ Carefully reverses keys/values in dictionary.
    """
    ret = {}
    for k,v in gram.items():
        new_key = ''
        for x in v:
            for sym in x:
                new_key += sym
            if new_key not in ret:    
                ret[new_key] = [k]
            else:
                if k not in ret[new_key]:
                    ret[new_key].append(k)
            new_key = ''
    return ret

# if A = [a, b, c], B = [d]
# returns [ad,ae,bd,be,cd,ce]
def get_options(A, B):
    """
    If A = [a, b, c], B = [d],
    def returns [ad,ae,bd,be,cd,ce].
    """
    ret = []
    for a in A:
        for b in B:
            c = a + b
            if c not in ret:
                ret.append(c)
    return ret

def print_matrix(matrix):
    """ For debugging.
    """
    for row in matrix:
        print(row)
        print("\n")

def run_cky(s, reverse_grammar, start):
    # initialize half matrix
    matrix = []
    for i in range(len(s)):
        matrix.append([])
        for _ in range(i + 1):
            matrix[-1].append([])
    # diag 
    for a in range(len(s)):
        # rows
        for i in range(a,len(s)):
            j = i - a
            if i == j:
                if s[i] in reverse_grammar:
                    matrix[i][j] += reverse_grammar[s[i]]
            else:
                # loop through options
                for k in range(a):
                    ops = get_options(matrix[j + k][j], matrix[i][j+k+1])
                    for o in ops:
                        if o in reverse_grammar:
                            matrix[i][j] += reverse_grammar[o]
    # is string in CFL produced by supplied CFG?
    if start in matrix[len(s) - 1][0]:
        print("Yes")
    else:
        print("No")
 
def main(args):
    #print(args.strings)
    with open(args.grammar_file) as gram_file:
        cfg = gram_file.read()
        start, cnf = get_cnf(cfg)
        # makes algorithm easier to implement
        reverse_cnf = reverse_grammar(cnf)
    for s in args.strings:
        run_cky(s, reverse_cnf, start)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check if a string (or list of strings) is in a grammar.')
    parser.add_argument('strings', metavar='S', type=str, nargs='+',
                         help='input string(s)') 
    parser.add_argument('grammar_file', metavar='grammar_file', type=str, help="Input file containing context free grammar")
    main(parser.parse_args())
