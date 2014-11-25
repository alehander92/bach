class Node(object):
    pass

class Label(Node):
    def __init__(self, label):
        self.label = self.as_python_label(label)

    def as_python_label(self, label):
        if label in self.OPERATOR_PYTHON_LABELS:
            return self.OPERATOR_PYTHON_LABELS[label]

        converted = label.replace('-', '_')
        if converted.endswith('?'):
            converted = 'is_%s' % converted[:-1]

        return converted
    
    def as_code(self):
        return self.label
    
    OPERATOR_PYTHON_LABELS = {
        '+' : 'bach_add',
        '-' : 'bach_sub',
        '*' : 'bach_mult',
        '/' : 'bach_div',
        '>' : 'bach_gt',
        '<' : 'bach_lt',
        '=' : 'bach_eq',
        '>=' : 'bach_gte',
        '!=' : 'bach_ne',
        '<=' : 'bach_lte',
        'and' : 'bach_and',
    }
    

class Number(Node):
    def __init__(self, value):
        self.value = value

    def as_code(self):
        return str(self.value)

class Float(Number):
    pass

class Integer(Number):
    pass

class String(Node):
    def __init__(self, value):
        self.value = value

    def as_code(self):
        return '"%s"' % self.value

class Boolean(Node):
    def __init__(self, value):
        self.value = value

    def as_code(self):
        return '#t' if self.value else '#f'


class Function(Node):
    def __init__(self, label, args, body):
        self.label, self.args, self.body = label, args, body

    def as_code(self, depth=0):
        return '(define %s (%s)\n  %s)' % (
            self.label.as_code(),
            ', '.join([arg.as_code() for arg in self.args]),
            '\n'.join([child.as_code(depth + 1) for child in self.body]))

class Do(Node):
    def __init__(self, body):
        self.body = body

    def as_code(self, depth=0):
        return '%s(do %s)' % ('  ' * depth, ' '.join([child.as_code() for child in self.body]))

class Vector(Node):
    def __init__(self, values):
        self.values = values

    def as_code(self, depth=0):
        return '%s#(%s)' % ('  ' * depth, ' '.join([w.as_code() for w in self.values]))

class Import(Node):
    def __init__(self, modules):
        self.modules = modules

    def as_code(self, depth=0):
        return '%s(import %s)' % ('  ' * depth, ' '.join([child.as_code() for child in self.values]))

class Set(Node):
    def __init__(self, values):
        self.values = values

    def as_code(self, depth=0):
        return '%s(set %s)' % ('  ' * depth, ' '.join([child.as_code() for child in self.values]))

class Dict(Node):
    def __init__(self, keys, values):
        self.keys, self.values = keys, values

    def as_code(self, depth=0):
        return '%s{%s}' % ('  ' * depth, ' '.join(['%s : %s' % map(pair, lambda a: a.as_code()) for pair in zip(self.keys, self.values)]))

class List(Node):
    def __init__(self, values):
        self.values = values

    def as_code(self, depth=0):
        return '%s\'(%s)' % ('  ' * depth, ' '.join([value.as_code() for value in self.values]))

class Call(Node):
    def __init__(self, handler, args):
        self.handler, self.args = handler, args

    def as_code(self, depth=0):
        return '(%s %s)' % (self.handler.as_code(), ' '.join([arg.as_code() for arg in self.args]))

class Cond(Node):
    def __init__(self, tests, results):
        self.tests, self.results = tests, results

    def as_code(self, depth=0):
        return '(cond\n%s\n%s)' % (
            '\n'.join(['%s(%s %s)' % ('  ' * (depth + 1), self.tests[i].as_code(), self.results[i].as_code()) for i in range(len(self.tests))]),
            '%s%s' % ('  ' * (depth + 1), self.results[-1].as_code()))

class If(Node):
    def __init__(self, test, if_true, if_false):
        self.test, self.if_true, self.if_false = test, if_false, if_false

    def as_code(self, depth=0):
        return '(if %s %s %s)' % (self.test.as_code(), self.if_true.as_code(), self.if_false.as_code())

class Define(Node):
    def __init__(self, label, value):
        self.label, self.value = label, value

    def as_code(self, depth=0):
        return '(define %s %s)' % (self.label.as_code(), self.value.as_code())


class Let(Node):
    '''
    Represents (let (label value..) body..)
    We can implement let as a macro with nested lambdas, but we prefer to compile them to more efficient bytecode
    '''
    def __init__(self, aliases, body):
        self.aliases, self.body = aliases, body


class Lambda(Node):
    def __init__(self, args, body):
        self.args, self.body = args, body

    def as_code(self, depth=0):
        return '%s(lambda (%s) %s)' % ('  ' * depth, ' '.join([arg.as_code() for arg in self.args]), ' '.join([v.as_code() for v in self.body]))

class Quote(Node):
    def __init__(self, expr):
        self.expr = expr

    def as_code(self, depth=0):
        return '%s\'%s' % ('  ' * depth, self.expr.as_code())

class Quasiquote(Node):
    def __init__(self, expr):
        self.expr = expr

    def as_code(self, depth=0):
        return '%s`%s' % ('  ' * depth, self.expr.as_code())

class Unquote(Node):
    def __init__(self, expr):
        self.expr = expr

    def as_code(self, depth=0):
        return '%s ~%s' % ('  ' * depth, self.expr.as_code())

class UnquoteList(Node):
    def __init__(self, expr):
        self.expr = expr

    def as_code(self, depth=0):
        return '%s ~@%s' % ('  ' * depth, self.expr.as_code())


class Program(Node):
    def __init__(self, code):
        self.code = code

    def as_code(self, depth=0):
        return '\n'.join([c.as_code() for c in self.code]) + '\n'

def find_outer_labels(sexp, fast):
    if isinstance(sexp, (list, tuple)):
        return reduce(lambda l, r: l | r, [find_outer_labels(s, fast) for s in sexp], set([]))
    elif isinstance(sexp, Label):
        if sexp.label not in fast:
            return {sexp.label}
        else:
            return set([])
    elif isinstance(sexp, Node):
        return reduce(lambda l, r: l | r, [find_outer_labels(s, fast) for s in sexp.__dict__.values()], set([]))
    else:
        return set([])

