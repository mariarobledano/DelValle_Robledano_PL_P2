import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.lexer import lexer
from src.parser import parser


input_dir = os.path.join(os.path.dirname(__file__), '../tests')
output_dir = os.path.join(input_dir, 'tokens')
os.makedirs(output_dir, exist_ok=True)

def pretty_print(tree, indent=0):
    if isinstance(tree, tuple):
        print("  " * indent + str(tree[0]))
        for child in tree[1:]:
            pretty_print(child, indent + 1)
    elif isinstance(tree, list):
        for item in tree:
            pretty_print(item, indent)
    else:
        print("  " * indent + str(tree))

        
for filename in os.listdir(input_dir):
    if filename.endswith(".vip"):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + ".token")

        print(f"🟡 Procesando {filename}...")

        with open(input_path, "r", encoding="utf-8") as f:
            data = f.read()

        lexer.lineno = 1
        lexer.input(data)

        success = True
        with open(output_path, "w", encoding="utf-8") as out:
            while True:
                try:
                    tok = lexer.token()
                except Exception as e:
                    print(f"❌ Error en {filename}: {e}")
                    success = False
                    break
                if not tok:
                    break
                out.write(f"{tok.type} {tok.value}\n")

        if success:
            print(f"✅ {filename} procesado correctamente. Tokens en: tests/tokens/{os.path.basename(output_path)}")

            # Ahora ejecutamos el parser
            try:
                result = parser.parse(data, lexer=lexer)
                print(f"🌳 Árbol sintáctico de {filename}:\n")
                pretty_print(result)
                print()
            except Exception as e:
                print(f"❌ Error de sintaxis en {filename}: {e}\n")

        else:
            print(f"❌ {filename} tuvo errores.\n")


