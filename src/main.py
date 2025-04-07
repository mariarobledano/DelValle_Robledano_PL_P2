import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.lexer import lexer

input_dir = os.path.join(os.path.dirname(__file__), '../tests')
output_dir = os.path.join(input_dir, 'tokens')
os.makedirs(output_dir, exist_ok=True)

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
            print(f"✅ {filename} procesado correctamente. Tokens en: tests/tokens/{os.path.basename(output_path)}\n")
        else:
            print(f"❌ {filename} tuvo errores.\n")