#!/usr/bin/env python3
"""Script para validar sintaxis de los endpoints de peleas y topes"""

import ast
import sys

def validate_python_syntax(file_path):
    """Valida la sintaxis de un archivo Python"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Compilar el código para verificar sintaxis
        ast.parse(content, filename=file_path)
        print(f"✅ {file_path}: Sintaxis válida")
        return True
        
    except SyntaxError as e:
        print(f"❌ {file_path}: Error de sintaxis en línea {e.lineno}: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ {file_path}: Error: {str(e)}")
        return False

def main():
    files_to_check = [
        "app/api/v1/peleas.py",
        "app/api/v1/topes.py",
        "app/schemas/pelea.py",
        "app/schemas/tope.py"
    ]
    
    all_valid = True
    
    for file_path in files_to_check:
        if not validate_python_syntax(file_path):
            all_valid = False
    
    if all_valid:
        print("\n🎉 Todos los archivos tienen sintaxis válida!")
        return 0
    else:
        print("\n💥 Se encontraron errores de sintaxis")
        return 1

if __name__ == "__main__":
    sys.exit(main())