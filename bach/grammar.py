from parsimonious import Grammar, NodeVisitor
import bach_ast

BachGrammar = Grammar('''
p = (expr ws?)*
expr = number / boolean / string / label / sexp / quote
number = float / integer
float = ~"[0-9]+"i "." ~"[0-9]+"i
integer = ~"[0-9]+"i
label = operator / m
operator = ">=" / "!=" / "<=" / "=" / "<" / ">" / "+" / "-" / "/"
m = ~"[a-zA-Z\-\?]+"i
boolean = '#t' / '#f'
string = "\\"" t "\\""
t = ~"[^\\"]*"i
sexp = lp (expr ws?)* rp
quote = "'" expr
lp = "("
rp = ")"
ws = ~"[ \\t\\n]+"i
nl = ~"\\n+"i
''')

# e = bach.parse('''(define filter (test list)
#   (cond
#     ((null? list)
#       list)
#     ((test (head list))
#       (cons (head list) (filter test (tail list))))
#     (filter test (tail list))))
# (define pos? (num) (> num 0))

# (filter pos? '(2 3 -2.2))
# ''')