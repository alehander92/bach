from bach_macro import register_macro
import bach_ast

__all__ = ['BUILTIN_MACROS']

def if_macro(test, if_true, if_false=None):
    return bach_ast.If(test, if_true, if_false)

def lambda_macro(args, *body):
    return bach_ast.Lambda(args, body)

def define_macro(label, value):
    return bach_ast.Define(label, value)

def dict_macro(*elements):
    print(elements)
    print
    keys = elements[::2]
    values = elements[1::2]
    print(keys)
    print(values)
    return bach_ast.Dict(keys, values)

def set_macro(*elements):
    return bach_ast.Set(elements)

def import_macro(*files):
    return bach_ast.Import(files)

def let_macro(values, *body):
    aliases = dict(zip([value.label for value in values[::2]], values[1::2]))
    return bach_ast.Let(aliases, body)

def vector_macro(*values):
    return bach_ast.Vector(values)

def do_macro(*body):
    return bach_ast.Do(body)


BUILTIN_MACROS = {}
register_macro(BUILTIN_MACROS, 'if', if_macro, (2, 3))
register_macro(BUILTIN_MACROS, 'fn', lambda_macro, (1,))
register_macro(BUILTIN_MACROS, 'define', define_macro, 2)
register_macro(BUILTIN_MACROS, 'dict', dict_macro, (0,))
register_macro(BUILTIN_MACROS, 'set', set_macro, (0,))
register_macro(BUILTIN_MACROS, 'import', import_macro, (1,))
register_macro(BUILTIN_MACROS, 'let', let_macro, (1,))
register_macro(BUILTIN_MACROS, 'vector', vector_macro, (0,))
register_macro(BUILTIN_MACROS, 'do', do_macro, (0,))
