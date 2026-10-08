# Sanskrypt & EngScript

A root-based, order-agnostic programming language parser inspired by Paninian grammar. 

Sanskrypt replaces hundreds of arbitrary keywords with a minimal set of foundational roots (*Dhatus*), allowing you to construct expressive, self-documenting code. It supports two dialects: the original **Sanskrypt** (using Sanskrit roots) and **EngScript** (mapped to English roots).

## Installation

```bash
pip install sanskrypt
```

## Quick Start

```python
import sanskrypt

code = """
hold_var n_count v_0
do_loop n_count < 3
    speak_out n_count
    compute_math n_count n_count + 1
end
"""

sanskrypt.run(code, lang='engscript')
```
