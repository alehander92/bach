from byteplay import *
from opcodes import Opcodes
import bach_ast

def z(): 2

class Generator(object):
    BACH_SYMBOL = 'BachSymbol'

    def generate_module(self, sexp, stl=None):
        data = Code.from_code(z.func_code) #Code([], [], [], False, False, False, '<>', '<>', 1, 'a bach file')
        if stl:
            data.code = stl.code
        else:
            data.code = []
        opcodes = Opcodes(map(self.generate, sexp.code)).to_list()
        data.code += opcodes + [(LOAD_CONST, None), (RETURN_VALUE, None)]
        print(data.code)
        return data.to_code()

    def generate(self, node):
        if isinstance(node, bach_ast.Label):
            return self.generate_label(node.as_python_label())
        elif isinstance(node, list):            
            return self.generate_list(node)
        else:
            return getattr(self, 'generate_%s' % type(node).__name__.lower())(*node.__dict__.values())

    def generate_label(self, python_label):
        return Opcodes((LOAD_GLOBAL, python_label))

    def generate_bytecode_label(self):
        return byteplay.Label()

    def generate_if(self, test_node, true_node, false_node):
        test, if_true, if_false = map(self.generate, [test_node, true_node, false_node])
        l = self.generate_bytecode_label()
        return Opcodes(
            test,
            (b.POP_JUMP_IF_FALSE, l),
            true,
            l,
            false)

    def generate_value(self, value):
        return Opcodes((LOAD_CONST, value))

    generate_integer = generate_float = generate_string = generate_value

    def generate_symbol(self, value):
        return Opcodes([
            (LOAD_GLOBAL, self.BACH_SYMBOL),
            (LOAD_CONST,  value),
            (CALL_FUNCTION, None)])

    def generate_quoted_list(self, values):
        v = map(self.generate, values)
        return Opcodes(
            v,
            (BUILD_LIST, len(values)))

    def generate_call(self, handler, args):
        z = map(self.generate, args)
        h = self.generate(handler)
        return Opcodes(
            h,
            z,
            (CALL_FUNCTION, len(z)))

    def generate_list(self, values):
        '''
        if an unquoted list is given, it's assumed
        it's a call : (handler &args)
        '''
        handler, args = values[0], values[1:]
        return self.generate_call(handler, args)

    def generate_dict(self, keys, values):
        z = map(
            lambda pair: Opcodes(map(self.generate, pair), (STORE_MAP, None)),
            zip(keys, values))

        return Opcodes(
            (BUILD_MAP, len(z)),
            z)

    def generate_set(self, values):
        v = map(self.generate, values)
        return Opcodes(
            v,
            (BUILD_SET, len(values)))

    def generate_import(self, module_names):
        modules = map(self.generate_python_module, module_names)
        return Opcodes(modules)

    def generate_python_module(self, module_name):
        name = self.save_name(module_name)
        return Opcodes(
            (LOAD_CONST, -1),
            (LOAD_CONST, None),
            (IMPORT_NAME, name),
            (STORE_NAME, name))

    def generate_do(self, elements):
        return Opcodes(map(self.generate, elements))

    def generate_quote(self, expr):
        if isinstance(expr, bach_ast.Label):
            return self.generate_symbol(expr.label)
        elif isinstance(expr, list):
            return self.generate_quoted_list(expr.values)
        else:
            return self.generate(expr)

    def generate_quasiquote(self, expr):
        if isinstance(expr, bach_ast.Label):
            return self.generate_symbol(expr.label)
        elif isinstance(expr, list):
            return self.generate_quasiquote_list(expr.values)
        else:
            return self.generate(expr)

    def generate_quasiquote_list(self, values):
        z = []
        counter = 0
        y = True
        for value in values:
            if isinstance(value, bach_ast.Unquote):
                z.append(self.generate(value.expr))
                counter += 1
            elif isinstance(value, bach_ast.UnquoteList):
                z.append((BUILD_LIST, counter))
                if y:
                    y = False
                else:
                    z.append((BINARY_ADD, None)) # add to last list
                z.append(self.generate(value.expr))
                z.append((BINARY_ADD, None))
                counter = 0
            else:
                z.append(self.generate(value))

        if counter > 0:
            z.append((BUILD_LIST, counter))
            if not y:
                z.append((BINARY_ADD, None))

        return Opcodes(z)
