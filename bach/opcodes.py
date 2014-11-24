class Opcodes(object):
    '''
    a collection of cpython opcodes
    for cleaner opcode comprehensions in generator
    '''

    def __init__(self, *values):
        self.values = []
        for value in values:
            if isinstance(value, list):
                data = Opcodes(*value)
                self.values += data.to_list()
            elif isinstance(value, Opcodes):
                self.values += value.to_list()
            else:
                self.values.append(value)

    def to_list(self):
        return self.values
