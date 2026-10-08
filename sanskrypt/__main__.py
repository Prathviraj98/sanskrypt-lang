import sys
import os
import ast
from .compiler import SanskritASTCompiler

def get_compiler(filepath):
    lang = 'engscript' if filepath.endswith('.eng') else 'sanskrypt'
    return SanskritASTCompiler(lang=lang)

def cmd_run(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()
    compiler = get_compiler(filepath)
    ast_tree = compiler.compile(code)
    bytecode = compile(ast_tree, filename=filepath, mode="exec")
    exec(bytecode, {})

def cmd_transpile(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()
    compiler = get_compiler(filepath)
    ast_tree = compiler.compile(code)
    print(ast.unparse(ast_tree))

def cmd_ast(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()
    compiler = get_compiler(filepath)
    ast_tree = compiler.compile(code)
    print(ast.dump(ast_tree, indent=4))

def cmd_check(filepath):
    print(f"Checking {filepath}...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        compiler = get_compiler(filepath)
        compiler.compile(code)
        print("✅ Static Verification passed: No syntax errors found.")
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        sys.exit(1)

def cmd_repl():
    print("सस्ं कृत प्रोग्रामि गं वातावरणम ्(Sanskrypt REPL) AST Mode")
    print("Type 'exit' to quit.\n")
    compiler = SanskritASTCompiler(lang='sanskrypt')
    namespace = {}
    while True:
        try:
            command = input("वेद>>> ")
            if command.strip() in ("त्याग", "exit", "quit"):
                break
            if not command.strip():
                continue
            ast_tree = compiler.compile(command)
            bytecode = compile(ast_tree, filename="<stdin>", mode="exec")
            exec(bytecode, namespace)
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: sanskrypt <command> [<args>]")
        print("Commands:")
        print("  run <file>       Execute compiled CPython bytecode")
        print("  transpile <file> Translate to standard Python source")
        print("  ast <file>       Dump CPython AST representation")
        print("  check <file>     Run static grammar validation")
        print("  repl             Launch interactive terminal")
        sys.exit(1)
        
    cmd = sys.argv[1]
    
    # Backwards compatibility for --lint or direct file
    if cmd == '--lint':
        cmd_check(sys.argv[2])
        return
    elif cmd.endswith('.eng') or cmd.endswith('.skr') or cmd.endswith('.sans'):
        cmd_run(cmd)
        return
        
    if cmd == 'repl':
        cmd_repl()
    elif len(sys.argv) > 2:
        filepath = sys.argv[2]
        if cmd == 'run': cmd_run(filepath)
        elif cmd == 'transpile': cmd_transpile(filepath)
        elif cmd == 'ast': cmd_ast(filepath)
        elif cmd == 'check': cmd_check(filepath)
        else: print(f"Unknown command: {cmd}")
    else:
        print(f"Command '{cmd}' requires a file argument.")

if __name__ == "__main__":
    main()
