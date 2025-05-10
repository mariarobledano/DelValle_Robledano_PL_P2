
# Palabras reservadas
reserved = {
    'int': 'INT',
    'float': 'FLOAT',
    'char': 'CHAR',
    'bool': 'BOOL',
    'true': 'TRUE',
    'false': 'FALSE',
    'def': 'DEF',
    'return': 'RETURN',
    'type': 'TYPE',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT'
}

# Lista de tokens
tokens = [
    'ID',
    'NUMBER',
    'FLOAT_NUMBER',
    'CHARACTER',

    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'EQ', 'GT', 'GE', 'LT', 'LE', 'ASSIGN',

    'LPAREN', 'RPAREN',
    'LBRACKET', 'RBRACKET',
    'LBRACE', 'RBRACE',
    'COMMA', 'COLON', 'DOT', 'SEMICOLON',

    #'NEWLINE',
] + list(reserved.values())
