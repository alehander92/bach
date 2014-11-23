from fractions import Fraction

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
