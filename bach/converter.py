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
        # print(label)

    def convert_sexp(self, sexp):
        return [self.convert_child(c.children[0].children[0]) for c in sexp.children[1].children]
    
    def convert_quote(self, expr):
        return bach_ast.Quote(self.convert_child(expr.children[1].children[0]))

    def convert_number(self, number):
        return self.convert_child(number.children[0])

    def convert_integer(self, integer):
        return bach_ast.Integer(int(integer.text))

    def convert_float(self, f):
        return bach_ast.Float(float(f.text))

    def convert_operator(self, operator):
        return bach_ast.Label(operator.text)

    def convert_boolean(self, boolean):
        return bach_ast.Boolean(boolean.text == '#t')
