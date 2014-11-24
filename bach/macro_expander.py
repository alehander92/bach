import bach_ast, types
from bach_macro import BachMacro
from errors import MacroMatchError

class MacroExpander(object):
    '''
    loops around the parsed sexp
    and expands each macro recursively
    '''
    def __init__(self, macros=None):
        self.macros = macros or {}

    def macro_expand(self, node):
       return bach_ast.Program(map(self.macro_expand_node, node.code))

    def macro_expand_node(self, node):
        if isinstance(node, list) and len(node) > 0 and isinstance(node[0], bach_ast.Label) and node[0].label in self.macros:
            macro = self.find_macro(node[0].label, len(node) - 1)
            if isinstance(macro, types.FunctionType):
                return macro(*map(self.macro_expand_node, node[1:]))
            elif isinstance(macro, BachMacro):
                return macro.render(*map(self.macro_expand_node, node[1:]))
        else:
            return node
    
    def find_macro(self, label, args_count):
        if label not in self.macros:
            raise MacroMatchError("No macro for " + label)
        else:
            branches = self.macros[label]
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

