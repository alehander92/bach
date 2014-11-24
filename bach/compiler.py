import marshal
import time
import generator

class Compiler(object):
    MAGIC_PYTHON = '\x03\xf3\r\n'

    def compile(self, sexp, stl=None):
        '''
        return the content
        of a pyc file
        '''
        g = generator.Generator()
        code = g.generate_module(sexp, stl=stl)
        return '%s%s%s' % (
            self.MAGIC_PYTHON,
            self.compile_timestamp(),
            marshal.dumps(code))

    def compile_and_save(self, sexp, filename, stl=None):
        c = self.compile(sexp, stl)
        with open(filename, 'wb') as f:
            f.write(c)

    def compile_timestamp(self):
        return marshal.dumps(int(time.time()))[1:]

    def compile_and_eval(self, sexp, stl=None):
        g = generator.Generator()
        code = g.generate_module(sexp, stl=stl)
        return eval(code.to_code())
