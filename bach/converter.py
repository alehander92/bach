import bach_ast

class Converter(object):
    def convert(self, sexp):
        return self.convert_p(sexp.children)

    def convert_p(self, expressions):
        return bach_ast.Program([self.convert_child(expr.children[0]) for expr in expressions])

    def convert_child(self, child):
        #print(child, child.expr_name, len(child.children))
        #print(child.children[0].expr_name)
        return getattr(self, 'convert_' + child.expr_name)(child)

    def convert_expr(self, expr):
        return self.convert_child(expr.children[0])

    def convert_m(self, m):
        return bach_ast.Label(m.text)

    def convert_label(self, label):
        return bach_ast.Label(label.text)

    def convert_many(self, label):
        return bach_ast.Many(label.text)

    def convert_sexp(self, sexp):
        return [self.convert_child(c.children[0].children[0]) for c in sexp.children[1].children]
    
    def convert_vector(self, sexp):
        return [bach_ast.Label('vector')] + [self.convert_child(c.children[0].children[0]) for c in sexp.children[2].children]

    def convert_dict(self, dict):
        children = [(c.children[0].children[0].children[0], c.children[0].children[4].children[0]) for c in dict.children[1:-1]]
        elements = []
        for child in children:
            elements += map(self.convert_child, child)
        return [bach_ast.Label('dict')] + elements

    def convert_quote(self, expr):
        return bach_ast.Quote(self.convert_child(expr.children[1].children[0]))

    def convert_quasiquote(self, expr):
        return bach_ast.Quasiquote(self.convert_child(expr.children[1].children[0]))

    def convert_unquote(self, expr):
        return bach_ast.Unquote(self.convert_child(expr.children[1].children[0]))

    def convert_unquotelist(self, expr):
        return  bach_ast.UnquoteList(self.convert_child(expr.children[1].children[0]))

    def convert_number(self, number):
        return self.convert_child(number.children[0])

    def convert_float(self, f):
        return bach_ast.Float(float(f.text))
  
    def convert_integer(self, integer):
        return bach_ast.Integer(int(integer.text))

    def convert_string(self, value):
        return bach_ast.String(value.text[1:-1])

    def convert_operator(self, operator):
        return bach_ast.Label(operator.text)

    def convert_boolean(self, boolean):
        return bach_ast.Boolean(boolean.text == '#t')
