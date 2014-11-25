import bach_ast, types
from bach_macro import BachMacro
from errors import MacroMatchError

class MacroExpander(object):
    '''
    loops around the parsed sexp
    and expands each macro recursively
    '''
    def __init__(self, macros, user_macros):
        self.macros = macros
        self.user_macros = user_macros

    def macro_expand(self, node):
       first = [expanded for expanded in map(self.macro_expand_node, node.code) if expanded]
       return bach_ast.Program(map(self.macro_expand_node, first))

    def macro_expand_node(self, node):
        if isinstance(node, list) and len(node) > 0 and isinstance(node[0], bach_ast.Label) and\
           (node[0].label in self.macros or node[0].label in self.user_macros):
            macro = self.find_macro(node[0].label, len(node) - 1)
            if isinstance(macro, types.FunctionType):
                return macro(*map(self.macro_expand_node, node[1:]))
            elif isinstance(macro, BachMacro):
                return macro.render(map(self.macro_expand_node, node[1:]))
        elif isinstance(node, list):
            return [expanded for expanded in map(self.macro_expand_node, node) if expanded is not None]
        else:
            return node
    
    def find_macro(self, label, args_count):
        branches = self.macros.get(label) or self.user_macros[label]
        for count, macro in branches:
            if isinstance(count, int) and count == args_count:
                return macro
            elif isinstance(count, tuple):
                if len(count) == 1:
                    if args_count >= count[0]:
                        return macro
                elif count[0] <= args_count <= count[1]:
                    return macro
        raise MacroMatchError("No macro for %s with %d args" % (label, args_count))

