from fractions import Fraction

'''
Some builtin functions for bach's runtime
bach_add/bach_sub etc correspond to +/-...
see bach_ast for mapping(bach converts all those labels into valid python labels)
Most of those implementations don't feel pythonic, and that's intentional
Those functions would be used frequently, so we 
try to write them more efficiently without too much magic
'''

def symbol():
    class BachSymbol(object):
        def __init__(self, value):
            self.value = value

        def __repr__(self):
            return "'%s" % self.value

        def __str__(self):
            return repr(self)

    def car(list):
        return list[0]

    def cdr(list):
        return list[1:]

    def cons(head, tail):
        return [head] + tail

    def bach_add(*values):
        return sum(values)

    def bach_sub(*values):
        if len(values) == 0:
            raise BachArgumentError("expected 1 or more got 0 args for -")
        elif len(values) == 1:
            return -values[0]
        else:
            value = values[0]
            for n in values[1:]:
                value -= n
            return value

    def display(value):
        print(value)

    def string(*values):
        result = ''
        for value in values:
            result += value
        return result

    def bach_eq(*values):
        if len(values) == 0:
            raise BachArgumentError("expected 1 or more got 0 args for =")
        first = values[0]
        for value in values[1:]:
            if value != first:
                return False
        return True

    def bach_neq(*values):
        if len(values) == 0:
            raise BachArgumentError("expected 1 or more got 0 args for !=")
        first = values[0]
        for value in values[1:]:
            if value != first:
                return True
        return False

    def bach_gt(*values):
        if len(values) == 0:
            raise BachArgumentError("expected 1 or more got 0 args for >")
        current = values[0]
        for value in values[1:]:
            if current <= value:
                return False
            current = value
        return True

    def bach_lt(*values):
        if len(values) == 0:
            raise BachArgumentError("expected 1 or more got 0 args for =")
        current = values[0]
        for value in values[1:]:
            if current >= value:
                return False
            current = value
        return True

    def bach_mult(*values):
        value = 1
        for n in values:
            value *= n
        return value

    def bach_div(*values):
        if len(values) == 0:
            raise BachArgumentError("expected 1 or more got 0 args for /")
        elif len(values) == 1:
            if isinstance(values[0], (int, Fraction)):
                return Fraction(1, values[0])
            else:
                return 1 / values[0]
        else:
            value = values[0]
            for d in values[1:]:
                if isinstance(value, (int, Fraction)) and isinstance(d, (int, Fraction)):
                    return Fraction(value, d)
                else:
                    return value / d

    return BachSymbol

__all__ = ['car', 'cdr', 'cons', 'bach_add', 'bach_sub', 'bach_mult', 'bach_div', 'display', 'symbol']



# e? -> is_e

# + bach_add
# - bach_sub
# * bach_mult
# / bach_div
# > bach_gt
# < bach_lt
# = bach_eq
# >= bach_gte
# != bach_ne
# <= bach_lte
# and bach_and
