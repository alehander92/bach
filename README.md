# bach

a lisp dialect that compiles to cpython bytecode.

'cause it's fun.

currently targeting cpython 2.7

# status

dirty but working in the base case macros

```scheme
(macro function (label args &body)
    `(define ~label (fn ~args ~body)))
```

`define`, `if`, `let`, `fn`(`lambda`), `function`(`define` for functions), lists, dicts, sets, some stl

```scheme
{2 : "4"}
'(a b)
(define d 2)
#(d 4)
(let (a 2 b a) a)
(define a 2)
(define add-to 
    (fn (e)
        (fn (z) (+ a z))))
(display ((add-to 4) 2))

```