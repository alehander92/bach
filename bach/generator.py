from byteplay import *
from opcodes import Opcodes
import bach_ast
from errors import UnquoteError

def z(): 2

class Generator(object):
    BACH_SYMBOL = 'BachSymbol'

    def generate_module(self, sexp, stl=None):
        data = Code.from_code(z.func_code) #Code([], [], [], False, False, False, '<>', '<>', 1, 'a bach file')
        if stl:
            data.code = stl.code
        else:
            data.code = []
        self.quote_depth = 0
        self.quasiquote_depth = 0
        self.closures = []
        self.outers = []
        opcodes = Opcodes(map(self.generate, sexp.code)).to_list()
        data.code += opcodes + [(LOAD_CONST, None), (RETURN_VALUE, None)]
        # print(data.code)
        return data.to_code()

    def generate(self, node):
        if isinstance(node, bach_ast.Label):
            return self.generate_label(node.label)
        elif isinstance(node, list):            
            return self.generate_list(node)
        else:
            return getattr(self, 'generate_%s' % type(node).__name__.lower())(**node.__dict__)

    def generate_define(self, label, value):
        compiled_value = self.generate(value)
        return Opcodes(
            compiled_value,
            (STORE_GLOBAL, label.label))

    def generate_label(self, python_label):
        if len(self.outers) == 0:
            load = LOAD_GLOBAL
        elif python_label in self.closures[-1]:
            load = LOAD_FAST
        else:
            load = self.outers[-1][python_label]
        return Opcodes((load, python_label))

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

    def generate_do(self, body):
        compiled_body = map(self.generate, body)
        return Opcodes(compiled_body)

    def generate_value(self, value):
        return Opcodes((LOAD_CONST, value))

    generate_integer = generate_float = generate_string = generate_value

    def generate_symbol(self, value):
        return Opcodes([
            (LOAD_GLOBAL, self.BACH_SYMBOL),
            (LOAD_CONST,  value),
            (CALL_FUNCTION, 1)])

    def generate_quoted_list(self, values):
        v = map(self.generate_quote, values)
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

    def generate_vector(self, values):
        compiled_values = map(self.generate, values)
        return Opcodes(compiled_values, (BUILD_LIST, len(values)))

    def generate_list(self, values):
        handler, args = values[0], values[1:]
        return self.generate_call(handler, args)

    def generate_dict(self, keys, values):
        z = map(
            lambda pair: Opcodes(map(self.generate, pair), (STORE_MAP, None)),
            zip(values, keys))

        return Opcodes(
            (BUILD_MAP, len(z)),
            z)

    def generate_set(self, values):
        v = map(self.generate, values)
        return Opcodes(
            v,
            (BUILD_SET, len(values)))

    def generate_import(self, modules):
        compiled_modules = map(self.generate_python_module, modules)
        return Opcodes(compiled_modules)

    def generate_python_module(self, module_name):
        return Opcodes(
            (LOAD_CONST, -1),
            (LOAD_CONST, None),
            (IMPORT_NAME, module_name.label),
            (STORE_GLOBAL, module_name.label))

    def generate_let(self, aliases, body):
        compiled_lambda = self.generate_lambda(body, [], aliases)
        return Opcodes(
            compiled_lambda,
            (CALL_FUNCTION, 0))

    def generate_lambda(self, body, args, let_aliases=None):
        let_fast = set(let_aliases.keys()) if let_aliases else set([])
        arg_labels = {arg.label for arg in args}
        self.closures.append(arg_labels | let_fast)
        self.outers.append({})
        outer_labels = bach_ast.find_outer_labels(body, self.closures[-1])
        is_python_closure = False
        fast = set([])
        for label in outer_labels:
            for closure in self.closures[:-1]:
                if label in closure:
                    self.outers[-1][label] = LOAD_DEREF
                    fast.add(label)
                    is_python_closure = True
                    break
            else:
                self.outers[-1][label] = LOAD_GLOBAL
        
        if let_aliases:
            let_bytecode = [Opcodes(self.generate(value), (STORE_FAST, a)) for a, value in let_aliases.items()]
        else:
            let_bytecode = []
        compiled_body = self.compile_function(arg_labels, self.outers[-1], Opcodes(let_bytecode, map(self.generate, body)))
        self.closures.pop()
        self.outers.pop()

        if is_python_closure:
            fast = [(LOAD_CLOSURE, f) for f in fast]
            return Opcodes(
                fast,
                (BUILD_TUPLE, len(fast)),
                (LOAD_CONST, compiled_body),
                (MAKE_CLOSURE, 0))
        else:
            return Opcodes(
                (LOAD_CONST, compiled_body),
                (MAKE_FUNCTION, 0))

    def compile_function(self, args, outers, body):
        compiled_body = Code.from_code((lambda: None).func_code)
        compiled_body.code = body.to_list()
        if len(compiled_body.code) == 0:
            compiled_body.code += [(LOAD_CONST, None)]
        compiled_body.code += [(RETURN_VALUE, None)]
        compiled_body.code = CodeList(compiled_body.code)
        compiled_body.args = tuple(args)
        compiled_body.freevars = tuple(var for var, load in outers.items() if load == LOAD_DEREF)
        # print('COMPILE')
        # print(compiled_body.code)
        # print(compiled_body.__dict__)
        return compiled_body

    def generate_quote(self, expr):
        self.quote_depth += 1
        if isinstance(expr, bach_ast.Label):
            value = self.generate_symbol(expr.label)
        elif isinstance(expr, list):
            value = self.generate_quoted_list(expr)
        else:
            value = self.generate(expr)
        self.quote_depth -= 1
        return value

    def generate_quasiquote(self, expr):
        self.quasiquote_depth += 1
        if isinstance(expr, bach_ast.Label):
            value = self.generate_symbol(expr.label)
        elif isinstance(expr, list):
            value = self.generate_quasiquote_list(expr)
        else:
            value = self.generate(expr)
        self.quasiquote_depth -= 1
        return value

    def generate_quasiquote_list(self, values):
        z = []
        counter = 0
        y = True
        for value in values:
            if isinstance(value, bach_ast.Unquote):
                z.append(self.generate_unquote(value))
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
                counter += 1

        if counter > 0:
            z.append((BUILD_LIST, counter))
            if not y:
                z.append((BINARY_ADD, None))

        return Opcodes(z)

    def generate_unquote(self, expr):
        if self.in_quasiquote():
            return self.generate(expr)
        elif self.in_quote():
            compiled_expr = self.generate_quote(expr)
            return Opcodes(
                (LOAD_CONST, 'unquote'),
                compiled_expr,
                (BUILD_LIST, 2))
        else:
            raise UnquoteError("Attempting to call unquote outside of quasiquote/quote")

    def in_quasiquote(self):
        return self.quasiquote_depth > 0

    def in_quote(self):
        return self.quote_depth > 0
