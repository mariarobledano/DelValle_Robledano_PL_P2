import ply.lex as lex
import re
from viper_tokens import tokens, reserved

class Lexer:
    tokens = tokens
    
    def __init__(self):
        self.lexer = lex.lex(module=self)

    # Comentarios multilínea
    def t_MULTILINE_COMMENT(self, t):
        r"\'\'\'(.|\n)*?\'\'\'"  
        t.lexer.lineno += t.value.count('\n')
        return None

    def t_MULTILINE_COMMENT_UNCLOSED(self, t):
        r"\'\'\'(.|\n)*"  # Comentarios sin cerrar
        print(f"[Lexer Error] Comentario multilínea no cerrado en línea {t.lineno}")
        t.lexer.skip(len(t.value))
        return None

    # Identificadores y palabras reservadas
    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = reserved.get(t.value, 'ID')
        return t

    # Números flotantes (incluye notación científica)
    def t_FLOAT_NUMBER(self, t):
        r'(\d+\.\d+([eE][-+]?\d+)?|\d+[eE][-+]?\d+)'
        try:
            t.value = float(t.value)
            return t
        except ValueError:
            print(f"[Lexer Error] Número flotante mal formado '{t.value}' en línea {t.lineno}")
            t.lexer.skip(len(t.value))

    def t_INVALID_LEADING_ZERO(self, t):
        r'0[0-9]+'
        print(f"[Lexer Error] Número decimal con ceros no significativos: '{t.value}' en línea {t.lineno}")
        return None
    # Números enteros en decimal, binario, octal, hexadecimal (no permitir ceros no significativos)
    def t_NUMBER(self, t):
        r'0b[01]+|0o[0-7]+|0x[0-9A-F]+|0|[1-9][0-9]*'
        t.value = int(t.value, 0)
        return t

    # Caracteres entre comillas simples (limitado a ASCII imprimible)
    def t_CHARACTER(self, t):
        r"'(\\\\|\\'|[^\\'])'"
        raw = t.value[1:-1]  # quita las comillas externas

        if raw == "\\\\":
            t.value = "\\"
            return t
        elif raw == "\\'":
            t.value = "'"
            return t
        elif len(raw) == 1 and 32 <= ord(raw) <= 126:
            t.value = raw
            return t
        else:
            print(f"[Lexer Error] Carácter inválido '{raw}' en línea {t.lineno}")
            return None


    # Contador de líneas
    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # Manejo de errores
    def t_error(self, t):
        if t.value[0] in ["'", "\"", "\\"]:  
            print(f"[Lexer Error] Carácter ilegal '{t.value[0]}' en línea {t.lineno}, ignorado.")
            t.lexer.skip(1)
        else:
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
    t_ignore    = ' \t'
    t_ignore_COMMENT    = r'\#.*'
    t_ignore_COMMENT_   = r'/\*([^*]|\*+[^*/])*\*+/'

