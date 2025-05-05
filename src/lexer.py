import ply.lex as lex
from viper_tokens import tokens, reserved

class Lexer:
    tokens = tokens 
    
    def __init__(self):
        self.lexer = lex.lex(module=self)
    
    # Comentarios multilínea (cerrados y no cerrados)
    def t_MULTILINE_COMMENT(self, t):
        r"'''(.|\n)*?'''"
        if not t.value.endswith("'''"):
            print(f"[Lexer Error] Comentario multilínea no cerrado en línea {t.lineno}")
            t.lexer.skip(len(t.value))
        else:
            t.lexer.lineno += t.value.count('\n')
            return None

    # Identificadores y palabras reservadas
    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = reserved.get(t.value, 'ID')
        if t.type == 'TRUE':
            t.value = True
        elif t.type == 'FALSE':
            t.value = False
        return t

    # Números flotantes (incluye notación científica)
    def t_FLOAT_NUMBER(self, t):
        r'((\d+\.\d*)([eE][-+]?\d+)?|\d+[eE][-+]?\d+)'
        try:
            t.value = float(t.value)
            return t
        except ValueError:
            print(f"[Lexer Error] Número flotante mal formado '{t.value}' en línea {t.lineno}")

    # Números enteros en decimal, binario, octal, hexadecimal
    def t_NUMBER(self, t):
        r'0b[01]+|0o[0-7]+|0x[A-F0-9]+|0|[1-9][0-9]*'
        try:
            if t.value.startswith("0b"):
                t.value = int(t.value, 2)
            elif t.value.startswith("0o"):
                t.value = int(t.value, 8)
            elif t.value.startswith("0x"):
                t.value = int(t.value, 16)
            else:
                t.value = int(t.value)
            return t
        except ValueError:
            print(f"[Lexer Error] Número entero mal formado '{t.value}' en línea {t.lineno}")
            t.lexer.skip(len(t.value))

    # Caracteres entre comillas simples - con corrección de la p2
    def t_CHARACTER(self, t):
        r'\'[a-zA-Z0-9]\''
        t.value = t.value[1]
        return t

    # Comentarios de una línea
    t_ignore_COMMENT = r'\#.*'

    # Ignorar espacios y tabulaciones
    t_ignore = ' \t'

    # Contador de líneas
    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # Manejo de errores
    def t_error(self, t):
        print(f"[Lexer Error] Carácter ilegal '{t.value[0]}' en línea {t.lineno}")
        t.lexer.skip(1)

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