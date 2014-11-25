import os
import byteplay
import functions

CURRENT_FILE_DIR = '.'

def load_stl():
    codes = []
    opcode = None
    opcode = byteplay.Code.from_code(functions.symbol.func_code)
    new_code = []
    for value in opcode.code:
        if value[0] == byteplay.STORE_FAST:
            new_code.append((byteplay.STORE_GLOBAL, value[1]))
        elif value[0] != byteplay.SetLineno:
            new_code.append(value)
    opcode.code = byteplay.CodeList(new_code[:-2])
    return opcode

def include(*filenames):
    result = []
    for filename in filenames:
        with open(os.path.join(CURRENT_FILE_DIR, filename + '.bach'), 'r') as f:
            result.append(f.read())
    return '\n'.join(result)


