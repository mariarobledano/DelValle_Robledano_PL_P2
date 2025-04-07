import ply.lex as lex
from src.viper_tokens import tokens, reserved


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    # Comprobamos si es una palabra reservada
    t.type = reserved.get(t.value, 'ID')  
    return t

def t_error(t):
    print(f"[Lexer Error] Carácter ilegal '{t.value[0]}' en línea {t.lineno}")
    t.lexer.skip(1)

def t_FLOAT_NUMBER(t):
    r'((\d+\.\d*)([eE][-+]?\d+)?|\d+[eE][-+]?\d+)'
    t.value = float(t.value)
    return t
    
def t_NUMBER(t):
    r'0b[01]+|0o[0-7]+|0x[A-F0-9]+|[0-9]+'
    if t.value.startswith("0b"):
        t.value = int(t.value, 2)
    elif t.value.startswith("0o"):
        t.value = int(t.value, 8)
    elif t.value.startswith("0x"):
        t.value = int(t.value, 16)
    else:
        t.value = int(t.value)
    return t

def t_CHARACTER(t):
    r'\'[ -~]\''
    t.value = t.value[1]  # eliminar comillas
    return t

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_COMMENT(t):
    r'\#.*'
    pass  

def t_MULTILINE_COMMENT(t):
    r"\'\'\'(.|\n)*?\'\'\'"
    t.lexer.lineno += t.value.count('\n')
    pass  


t_ignore = ' \t'
t_ASSIGN = r'='

t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LBRACKET  = r'\['
t_RBRACKET  = r'\]'
t_LBRACE    = r'\{'
t_RBRACE    = r'\}'

t_COLON     = r':'
t_SEMICOLON = r';'
t_COMMA     = r','
t_DOT       = r'\.'

t_PLUS   = r'\+'
t_MINUS  = r'-'
t_TIMES  = r'\*'
t_DIVIDE = r'/'

t_EQ = r'=='
t_GT = r'>'
t_GE = r'>='
t_LT = r'<'
t_LE = r'<='

lexer = lex.lex()

