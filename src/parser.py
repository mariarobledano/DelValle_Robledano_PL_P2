import ply.yacc as yacc
from viper_tokens import tokens as token_list
from symbol_table import SymbolTable



class Parser:
    def __init__(self):
        self.tokens = token_list
        self.parser = yacc.yacc(module=self, write_tables=False)
        self.symbol_table = SymbolTable()

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

    # ----------------------------- Programa principal -----------------------------
    def p_program(self, p):
        'program : global_statement_list'
        p[0] = ('program', p[1])

    def p_global_statement_list(self, p):
        '''global_statement_list : global_statement
                                 | global_statement_list global_statement'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_global_statement(self, p):
        '''global_statement : declaration
                            | assignment
                            | function_def
                            | type_def
                            | instance'''
        p[0] = p[1]

    # ----------------------------- Sentencias (solo para funciones) -----------------------------
    def p_statement_list(self, p):
        '''statement_list : statement SEMICOLON
                        | statement_list statement SEMICOLON'''
        if len(p) == 3:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]


    def p_statement(self, p):
        '''statement : declaration
                     | assignment
                     | return_stmt
                     | instance
                     | type_def'''
        p[0] = p[1]

    # ----------------------------- Declaraciones y asignaciones -----------------------------
    def p_declaration(self, p):
        '''declaration : type id_list
                       | type id_list ASSIGN expression'''
        tipo = p[1]
        id_list = p[2]

        for var in id_list:
            try:
                if isinstance(tipo, tuple) and tipo[0] == 'vector':
                    tipo_base = tipo[1]
                    tamaño = tipo[2]
                    self.symbol_table.add_vector(var, tipo_base, tamaño)
                else:
                    self.symbol_table.add_variable(var, tipo)
            except Exception as e:
                print(e)

        if len(p) == 3:
            p[0] = ('decl', tipo, id_list)
        else:
            p[0] = ('decl_assign', tipo, id_list, p[4])

    def p_assignment(self, p):
        'assignment : expression ASSIGN expression'
        p[0] = ('assign', p[1], p[3])

    def p_return_stmt(self, p):
        'return_stmt : RETURN expression'
        p[0] = ('return', p[2])

    # ----------------------------- Definición de funciones -----------------------------
    def p_function_def(self, p):
        'function_def : DEF type ID LPAREN param_list RPAREN COLON LBRACE statement_list RBRACE'
        p[0] = ('func_def', p[2], p[3], p[5], p[9])

    def p_param_list(self, p):
        '''param_list : param
                      | param_list SEMICOLON param
                      | empty'''
        if len(p) == 2:
            if p[1] is None:
                p[0] = []
            else:
                p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_param(self, p):
        'param : type ID'
        p[0] = (p[1], p[2])

    # ----------------------------- Tipos e identificadores -----------------------------
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

    def p_id_list_single(self, p):
        'id_list : ID'
        p[0] = [p[1]]

    def p_id_list_rec(self, p):
        'id_list : id_list COMMA ID'
        p[0] = p[1] + [p[3]]

    # ----------------------------- Registros -----------------------------
    def p_type_def(self, p):
        'type_def : TYPE ID COLON LBRACE field_list RBRACE'
        p[0] = ('type_def', p[2], p[5])

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

    def p_instance(self, p):
        'instance : ID ID'
        p[0] = ('instance', p[1], p[2])

    # ----------------------------- Expresiones -----------------------------
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

    def p_expression_field_access(self, p):
        'expression : expression DOT ID'
        p[0] = ('field_access', p[1], p[3])

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

    # ----------------------------- Utilidades -----------------------------
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
