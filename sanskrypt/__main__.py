import sys
import os
from .interpreter import Interpreter

def lint_file(filepath):
    print(f"Linting {filepath}...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Simple Linter checks
        errors = 0
        lang = 'engscript' if filepath.endswith('.eng') else 'sanskrypt'
        interp = Interpreter(lang)
        
        depth = 0
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('#'): continue
            
            # Check valid root
            tokens = line.split()
            command = tokens[0]
            if command != interp.end_marker:
                root, _ = interp._get_root(command)
                if not root:
                    print(f"Linter Error (Line {i+1}): Unknown root command '{command}'")
                    errors += 1
                    
            # Check block depth
            if lang == 'engscript' and (command.startswith('do_') or command.startswith('func_') or command.startswith('try_')): depth += 1
            if lang == 'sanskrypt' and (command.startswith('kri_') or command.startswith('karya_') or command.startswith('yatna_')): depth += 1
            if command == interp.end_marker: depth -= 1
            
        if depth > 0:
            print(f"Linter Error: Missing {depth} '{interp.end_marker}' block closures.")
            errors += 1
        elif depth < 0:
            print(f"Linter Error: Too many '{interp.end_marker}' block closures.")
            errors += 1
            
        if errors == 0:
            print("✅ Linter passed: 0 syntax errors found.")
        else:
            print(f"❌ Linter failed with {errors} errors.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Fatal Linter Error: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m sanskrypt <file.eng>  OR  python -m sanskrypt --lint <file.eng>")
        sys.exit(1)
        
    if sys.argv[1] == '--lint':
        lint_file(sys.argv[2])
    else:
        from . import run_file
        run_file(sys.argv[1])

if __name__ == "__main__":
    main()
