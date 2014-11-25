import types
import bach_ast
import compiler
import bach_stl
from errors import MacroMatchError

def register_macro(mapping, label, macro, count=None):
    if label not in mapping:
        mapping[label] = []
    if isinstance(macro, types.FunctionType):
        mapping[label].append((count, macro))
    else:
        mapping[label].append((macro.args_count(), macro))

class BachMacro(object):
    def __init__(self, label, args, body):
        self.label, self.args, self.body = label, args, body
    
    def render(self, sexps):
        # mapping = {}
        # if len(self.args) > 0 and isinstance(self.args[-1], bach_ast.Many):
        #     if len(self.args) >= len(sexps) - 1:
        #         for arg, sexp in zip(self.args[:-1], self.sexps[:len(self.args) - 1]):
        #             mapping[arg.label] = sexp
        #         mapping[self.args[-1].label] = sexps[len(self.args) - 1:]
        #     else:
        #         raise MacroMatchError("No enough args for %s" % self.label)
        # else:
        #     if len(self.args) == len(sexps):
        #         for arg, sexp in zip(self.args, sexps):
        #             mapping[arg.label] = sexp
        #     else:
        #         raise MacroMatchError("Expected %d args got %d for %s" % (len(self.args), len(sexps), self.label))
        # value = 
        if not self.args:
            args = []
        elif isinstance(self.args[-1], bach_ast.Many):
            args = self.args[:-1] + [bach_ast.Label(self.args[-1].label)]
        else:
            args = self.args
        
        sexps = [bach_ast.Quote(sexp) for sexp in sexps]
        sexp = bach_ast.Program([[bach_ast.Lambda(args, self.body)] + sexps])
        result = compiler.Compiler().compile_and_eval(sexp, stl=bach_stl.load_stl(), return_value=True)
        return self.normal_sexp(result)

    def normal_sexp(self, sexp):
        '''
        we compile macros to a bach lambda and then run them, so some of the resulting values
        can't have the compile-time node types(only native python types and bach runtime types)
        however they are just several of those cases and they're pretty similar
        we convert the results back to normal bach sexp, so we can easily apply other macros
        '''
        PYTHON_BACH_EQUIVALENTS = {int: bach_ast.Integer, float: bach_ast.Float, str: bach_ast.String, bool: bach_ast.Boolean}
        if isinstance(sexp, list):
            return map(self.normal_sexp, sexp)
        elif type(sexp) in PYTHON_BACH_EQUIVALENTS:
            return PYTHON_BACH_EQUIVALENTS[type(sexp)](sexp)
        elif type(sexp).__name__ == 'BachSymbol':
            return bach_ast.Label(sexp.value)
        elif isinstance(sexp, dict):
            return bach_ast.Dict(map(self.normal_sexp, sexp.keys()), map(self.normal_sexp, sexp.values()))
        elif isinstance(sexp, set):
            return bach_ast.Set(map(self.normal_sexp, sexp))
        else:
            return sexp

    def generic_render(self, node, mapping):
        method_name = 'render_' + type(node).lower()
        if hasattr(self, method_name):
            return getattr(self, 'render_' + type(node).lower())(node, mapping)
        else:
            return node

    def render_list(self, node, mapping):
        if mapping[QUA]:
            result = []
            for child in node:
                if isinstance(child, bach_ast.UnquoteList):
                    result += self.generic_render(child, mapping)
                else:
                    result.append(self.generic_render(child, mapping))
        else:                    
            return [self.generic_render(child) for child in node]
    
    def render_quasiquote(self, node, mapping):
        quasiquote_mapping = mapping.copy()
        quasiquote_mapping[QUA] = True
        return self.generic_render(node.expr, quasiquote_mapping)
    
    def render_quote(self, node, mapping):
        return self.generic_render(node.expr, mapping)

    def render_unquote(self, node, mapping):
        if mapping[QUA]:
            return mapping[node.expr.label]
        else:
            return node

    def render_unquotelist(self, node, mapping):
        if mapping[QUA]:
            return mapping[node.expr.label]
        else:
            return node

    def register(self, sexps):
        mapping = {QUA: False} # a flag for activated quasi
        for arg, sexp in zip(self.args, sexps):
            e = 4
            if isinstance(arg, bach_ast.Label):
                mapping[arg.label] = sexp

        if len(sexps) > len(self.args) and isinstance(self.args[-1], bach_ast.Many):
           mapping[self.args[-1].label] = sexps[len(self.args)-1:]
        return mapping

    def args_count(self):
        if len(self.args) > 0 and isinstance(self.args[-1], bach_ast.Label) or len(self.args) == 0:
            return len(self.args)
        else:
            return (len(self.args),)

