import byteplay
import functions

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
