import ply.yacc as yacc
from viper_tokens import tokens as token_list


class Parser:
    def __init__(self):
        self.tokens = token_list
        self.parser = yacc.yacc(module=self, write_tables=False)

    # ----------------------------- Precedencia de operadores -----------------------------
    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('right', 'NOT'),
        ('nonassoc', 'EQ', 'GT', 'GE', 'LT', 'LE'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
        ('right', 'UMINUS'),
    )

    # ----------------------------- Reglas del parser -----------------------------

    def p_program(self, p):
        'program : statement_list'
        p[0] = ('program', p[1])

    def p_statement_list(self, p):
        '''statement_list : statement
                          | statement_list statement'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_statement_declaration(self, p):
        '''statement : type id_list
                     | type id_list ASSIGN expression'''
        if len(p) == 3:
            p[0] = ('decl', p[1], p[2])
        else:
            p[0] = ('decl_assign', p[1], p[2], p[4])

    def p_id_list_single(self, p):
        'id_list : ID'
        p[0] = [p[1]]

    def p_id_list_rec(self, p):
        'id_list : id_list COMMA ID'
        p[0] = p[1] + [p[3]]


    def p_type(self, p):
        '''type : base_type
                | base_type LBRACKET NUMBER RBRACKET'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ('vector', p[1], p[3])

    def p_base_type(self, p):
        '''base_type : INT
                    | FLOAT
                    | CHAR
                    | BOOL'''
        p[0] = p[1]

    def p_expression_binaria(self, p):
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

    def p_expression_unaria(self, p):
        '''expression : MINUS expression %prec UMINUS
                      | NOT expression'''
        p[0] = ('unop', p[1], p[2])

    def p_expression_group(self, p):
        'expression : LPAREN expression RPAREN'
        p[0] = p[2]

    def p_expression_number(self, p):
        '''expression : NUMBER
                      | FLOAT_NUMBER
                      | TRUE
                      | FALSE
                      | CHARACTER'''
        p[0] = ('const', p[1])

    def p_expression_id(self, p):
        'expression : ID'
        p[0] = ('var', p[1])

    def p_expression_array_access(self, p):
        'expression : expression LBRACKET expression RBRACKET'
        p[0] = ('array_access', p[1], p[3])

    def p_statement_assign(self, p):
        'statement : expression ASSIGN expression'
        p[0] = ('assign', p[1], p[3])

    def p_statement_function(self, p):
        'statement : DEF type ID LPAREN param_list RPAREN COLON LBRACE statement_list RBRACE'
        p[0] = ('func_def', p[2], p[3], p[5], p[9])

    def p_param_list(self, p):
        '''param_list : param
                      | param_list SEMICOLON param'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_param(self, p):
        'param : type ID'
        p[0] = (p[1], p[2])

    def p_statement_return(self, p):
        'statement : RETURN expression'
        p[0] = ('return', p[2])

    def p_expression_func_call(self, p):
        'expression : ID LPAREN arg_list RPAREN'
        p[0] = ('func_call', p[1], p[3])

    def p_arg_list(self, p):
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

    def p_statement_type_def(self, p):
        'statement : TYPE ID COLON LBRACE field_list RBRACE'
        p[0] = ('type_def', p[2], p[5])

    def p_statement_instance(self, p):
        'statement : ID ID'
        p[0] = ('instance', p[1], p[2])


    def p_field_list(self, p):
        '''field_list : field
                      | field_list field'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_field(self, p):
        'field : type ID'
        p[0] = (p[1], p[2])

    def p_expression_field_access(self, p):
        'expression : expression DOT ID'
        p[0] = ('field_access', p[1], p[3])

    def p_empty(self, p):
        'empty :'
        p[0] = None

    def p_error(self, p):
        if p:
            print(f"[Syntax Error] Token inesperado '{p.value}' en línea {p.lineno}")
        else:
            print("[Syntax Error] Fin de entrada inesperado")

    def parse(self, input_text, lexer=None):
        return self.parser.parse(input_text, lexer=lexer)
