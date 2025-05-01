
class SymbolTable:
    def __init__(self):
        self.variables = {}  # Diccionario para guardar: nombre → info

    def add_variable(self, name, var_type):
        """Registra una variable simple (int, float, bool, char)."""
        if name in self.variables:
            raise Exception(f"[SymbolTable Error] Variable '{name}' ya declarada")
        self.variables[name] = {'type': var_type, 'kind': 'basic'}

    def add_vector(self, name, var_type, size):
        """Registra un vector (ej: int[3])"""
        if name in self.variables:
            raise Exception(f"[SymbolTable Error] Vector '{name}' ya declarado")
        self.variables[name] = {'type': var_type, 'kind': 'vector', 'size': size}

    def exists(self, name):
        """Devuelve True si la variable ya está en la tabla."""
        return name in self.variables

    def get_type(self, name):
        """Devuelve el tipo de la variable."""
        if name not in self.variables:
            raise Exception(f"[SymbolTable Error] Variable '{name}' no declarada")
        return self.variables[name]['type']

    def get_info(self, name):
        """Devuelve toda la información de una variable."""
        if name not in self.variables:
            raise Exception(f"[SymbolTable Error] Variable '{name}' no declarada")
        return self.variables[name]


    def debug_print(self):
        print("📋 Tabla de símbolos actual:")
        for name, info in self.variables.items():
            print(f"  - {name}: {info}")
