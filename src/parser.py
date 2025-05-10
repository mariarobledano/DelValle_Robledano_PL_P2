import ply.yacc as yacc
from viper_tokens import tokens as token_list


class Parser:
    def __init__(self):
        self.tokens = token_list
        self.parser = yacc.yacc(module=self, write_tables=True)
        self.current_block = None 

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
    
    # ----------------------------- Program -----------------------------
    def p_program(self, p):
        'program : statement_list'
        p[0] = ('program', p[1])

    # ----------------------------- Statement List -----------------------------
    
    def p_statement_list(self, p):
        '''statement_list : statement
                          | statement_list statement '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]
    
    # ----------------------------- Statements -----------------------------
    def p_statement(self, p):
        '''statement : statement_declaration
                    | statement_assign
                    | statement_function
                    | statement_return
                    | statement_if
                    | statement_instance
                    | statement_type_def'''
        p[0] = p[1]
    
    def p_statement_declaration(self, p):
        '''statement_declaration : type id_list
                                | type id_list ASSIGN expression'''
        if len(p) == 3:
            p[0] = ('decl', p[1], p[2])
        else:
            p[0] = ('decl_assign', p[1], p[2], p[4])
    # Regla para asignaciones
    def p_statement_assign(self, p):
        'statement_assign : expression ASSIGN expression'
        p[0] = ('assign', p[1], p[3])

    # Regla para funciones
    def p_statement_function(self, p):
        'statement_function : DEF type ID LPAREN param_list RPAREN COLON LBRACE statement_list RBRACE'
        self.current_block = 'function'
        p[0] = ('func_def', p[2], p[3], p[5], p[9])
        self.current_block = None  # Salimos del bloque de la función

    # Regla para `return`
    def p_statement_return(self, p):
        'statement_return : RETURN expression'
        if self.current_block == 'function':
            p[0] = ('return', p[2])
        else:
            print(f"[Syntax Error] 'return' fuera de una función en línea {p.lineno(1)}")
            raise SyntaxError("El 'return' debe estar dentro de una función.")

    # Regla para `if`
    def p_statement_if(self, p):
        '''statement_if : IF expression COLON LBRACE statement_list RBRACE
                        | IF expression COLON LBRACE statement_list RBRACE ELSE LBRACE statement_list RBRACE'''
        if len(p) == 7:
            p[0] = ('if', p[2], p[5], None)  # sin else
        else:
            p[0] = ('if', p[2], p[5], p[9])  # con else


    # Regla para `instance` (declaración de instancias)
    def p_statement_instance(self, p):
        'statement_instance : ID ID'
        p[0] = ('instance', p[1], p[2])

    # Regla para 'while'
    def p_statement_while(self, p):
        'statement : WHILE expression COLON LBRACE statement_list RBRACE'
        p[0] = ('while', p[2], p[5])

    # ----------------------------- Type Definitions -----------------------------
    def p_statement_type_def(self, p):
        'statement_type_def : TYPE ID COLON LBRACE field_list RBRACE'
        p[0] = ('type_def', p[2], p[5])

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


    # ----------------------------- Expressions -----------------------------
    def p_expression(self, p):
        '''expression : expression_binaria
                    | expression_comparacion
                    | expression_logica
                    | expression_unaria
                    | expression_group
                    | expression_number
                    | expression_var
                    | expression_array_access
                    | expression_field_access
                    | expression_func_call'''
        p[0] = p[1]

    def p_expression_binaria(self, p):
        '''expression_binaria : expression PLUS expression
                            | expression MINUS expression
                            | expression TIMES expression
                            | expression DIVIDE expression'''
        p[0] = ('binop', p[2], p[1], p[3])

    # Reglas de operaciones de comparación
    def p_expression_comparacion(self, p):
        '''expression_comparacion : expression EQ expression
                                | expression GT expression
                                | expression GE expression
                                | expression LT expression
                                | expression LE expression'''
        p[0] = ('binop', p[2], p[1], p[3])

    # Expresión lógica (AND, OR)
    def p_expression_logica(self, p):
        '''expression_logica : expression AND expression
                            | expression OR expression'''
        p[0] = ('binop', p[2], p[1], p[3])

    def p_expression_unaria(self, p):
        '''expression_unaria : MINUS expression %prec UMINUS
                            | NOT expression'''
        p[0] = ('unop', p[1], p[2])

    def p_expression_group(self, p):
        'expression_group : LPAREN expression RPAREN'
        p[0] = p[2] 

    def p_expression_number(self, p):
        '''expression_number : NUMBER
                            | FLOAT_NUMBER
                            | TRUE
                            | FALSE
                            | CHARACTER'''
        p[0] = ('const', p[1])  

    # Para el acceso a una variable
    def p_expression_var(self, p):
        'expression_var : ID'
        p[0] = ('var', p[1])

    # Para el acceso a un índice de un array
    def p_expression_array_access(self, p):
        'expression_array_access : expression LBRACKET expression RBRACKET'
        p[0] = ('array_access', p[1], p[3]) 

    # Para el acceso a campos
    def p_expression_field_access(self, p):
        'expression_field_access : expression DOT ID'
        p[0] = ('field_access', p[1], p[3])

    def p_expression_func_call(self, p):
        'expression_func_call : ID LPAREN arg_list RPAREN'
        p[0] = ('func_call', p[1], p[3])

    # ----------------------------- Parameters -----------------------------

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

    # ----------------------------- Field List -----------------------------
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


    # ----------------------------- Empty Rule -----------------------------
    def p_empty(self, p):
        'empty :'
        p[0] = None

    # ----------------------------- Error Handling -----------------------------
    def p_error(self, p):
        if p:
            print(f"[Syntax Error] No se esperaba '{p.value}' (tipo: {p.type}) en la línea {p.lineno}")
        else:
            print("[Syntax Error] Fin de entrada inesperado")

    def parse(self, input_text, lexer=None):
        return self.parser.parse(input_text, lexer=lexer)

""" def p_record_type(self, p):
        'record_type : TYPE ID COLON LBRACE field_list RBRACE'
        p[0] = ('record', p[2], p[5])  
""" 

