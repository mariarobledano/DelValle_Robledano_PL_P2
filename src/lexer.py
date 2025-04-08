import ply.lex as lex
from viper_tokens import tokens, reserved

class Lexer:
    tokens = tokens 
    def __init__(self):
        self.lexer = lex.lex(module=self)

    # Identificadores y palabras reservadas
    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = reserved.get(t.value, 'ID')
        return t

    # Números flotantes (incluye notación científica)
    def t_FLOAT_NUMBER(self, t):
        r'((\d+\.\d*)([eE][-+]?\d+)?|\d+[eE][-+]?\d+)'
        t.value = float(t.value)
        return t

    # Números enteros en decimal, binario, octal, hexadecimal
    def t_NUMBER(self, t):
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

    # Caracteres entre comillas simples
    def t_CHARACTER(self, t):
        r'\'[ -~]\''
        t.value = t.value[1]  # quitamos las comillas
        return t

    # Comentarios de una línea
    def t_COMMENT(self, t):
        r'\#.*'
        pass

    # Comentarios multilínea
    def t_MULTILINE_COMMENT(self, t):
        r"\'\'\'(.|\n)*?\'\'\'"
        t.lexer.lineno += t.value.count('\n')
        pass

    # Contador de líneas
    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # Manejo de errores
    def t_error(self, t):
        print(f"[Lexer Error] Carácter ilegal '{t.value[0]}' en línea {t.lineno}")
        t.lexer.skip(1)

    # Ignorar espacios y tabulaciones
    t_ignore = ' \t'

    # Operadores y símbolos
    t_ASSIGN    = r'='
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
    t_PLUS      = r'\+'
    t_MINUS     = r'-'
    t_TIMES     = r'\*'
    t_DIVIDE    = r'/'
    t_EQ        = r'=='
    t_GT        = r'>'
    t_GE        = r'>='
    t_LT        = r'<'
    t_LE        = r'<='
