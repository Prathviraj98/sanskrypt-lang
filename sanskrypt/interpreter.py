import re
import shlex
import urllib.request

class Interpreter:
    def __init__(self, lang='sanskrypt'):
        self.variables = {}
        self.lang = lang.lower()
        
        if self.lang == 'engscript':
            self.roots = {
                'speak': 'io',
                'hold': 'assign',
                'compute': 'compute',
                'do': 'control',
            }
            self.end_marker = 'end'
        else:
            # Default to Sanskrypt
            self.roots = {
                'vad': 'io',
                'dhri': 'assign',
                'gan': 'compute',
                'kri': 'control',
            }
            self.end_marker = 'iti'

    def _get_root(self, command):
        for root in self.roots:
            if command.startswith(root):
                return root, command[len(root):]
        return None, None

    def execute(self, code):
        lines = [l.strip() for l in code.strip().split('\n') if l.strip() and not l.strip().startswith('#')]
        self._execute_block(lines)

    def _extract_vibhakti(self, args, needs_target=True):
        var_name = None
        val_parts = []
        for arg in args:
            if needs_target and arg.startswith('n_') and var_name is None:
                var_name = arg[2:]
            elif arg.startswith('v_'):
                val_parts.append(arg[2:])
            else:
                if arg.startswith('n_'):
                    val_parts.append(arg[2:])
                else:
                    val_parts.append(arg)
        
        if needs_target and var_name is None and val_parts:
            var_name = val_parts[0]
            val_parts = val_parts[1:]
            
        val_expr = " ".join(val_parts) if val_parts else None
        return var_name, val_expr

    def _execute_block(self, lines):
        pc = 0
        while pc < len(lines):
            line = lines[pc]
            if line == self.end_marker:
                pc += 1
                continue
                
            tokens = shlex.split(line, posix=False) 
            command = tokens[0]
            args = tokens[1:]
            
            base_root, suffix = self._get_root(command)
            if not base_root:
                raise SyntaxError(f"[{self.lang.upper()}] Unknown root: {command}")
                
            action = self.roots[base_root]
            
            if action == 'assign':
                var_name, val_expr = self._extract_vibhakti(args, needs_target=True)
                self.variables[var_name] = self._eval_expr(val_expr)
                
            elif action == 'io':
                if suffix.startswith('_net'):
                    var_name, url_expr = self._extract_vibhakti(args, needs_target=True)
                    url = self._eval_expr(url_expr)
                    try:
                        req = urllib.request.Request(url, headers={'User-Agent': f'{self.lang.capitalize()}/2.0'})
                        with urllib.request.urlopen(req) as response:
                            content = response.read().decode('utf-8')
                            self.variables[var_name] = content[:150] + "... [truncated]"
                    except Exception as e:
                        self.variables[var_name] = f"Network Error: {e}"
                else:
                    _, val_expr = self._extract_vibhakti(args, needs_target=False)
                    print(f"Output: {self._eval_expr(val_expr)}")
                    
            elif action == 'compute':
                var_name, val_expr = self._extract_vibhakti(args, needs_target=True)
                self.variables[var_name] = self._eval_expr(val_expr)
                
            elif action == 'control':
                end_idx = self._find_block_end(lines, pc)
                block_lines = lines[pc+1:end_idx]
                
                _, cond_expr = self._extract_vibhakti(args, needs_target=False)
                
                if suffix.startswith('_yadi') or suffix.startswith('_if'):
                    if self._eval_expr(cond_expr):
                        self._execute_block(block_lines)
                elif suffix.startswith('_chakra') or suffix.startswith('_loop'):
                    while self._eval_expr(cond_expr):
                        self._execute_block(block_lines)
                        
                pc = end_idx
                
            pc += 1

    def _find_block_end(self, lines, start_idx):
        depth = 1
        for i in range(start_idx + 1, len(lines)):
            line = lines[i]
            
            # Count opening blocks
            if self.lang == 'sanskrypt' and line.startswith('kri_'): depth += 1
            elif self.lang == 'engscript' and line.startswith('do_'): depth += 1
            
            # Count closing blocks
            if line == self.end_marker: depth -= 1
            
            if depth == 0: return i
            
        raise SyntaxError(f"Missing '{self.end_marker}' (block end marker) starting at line {start_idx}")

    def _eval_expr(self, expr_str):
        if not expr_str: return ""
        if expr_str.startswith('"') and expr_str.endswith('"'):
            return expr_str[1:-1]
        
        sorted_vars = sorted(self.variables.keys(), key=len, reverse=True)
        for var in sorted_vars:
            val = self.variables[var]
            if isinstance(val, str):
                expr_str = re.sub(rf'\b{var}\b', f'"{val}"', expr_str)
            else:
                expr_str = re.sub(rf'\b{var}\b', str(val), expr_str)
        try:
            return eval(expr_str)
        except Exception:
            return expr_str
