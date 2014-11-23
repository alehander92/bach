class Node(object):
    pass

class Label(Node):
    def __init__(self, label):
        self.label = label

    def as_python_label(self):
        converted = self.label.replace('-', '_')
        if converted.endswith('?'):
            converted = 'is_%s' % converted[:-1]
        return converted
    
    def as_code(self):
        return self.label

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

class Quote(Node):
    def __init__(self, ast):
        self.ast = ast

    def as_code(self, depth=0):
        return '%s\'%s' % ('  ' * depth, self.ast.as_code())

class Program(Node):
    def __init__(self, code):
        self.code = code

    def as_code(self, depth=0):
        return '\n'.join([c.as_code() for c in self.code]) + '\n'
