import os
from .compiler import SanskritASTCompiler

def run(code, lang='engscript'):
    compiler = SanskritASTCompiler(lang=lang)
    ast_tree = compiler.compile(code)
    bytecode = compile(ast_tree, filename="<sanskrypt>", mode="exec")
    exec(bytecode, {})

def run_file(filepath, lang=None):
    if lang is None:
        lang = 'engscript' if filepath.endswith('.eng') else 'sanskrypt'
        
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()
        
    compiler = SanskritASTCompiler(lang=lang)
    ast_tree = compiler.compile(code)
    bytecode = compile(ast_tree, filename=filepath, mode="exec")
    exec(bytecode, {})
