class SemanticError(Exception):
    def __init__(self, message, lineno=None):
        if lineno is not None:
            message = f"[Semantic Error] Línea {lineno}: {message}"
        super().__init__(message)


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_stack = [{}]  # Tabla de símbolos para variables
        self.type_table = {}    # Tabla de tipos (si es necesario)
        self.functions = {}     # Funciones definidas
        self.current_function = None
    
    def _enter_scope(self):
        self.symbol_stack.append({})

    def _exit_scope(self):
        self.symbol_stack.pop()

    def _current_scope(self):
        return self.symbol_stack[-1]

    def _declare_variable(self, name, vtype):
        current = self._current_scope()
        if name in current:
            raise SemanticError(f"La variable '{name}' ya está declarada en este ámbito.")
        current[name] = vtype

    def _lookup_variable(self, name):
        for scope in reversed(self.symbol_stack):
            if name in scope:
                return scope[name]
        raise SemanticError(f"La variable '{name}' no ha sido declarada.")
 
    def analyze(self, node):
        if isinstance(node, list):
            for n in node:
                self.analyze(n)
        elif isinstance(node, tuple):
            tag = node[0]
            method_name = f"_handle_{tag}"
            
            if hasattr(self, method_name):
                return getattr(self, method_name)(node)
            else:
                raise Exception(f"No se ha definido el método para analizar: {tag}")

    def _analyze_statement(self, nodo):
        nodetype = nodo[0]

        if nodetype == 'decl':
            self._handle_declaration(nodo)
        elif nodetype == 'decl_assign':
            self._handle_decl_assign(nodo)
        elif nodetype == 'assign':
            self._handle_assignment(nodo)
        elif nodetype == 'type_def':
            self._handle_type_definition(nodo)
        elif nodetype == 'instance':
            self._handle_instance(nodo)
        elif nodetype == 'func_def':
            self._handle_function_definition(nodo)
        elif nodetype == 'return':
            self._handle_return(nodo)
        elif nodetype == 'if':
            self._handle_if(nodo)
        elif nodetype == 'func_call':
            self._handle_func_call(nodo)  # Manejo de llamada a función
        elif nodetype == 'array_access':
            self._handle_array_access(nodo)  # Manejo de acceso a arrays
        elif nodetype == 'binop':
            self._handle_binop(nodo)  # Manejo de operaciones binarias
        elif nodetype == 'const':
            self._handle_const(nodo)  # Manejo de constantes
        elif nodetype == 'var':
            self._handle_var(nodo)  # Manejo de variables
        elif nodetype == 'while':
            self._handle_while(nodo)
        else:
            raise SemanticError(f"Tipo de sentencia desconocido: {nodetype}")

    def _handle_declaration(self, stmt):
        tipo, lista_ids = stmt[1], stmt[2]
        
        for var in lista_ids:
            self._declare_variable(var, tipo)
            print(f"Declarada variable '{var}' de tipo {tipo}")  # Depuración

    def _handle_assignment(self, node):
        _, lhs, rhs = node  # Desempaquetamos la asignación

        # Primero analizamos el lado derecho (expresión)
        self.analyze(rhs)

        # Comprobamos el tipo de la variable en el lado izquierdo
        if lhs[0] == 'var':  # Si es una variable
            var_name = lhs[1]
            self._lookup_variable(var_name)
            print(f"Asignando a la variable '{var_name}'")  # Depuración
        elif lhs[0] in ('array_access', 'field_access'):  # Si es acceso a un array o campo
            self.analyze(lhs)
        else:
            raise SemanticError(f"Asignación a estructura no válida: {lhs[0]}")

        # Si el lado derecho es una llamada a función (func_call), debemos verificar que la función exista
        if rhs[0] == 'func_call':
            func_name = rhs[1]
            if func_name not in self.functions:
                raise SemanticError(f"La función '{func_name}' no está definida.")
            
            # Analizar los argumentos
            for arg in rhs[2]:
                self.analyze(arg)


    def _handle_decl_assign(self, node):
        _, tipo, lista_ids, expr = node
        for var in lista_ids:
            self._declare_variable(var, tipo)
        self.analyze(expr)  # Analizamos la expresión



    def _handle_function_definition(self, stmt):
        func_type, func_name, params, body = stmt[1], stmt[2], stmt[3], stmt[4]

        if func_name in self.functions:
            raise SemanticError(f"La función '{func_name}' ya está definida.")

        self.functions[func_name] = {'type': func_type, 'params': params}

        self._enter_scope()  # Nuevo ámbito para la función

        for param_type, param_name in params:
            self._declare_variable(param_name, param_type)

        self.current_function = func_name
        for stmt in body:
            self._analyze_statement(stmt)
        self.current_function = None

        self._exit_scope()

    def _handle_return(self, stmt):
        if self.current_function is None:
            raise SemanticError(f"El 'return' debe estar dentro de una función.")
        
        expr = stmt[1]
        
        func_type = self.functions[self.current_function]['type']
        expr_type = self._get_expression_type(expr)

        if func_type != expr_type:
            raise SemanticError(f"El tipo de la expresión de retorno '{expr_type}' no coincide con el tipo de la función '{func_type}'.")

    def _handle_if(self, stmt):
        condition, true_stmt, false_stmt = stmt[1], stmt[2], stmt[3]
        
        condition_type = self._get_expression_type(condition)
        
        if condition_type != 'bool':
            raise SemanticError(f"La condición del 'if' debe ser de tipo 'bool', pero es '{condition_type}'.")

        self._analyze_statement(true_stmt)
        if false_stmt:
            self._analyze_statement(false_stmt)

    def _handle_while(self, stmt):
        condition, body = stmt[1], stmt[2]

        condition_type = self._get_expression_type(condition)
        if condition_type != 'bool':
            raise SemanticError("La condición del 'while' debe ser de tipo 'bool'.")

        for inner_stmt in body:
            self._analyze_statement(inner_stmt)
        
    def _handle_program(self, node):
        for stmt in node[1]:
            self._analyze_statement(stmt)

    def _handle_func_call(self, node):
        func_name = node[1]
        args = node[2]

        if func_name not in self.functions:
            raise SemanticError(f"La función '{func_name}' no está definida.")
        
        func_params = self.functions[func_name]['params']
        if len(args) != len(func_params):
            raise SemanticError(f"La función '{func_name}' requiere {len(func_params)} parámetros, pero se le dieron {len(args)}.")

    def _handle_const(self, node):
        return node[1]  # Retornamos el valor de la constante
    
    def _handle_binop(self, node):
        left_expr = node[1]
        right_expr = node[2]
        
        # Analizar los tipos de los operandos (izquierdo y derecho)
        left_type = self._get_expression_type(left_expr)
        right_type = self._get_expression_type(right_expr)

        # Verificar que los operandos sean del mismo tipo
        if left_type != right_type:
            raise SemanticError(f"Los tipos de los operandos no coinciden: '{left_type}' vs '{right_type}'.")

        return left_type

    def _handle_binop(self, node):
        # El nodo binop debe tener tres elementos: el operador y los dos operandos
        operator = node[1]  # El operador: +
        left_expr = node[2]  # El operando izquierdo
        right_expr = node[3]  # El operando derecho
        
        # Verificamos los tipos de los operandos
        left_type = self._get_expression_type(left_expr)
        right_type = self._get_expression_type(right_expr)
        
        # Comprobamos si los tipos de los operandos coinciden
        if left_type != right_type:
            raise SemanticError(f"Los tipos de los operandos no coinciden: '{left_type}' vs '{right_type}'.")
        
        return left_type  # Devolvemos el tipo resultante de la operación

    def _get_expression_type(self, expr):
        if isinstance(expr, tuple):  # Si es una expresión compleja (binaria, unaria)
            if expr[0] == 'binop':
                operator = expr[1]
                left_expr = expr[2]
                right_expr = expr[3]
                left_type = self._get_expression_type(left_expr)
                right_type = self._get_expression_type(right_expr)

                if left_type != right_type:
                    raise SemanticError(f"Los tipos de los operandos no coinciden: {left_type} vs {right_type}.")

                # Devuelve el tipo de resultado esperado (por ejemplo, bool si es comparación)
                if operator in ['==', '>', '<', '>=', '<=']:
                    return 'bool'
                return left_type

        elif isinstance(expr, str):  # Si es una variable
            return self._lookup_variable(expr)
        elif isinstance(expr, (int, float, bool)):
            if isinstance(expr, bool):
                return 'bool'
            elif isinstance(expr, int):
                return 'int'
            elif isinstance(expr, float):
                return 'float'
        else:
            raise SemanticError(f"Expresión desconocida: {expr}")


    def _handle_array_access(self, node):
        self.analyze(node[1])  # Analizamos el índice del array
        
        var_name = node[0][1]  # El nombre del array
        return self._lookup_variable(var_name)
    
    def _handle_var(self, node):
        var_name = node[1]
        return self._lookup_variable(var_name)
