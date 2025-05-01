import sys
import os

from lexer import Lexer
from parser import Parser

class ParserRunner:
    def __init__(self):
        self.lexer_instance = Lexer()
        self.lexer = self.lexer_instance.lexer
        self.parser = Parser()

    def pretty_print(self, tree, indent=0):
        if isinstance(tree, tuple):
            print("  " * indent + str(tree[0]))
            for child in tree[1:]:
                self.pretty_print(child, indent + 1)
        elif isinstance(tree, list):
            for item in tree:
                self.pretty_print(item, indent)
        else:
            print("  " * indent + str(tree))

    def run(self, input_dir='tests'):
        input_dir = os.path.join(os.path.dirname(__file__), '..', input_dir)
        output_dir = os.path.join(input_dir, 'tokens')
        os.makedirs(output_dir, exist_ok=True)

        for filename in os.listdir(input_dir):
            if filename.endswith(".vip"):
                input_path = os.path.join(input_dir, filename)
                output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + ".token")

                print(f"\U0001F7E1 Procesando {filename}...")

                with open(input_path, "r", encoding="utf-8") as f:
                    data = f.read()

                self.lexer.lineno = 1
                self.lexer.input(data)

                success = True
                with open(output_path, "w", encoding="utf-8") as out:
                    while True:
                        try:
                            tok = self.lexer.token()
                        except Exception as e:
                            print(f"\u274C Error en {filename}: {e}")
                            success = False
                            break
                        if not tok:
                            break
                        out.write(f"{tok.type} {tok.value}\n")

                if success:
                    print(f"\u2705 {filename} procesado correctamente. Tokens en: tests/tokens/{os.path.basename(output_path)}")
                    try:
                        result = self.parser.parse(data, lexer=self.lexer) 
                        print(f"\U0001F333 Árbol sintáctico de {filename}:\n")
                        self.pretty_print(result)
                        self.parser.symbol_table.debug_print()  
                        print()
                    except Exception as e:
                        print(f"\u274C Error de sintaxis en {filename}: {e}\n")

# Para ejecutar desde consola:
if __name__ == "__main__":
    runner = ParserRunner()
    runner.run()
