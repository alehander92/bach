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
        str(self.value)

class Boolean(Node):
    def __init__(self, value):
        self.value = value

    def as_code(self):
        '#t' if self.value else '#f'


