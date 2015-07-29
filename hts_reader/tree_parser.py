
import ply.yacc as yacc

from tree_lex import tokens
from tree_structure import *
questions = {}

def p_macros(p):
    '''
    macros : macro macros
           | macro
    '''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_macro(p):
    '''
    macro : START_TREE_CMP tree
          | START_TREE_DUR tree
          | NAME question
    '''
    if not p[1] == "QS":
        p[2].name = p[1]
    p[0] = p[2]
def p_tree(p):
    '''
    tree : BEGIN_PATTERN nodes END_PATTERN
    '''
    p[0] = Tree(p[2])

def p_nodes(p):
    '''
    nodes : node nodes
          | node
    '''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_node(p):
    '''
    node : INT QUESTION INT INT
         | INT QUESTION GAUSS_NAME INT
         | INT QUESTION INT GAUSS_NAME
         | INT QUESTION GAUSS_NAME GAUSS_NAME
    '''
    p[0] = Node(p[1],p[2],p[3],p[4])

def p_question(p):
    '''
    question : QUESTION BEGIN_PATTERN patterns END_PATTERN
    '''
    p[0] = Question(p[1],p[3])
def p_patterns(p):
    '''
    patterns : PATTERN
             | PATTERN DELIM patterns
    '''
    if len(p) == 4:
        p[0] = [p[1].replace("\"","")] + p[3]
    else:
        p[0] = [p[1].replace("\"","")]
    pass


def p_error(p):
    print 'Syntax error at "%s" (line %s)' % (p.value, p.lineno)
yacc.yacc(debug=0, write_tables=0)
#result = parser.parse(open("cmp/mgc.inf.untied").read())


#result.display()
#for q in result:
#    q.display()
