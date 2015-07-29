import ply.lex as lex

tokens = (
    'NAME',
    'QUESTION',
    'BEGIN_PATTERN',
    'END_PATTERN',
    'PATTERN',
    'DELIM',
    'START_TREE_CMP',
    'START_TREE_DUR',
    'GAUSS_NAME',
    'INT',
)

t_NAME = r'QS'
t_QUESTION = r'[a-zA-Z0-9]+[-_][\S]+'
t_BEGIN_PATTERN = r'\{'
t_END_PATTERN = r'\}'
t_PATTERN = r'"[^, ]+'
t_DELIM = r','
t_START_TREE_CMP = r'[^\. \n]*\.stream.*'
t_START_TREE_DUR = r'\{\*\}\[\d+\]\s*'
t_GAUSS_NAME = r'"[a-zA-Z0-9_]+"'

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

def t_INT(t):
    r'[-+]*\d+'
    t.value = int(t.value)
    return t

def t_error(t):
    print "Illegal character '%s' line %s " % (t.value[0],t.lineno)
    t.lexer.skip(1)

lexer = lex.lex()

#lexer.input("""
#QS Utt_Emp=0 { "*/T:0" }

#{*}[2].stream[1]
#{
#-28 L-Phone_Atojita_Boin -52 -61
#}
#""")

#for tok in lexer:
#    print tok
