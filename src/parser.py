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
        ('nonassoc', 'EQ', 'GT', 'GE', 'LT', 'LE'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
        ('right', 'UMINUS'),
        ('right', 'LPAREN', 'RPAREN'),  
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
                     | type_def
                     | if_stmt'''
        p[0] = p[1]

    # ----------------------------- Sentencia IF -----------------------------
    def p_if_stmt(self, p):
        '''if_stmt : IF expression THEN statement_list ELSE statement_list
                | IF expression THEN statement_list'''
        if len(p) == 6:  # IF <exp> THEN <stmt> ELSE <stmt>
            p[0] = ('if_else', p[2], p[4], p[6])
        else:  # IF <exp> THEN <stmt>
            p[0] = ('if', p[2], p[4])

    # ----------------------------- Declaraciones y asignaciones -----------------------------
    def p_declaration(self, p):
        '''declaration : type id_list
                    | type id_list ASSIGN expression'''
        tipo = p[1]
        id_list = p[2]

        # Aquí se procesa cada variable de la lista de identificadores
        for var in id_list:
            try:
                # Depuración: Mostrar el tipo y el nombre de la variable
                print(f"[Parser] Registrando variable: {var} de tipo {tipo}")
                
                if isinstance(tipo, tuple) and tipo[0] == 'vector':
                    tipo_base = tipo[1]
                    tamaño = tipo[2]
                    self.symbol_table.add_vector(var, tipo_base, tamaño)
                else:
                    self.symbol_table.add_variable(var, tipo)
                
            except Exception as e:
                print(f"[SymbolTable Error] {e}")

        # En la parte final del parser, se establece la estructura del nodo
        if len(p) == 3:
            p[0] = ('decl', tipo, id_list)
        else:
            p[0] = ('decl_assign', tipo, id_list, p[4])  


    def p_assignment(self, p):
        'assignment : expression ASSIGN expression'
        var_expr = p[1]
        value_expr = p[3]

        if isinstance(var_expr, tuple) and var_expr[0] == 'var':
            var_name = var_expr[1]

            if not self.symbol_table.exists(var_name):
                print(f"[Semantic Error] Variable '{var_name}' usada antes de ser declarada.")
            else:
                var_type = self.symbol_table.get_type(var_name)
                expr_type = self.infer_type(value_expr)

                # Validación
                if expr_type == 'type_error':
                    print(f"[Semantic Error] Expresión inválida al asignar a '{var_name}'")
                elif not self.types_compatible(var_type, expr_type):
                    print(f"[Semantic Error] No se puede asignar '{expr_type}' a '{var_type}' en '{var_name}'")
                else:
                    print(f"[Info] Asignando a '{var_name}' de tipo '{var_type}' con expresión de tipo '{expr_type}'")
        else:
            print("[Semantic Warning] Asignación a algo que no es una variable directa (como acceso a array o propiedad).")

        p[0] = ('assign', var_expr, value_expr)


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
    def p_expression_unaria(self, p):
        '''expression : MINUS expression %prec UMINUS
                      | NOT expression'''
        p[0] = ('unop', p[1], p[2])
    
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
    
    def infer_type(self, expr):
        """Dado un nodo de expresión, devuelve su tipo estimado."""
        if expr[0] == 'const':
            value = expr[1]
            if isinstance(value, bool):
                return 'bool'
            elif isinstance(value, int):
                return 'int'
            elif isinstance(value, float):
                return 'float'
            elif isinstance(value, str) and len(value) == 1:
                return 'char'
            else:
                return 'unknown'

        elif expr[0] == 'var':
            var_name = expr[1]
            try:
                return self.symbol_table.get_type(var_name)
            except:
                print(f"[Semantic Error] Variable '{var_name}' usada antes de ser declarada.")
                return 'unknown'

        elif expr[0] == 'unop':
            op = expr[1]
            t = self.infer_type(expr[2])
            if op == 'not':
                return 'bool' if t == 'bool' else 'type_error'
            elif op == '-' and t in ['int', 'float']:
                return t
            else:
                return 'type_error'

        elif expr[0] == 'binop':
            op = expr[1]
            t1 = self.infer_type(expr[2])
            t2 = self.infer_type(expr[3])
            return self.resolve_binop_type(op, t1, t2)

        elif expr[0] == 'func_call':
            func_name = expr[1]
            arg_types = [self.infer_type(arg) for arg in expr[2]]
            return arg_types

        else:
            return 'unknown'

        
    def resolve_binop_type(self, op, t1, t2):
        conversion = ['char', 'int', 'float']

        if t1 == 'type_error' or t2 == 'type_error' or t1 == 'unknown' or t2 == 'unknown':
            return 'type_error'

        if t1 != t2:
            if t1 in conversion and t2 in conversion:
                # Promoción de tipo
                return conversion[max(conversion.index(t1), conversion.index(t2))]
            else:
                return 'type_error'

        if op in ['+', '-', '*', '/']:
            return t1  # mismos tipos compatibles

        elif op in ['==', '<', '>', '<=', '>=']:
            if t1 in ['int', 'float', 'char']:
                return 'bool'
            else:
                return 'type_error'

        elif op in ['and', 'or']:
            return 'bool' if t1 == 'bool' else 'type_error'

        return 'type_error'

    
    def types_compatible(self, declared_type, value_type):
        if declared_type == value_type:
            return True
        if declared_type == 'float' and value_type in ['int', 'char']:
            return True
        if declared_type == 'int' and value_type == 'char':
            return True
        return False

    def p_function_def(self, p):
            'function_def : DEF type ID LPAREN param_list RPAREN COLON LBRACE statement_list RBRACE'
            return_type = p[1]  # El tipo de retorno de la función
            func_name = p[3]    # El nombre de la función
            param_types = [param[0] for param in p[5]]  # Los tipos de los parámetros

            # Agregar la función a la tabla de símbolos
            self.symbol_table.add_function(func_name, return_type, param_types)
            
            p[0] = ('func_def', return_type, func_name, param_types, p[8])

    def p_param_list(self, p):
        '''param_list : param
                      | param_list SEMICOLON param
                      | empty'''
        if len(p) == 2:
            p[0] = [p[1]] if p[1] else []
        else:
            p[0] = p[1] + [p[3]]

    def p_param(self, p):
        'param : type ID'
        p[0] = (p[1], p[2])  # Devuelve un tuple con el tipo y el nombre del parámetro

    def p_expression_func_call(self, p):
        'expression : ID LPAREN arg_list RPAREN'
        func_name = p[1]
        args = p[3]

        # Verificar si la función está registrada
        if not self.symbol_table.exists(func_name):
            print(f"[Semantic Error] Función '{func_name}' no declarada.")
            p[0] = ('error', func_name)
        else:
            func_info = self.symbol_table.get_function(func_name)
            param_types = func_info['param_types']

            # Comprobar si los tipos de los parámetros coinciden
            if len(param_types) != len(args):
                print(f"[Semantic Error] Número de parámetros incorrecto en la llamada a '{func_name}'.")
                p[0] = ('error', func_name)
            else:
                # Comprobar los tipos de los parámetros
                for i, (arg, param_type) in enumerate(zip(args, param_types)):
                    arg_type = self.infer_type(arg)
                    if arg_type != param_type:
                        print(f"[Semantic Error] Tipo de parámetro incorrecto en la posición {i+1} para '{func_name}'. Se esperaba '{param_type}', pero se recibió '{arg_type}'.")
                        p[0] = ('error', func_name)
                    else:
                        print(f"[Info] Llamada a función '{func_name}' con parámetros correctos.")
                        
                p[0] = ('func_call', func_name, args)


