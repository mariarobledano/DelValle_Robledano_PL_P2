import ply.yacc as yacc
from src.viper_tokens import tokens

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('nonassoc', 'EQ', 'GT', 'GE', 'LT', 'LE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'UMINUS'),  # operador menos unario: -a
)

#Estructura base del parser
def p_program(p):
    '''program : statement_list'''
    p[0] = ('program', p[1])

def p_statement_list(p):
    '''statement_list : statement
                      | statement_list statement'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]


#Declaraciones de variables
def p_statement_declaration(p):
    '''statement : type ID
                 | type ID ASSIGN expression'''
    if len(p) == 3:
        p[0] = ('decl', p[1], p[2])
    else:
        p[0] = ('decl_assign', p[1], p[2], p[4])

def p_type(p):
    '''type : INT
            | FLOAT
            | CHAR
            | BOOL'''
    p[0] = p[1]


def p_expression_binaria(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression EQ expression
                  | expression GT expression
                  | expression GE expression
                  | expression LT expression
                  | expression LE expression
                  | expression AND expression
                  | expression OR expression'''
    p[0] = ('binop', p[2], p[1], p[3])

def p_expression_unaria(p):
    '''expression : MINUS expression %prec UMINUS
                  | NOT expression'''
    p[0] = ('unop', p[1], p[2])

def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_expression_number(p):
    '''expression : NUMBER
                  | FLOAT_NUMBER
                  | TRUE
                  | FALSE
                  | CHARACTER'''
    p[0] = ('const', p[1])



def p_expression_id(p):
    'expression : ID'
    p[0] = ('var', p[1])


def p_statement_assign(p):
    'statement : ID ASSIGN expression'
    p[0] = ('assign', p[1], p[3])

def p_statement_function(p):
    'statement : DEF type ID LPAREN param_list RPAREN COLON LBRACE statement_list RBRACE'
    p[0] = ('func_def', p[2], p[3], p[5], p[9])  # tipo, nombre, params, cuerpo

def p_param_list(p):
    '''param_list : param
                  | param_list SEMICOLON param'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_param(p):
    'param : type ID'
    p[0] = (p[1], p[2])  # (tipo, nombre)

def p_statement_return(p):
    'statement : RETURN expression'
    p[0] = ('return', p[2])

def p_expression_func_call(p):
    'expression : ID LPAREN arg_list RPAREN'
    p[0] = ('func_call', p[1], p[3])

def p_arg_list(p):
    '''arg_list : expression
                | arg_list COMMA expression
                | empty'''
    if len(p) == 2:
        if p[1] is None:
            p[0] = []
        else:
            p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_empty(p):
    'empty :'
    p[0] = None

def p_statement_type_def(p):
    'statement : TYPE ID COLON LBRACE field_list RBRACE'
    p[0] = ('type_def', p[2], p[5])  

def p_field_list(p):
    '''field_list : field
                  | field_list field'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_field(p):
    'field : type ID'
    p[0] = (p[1], p[2])  # (tipo, nombre)


def p_expression_field_access(p):
    'expression : expression DOT ID'
    p[0] = ('field_access', p[1], p[3])  # ej: ('field_access', ('var', 'juan'), 'edad')


parser = yacc.yacc()
