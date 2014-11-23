import grammar, converter

class Parser(object):
    def __init__(self, source):
        if isinstance(source, list):
            source = source.join('\n')

        self.source = source

    def parse(self):
        # invoke the parser generator
        # convert the result tree to bach_ast
        parsed = grammar.BachGrammar.parse(self.source)
        return converter.Converter().convert(parsed)
