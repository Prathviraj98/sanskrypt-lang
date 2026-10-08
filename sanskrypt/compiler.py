import ast
import unicodedata
import shlex

class SanskritASTCompiler:
    """Compiles parsed Sanskrit/Engscript constructs into executable CPython AST."""
    
    def __init__(self, lang='engscript'):
        self.lang = lang.lower()
        if self.lang == 'engscript':
            self.roots = {
                'speak': 'io', 'hold': 'assign', 'compute': 'compute', 'do': 'control',
                'file': 'file', 'func': 'function', 'mold': 'object', 'try': 'try',
                'bring': 'import'
            }
            self.end_marker = 'end'
        else:
            self.roots = {
                'vad': 'io', 'dhri': 'assign', 'gan': 'compute', 'kri': 'control',
                'lekh': 'file', 'karya': 'function', 'rupa': 'object', 'yatna': 'try',
                'anaya': 'import'
            }
            self.end_marker = 'iti'

    def transcode_devanagari_digits(self, text: str) -> str:
        return "".join(str(ord(ch) - 0x0966) if '\u0966' <= ch <= '\u096f' else ch for ch in text)

    def normalize_source(self, code: str) -> str:
        # Phase 1: NFC Normalization & Lexical Safety
        code = unicodedata.normalize("NFC", code)
        code = self.transcode_devanagari_digits(code)
        return code

    def _get_root(self, command):
        for root in self.roots:
            if command.startswith(root): return root, command[len(root):]
        return None, None

    def _extract_vibhakti(self, args, needs_target=True):
        var_name = None
        val_parts = []
        for arg in args:
            if needs_target and arg.startswith('n_') and var_name is None:
                var_name = arg[2:]
            elif arg.startswith('v_'):
                val_parts.append(arg[2:])
            else:
                if arg.startswith('n_'): val_parts.append(arg[2:])
                else: val_parts.append(arg)
        if needs_target and var_name is None and val_parts:
            var_name = val_parts[0]
            val_parts = val_parts[1:]
        val_expr = " ".join(val_parts) if val_parts else None
        return var_name, val_expr

    def _parse_expr(self, expr_str: str) -> ast.expr:
        if not expr_str: return ast.Constant(value=None)
        try:
            return ast.parse(expr_str, mode='eval').body
        except SyntaxError:
            return ast.Constant(value=expr_str)

    def compile(self, code: str) -> ast.Module:
        code = self.normalize_source(code)
        lines = [l.strip() for l in code.strip().split('\n')]
        
        body = self._parse_block(lines, 0, len(lines))
        module = ast.Module(body=body, type_ignores=[])
        ast.fix_missing_locations(module)
        return module

    def _find_block_end(self, lines, start_idx):
        depth = 1
        for i in range(start_idx + 1, len(lines)):
            line = lines[i]
            if not line or line.startswith('#'): continue
            
            tokens = line.split()
            if not tokens: continue
            command = tokens[0]
            
            if command == self.end_marker:
                depth -= 1
                if depth == 0: return i
            else:
                base_root, suffix = self._get_root(command)
                if base_root:
                    action = self.roots[base_root]
                    if action in ['control', 'try'] or (action == 'function' and suffix.startswith('_def')):
                        depth += 1
        raise SyntaxError(f"Missing '{self.end_marker}' for block starting at line {start_idx+1}")

    def _parse_block(self, lines, start_idx, end_idx) -> list:
        stmts = []
        pc = start_idx
        while pc < end_idx:
            line = lines[pc]
            if not line or line.startswith('#') or line == self.end_marker:
                pc += 1
                continue
            
            tokens = shlex.split(line, posix=False)
            command = tokens[0]
            args = tokens[1:]
            
            base_root, suffix = self._get_root(command)
            if not base_root:
                raise SyntaxError(f"Unknown root: {command} at line {pc+1}")
                
            action = self.roots[base_root]
            
            try:
                if action == 'assign' or action == 'compute':
                    var_name, val_expr = self._extract_vibhakti(args, needs_target=True)
                    target = ast.parse(var_name, mode='eval').body
                    if isinstance(target, ast.Name): target.ctx = ast.Store()
                    elif isinstance(target, ast.Attribute): target.ctx = ast.Store()
                    value_node = self._parse_expr(val_expr)
                    assign = ast.Assign(targets=[target], value=value_node, lineno=pc+1, col_offset=0)
                    stmts.append(assign)
                    
                elif action == 'io':
                    if suffix.startswith('_net'):
                        var_name, url_expr = self._extract_vibhakti(args, needs_target=True)
                        target = ast.parse(var_name, mode='eval').body
                        if isinstance(target, ast.Name): target.ctx = ast.Store()
                        val = ast.parse(f"__import__('urllib.request').request.urlopen({url_expr}).read().decode('utf-8')", mode='eval').body
                        stmts.append(ast.Assign(targets=[target], value=val, lineno=pc+1, col_offset=0))
                    else:
                        _, val_expr = self._extract_vibhakti(args, needs_target=False)
                        val_node = self._parse_expr(val_expr)
                        call = ast.Call(func=ast.Name(id='print', ctx=ast.Load()), args=[val_node], keywords=[])
                        stmts.append(ast.Expr(value=call, lineno=pc+1, col_offset=0))
                        
                elif action == 'control':
                    block_end = self._find_block_end(lines, pc)
                    body = self._parse_block(lines, pc+1, block_end)
                    _, cond_expr = self._extract_vibhakti(args, needs_target=False)
                    test_node = self._parse_expr(cond_expr)
                    
                    if suffix.startswith('_yadi') or suffix.startswith('_if'):
                        stmts.append(ast.If(test=test_node, body=body, orelse=[], lineno=pc+1, col_offset=0))
                    elif suffix.startswith('_chakra') or suffix.startswith('_loop'):
                        stmts.append(ast.While(test=test_node, body=body, orelse=[], lineno=pc+1, col_offset=0))
                    pc = block_end
                    
                elif action == 'function':
                    if suffix.startswith('_def'):
                        block_end = self._find_block_end(lines, pc)
                        body = self._parse_block(lines, pc+1, block_end)
                        var_name, _ = self._extract_vibhakti(args, needs_target=True)
                        args_node = ast.arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[])
                        func_def = ast.FunctionDef(name=var_name, args=args_node, body=body, decorator_list=[], lineno=pc+1, col_offset=0)
                        stmts.append(func_def)
                        pc = block_end
                    elif suffix.startswith('_call'):
                        var_name, _ = self._extract_vibhakti(args, needs_target=True)
                        call = ast.Call(func=ast.Name(id=var_name, ctx=ast.Load()), args=[], keywords=[])
                        stmts.append(ast.Expr(value=call, lineno=pc+1, col_offset=0))
                        
                elif action == 'import':
                    var_name, val_expr = self._extract_vibhakti(args, needs_target=True)
                    mod_name = val_expr.strip('"\'')
                    alias = ast.alias(name=mod_name, asname=var_name)
                    stmts.append(ast.Import(names=[alias], lineno=pc+1, col_offset=0))
                    
                elif action == 'object':
                    var_name, _ = self._extract_vibhakti(args, needs_target=True)
                    target = ast.Name(id=var_name, ctx=ast.Store())
                    val = ast.parse("type('SanskryptObject', (), {})()", mode='eval').body
                    stmts.append(ast.Assign(targets=[target], value=val, lineno=pc+1, col_offset=0))
                    
                elif action == 'try':
                    block_end = self._find_block_end(lines, pc)
                    body = self._parse_block(lines, pc+1, block_end)
                    var_name, _ = self._extract_vibhakti(args, needs_target=True)
                    handler_body = [ast.Pass()]
                    if var_name:
                        handler_body = [ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=ast.Call(func=ast.Name(id='str', ctx=ast.Load()), args=[ast.Name(id='e', ctx=ast.Load())], keywords=[]))]
                    handler = ast.ExceptHandler(type=ast.Name(id='Exception', ctx=ast.Load()), name='e', body=handler_body, lineno=pc+1, col_offset=0)
                    stmts.append(ast.Try(body=body, handlers=[handler], orelse=[], finalbody=[], lineno=pc+1, col_offset=0))
                    pc = block_end
                    
                elif action == 'file':
                    if suffix.startswith('_write'):
                        var_name, val_expr = self._extract_vibhakti(args, needs_target=True)
                        val = ast.parse(f"open({var_name}, 'w', encoding='utf-8').write(str({val_expr}))", mode='eval').body
                        stmts.append(ast.Expr(value=val, lineno=pc+1, col_offset=0))
                    elif suffix.startswith('_read'):
                        var_name, filename_expr = self._extract_vibhakti(args, needs_target=True)
                        target = ast.Name(id=var_name, ctx=ast.Store())
                        val = ast.parse(f"open({filename_expr}, 'r', encoding='utf-8').read()", mode='eval').body
                        stmts.append(ast.Assign(targets=[target], value=val, lineno=pc+1, col_offset=0))
                        
            except Exception as e:
                raise SyntaxError(f"Parse error at line {pc+1}: {str(e)}")
            
            pc += 1
        return stmts
