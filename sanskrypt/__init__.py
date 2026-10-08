from .interpreter import Interpreter

def run(code, lang='sanskrypt'):
    """
    Executes a string of Sanskrypt or EngScript code.
    :param code: The code string to execute.
    :param lang: 'sanskrypt' or 'engscript'.
    :return: The Interpreter instance (contains .variables).
    """
    interpreter = Interpreter(lang=lang)
    interpreter.execute(code)
    return interpreter

def run_file(filepath, lang=None):
    """
    Executes a .skr or .eng file.
    :param filepath: Path to the script.
    :param lang: Forces language parser (auto-detected if None).
    """
    if lang is None:
        lang = 'engscript' if filepath.endswith('.eng') else 'sanskrypt'
        
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()
        
    return run(code, lang=lang)
