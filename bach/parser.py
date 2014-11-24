import grammar, converter

class Parser(object):
    def __init__(self, source):
        if isinstance(source, list):
        	lines = source
        else:
        	lines = source.split('\n')
        lines = [line for line in lines if not line.startswith(';')]
        print(lines, source)
        self.source = '\n'.join(lines)

    def parse(self):
        # invoke the parser generator
        # convert the result tree to bach_ast
        parsed = grammar.BachGrammar.parse(self.source)
        return converter.Converter().convert(parsed)
