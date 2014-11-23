import types
import bach_ast

def register_macro(mapping, label, macro, count=None):
    if label not in map:
        mapping[label] = []
    if isinstance(macro, types.FunctionType):
        mapping[label].append(count, macro)
    else:
        mapping[label].append(macro.args_count(), macro)

class BachMacro(object):
    def __init__(self, args, body):
        self.args, self.body = args, body
    
    def render(self, sexps):
        mapping = self.register(sexps)
        return self.generic_render(self.body, mapping)

    def generic_render(self, node, mapping):
        return getattr(self, 'render_' + type(node).lower())(node, mapping)

    def render_list(self, node, mapping):
        if mapping[QUA]:
            result = []
            for child in node:
                if isinstance(child, bach_ast.UnquoteBody):
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

    def render_unquote_body(self, node, mapping):
        if mapping[QUA]:
            return mapping[node.expr.label]
        else:
            return node

    def render_label(self, node, mapping):
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
