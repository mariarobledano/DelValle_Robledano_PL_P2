class SymbolTable:
    def __init__(self):
        self.variables = {}  
        self.functions = {}  

    def add_variable(self, name, var_type):
        """Registra una variable simple (int, float, bool, char)."""
        if name in self.variables:
            raise Exception(f"[SymbolTable Error] Variable '{name}' ya declarada")
        self.variables[name] = {'type': var_type, 'kind': 'basic'}

    def add_function(self, name, return_type, param_types):
        """Registra una función."""
        if name in self.functions:
            raise Exception(f"[SymbolTable Error] Función '{name}' ya declarada")
        self.functions[name] = {'return_type': return_type, 'param_types': param_types}

    def exists(self, name):
        """Devuelve True si la variable o función ya está en la tabla."""
        return name in self.variables or name in self.functions

    def get_type(self, name):
        """Devuelve el tipo de la variable o función."""
        if name in self.variables:
            return self.variables[name]['type']
        elif name in self.functions:
            return self.functions[name]['return_type']
        else:
            raise Exception(f"[SymbolTable Error] '{name}' no declarado")

    def get_function(self, name):
        """Devuelve la información de la función."""
        if name not in self.functions:
            raise Exception(f"[SymbolTable Error] Función '{name}' no declarada")
        return self.functions[name]

    def debug_print(self):
        """Imprime la tabla de símbolos de forma organizada."""
        print("\n📋 Tabla de símbolos actual:")
        print(f"{'Nombre':<20}{'Tipo':<10}{'Kind':<10}{'Tamaño':<10}")
        print("-" * 50)

        for name, info in self.variables.items():
            size = info.get('size', '')  # Si no tiene tamaño, dejamos vacío
            print(f"{name:<20}{info['type']:<10}{info['kind']:<10}{size:<10}")
        
        print("\nFunciones registradas:")
        for name, func in self.functions.items():
            print(f"{name:<20} {func['return_type']:<10} {'function'} {'-'}")
