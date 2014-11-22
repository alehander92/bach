# -*- encoding: utf-8 -*-
from nose.tools import assert_equal, assert_not_equal, assert_raises, assert_is_instance
from bach_ast import Node, Label, Number, Function

class TestLabel(object):
    def test_init(self):
        label = Label('e')
        assert_equal(label.label, 'e')

    def test_convert_to_valid_python_labels(self):
        z = Label('e?').as_python_label()
        assert_equal(z, 'is_e')

        translated = Label('f-x').as_python_label()
        assert_equal(translated, 'f_x')

class TestNumber(object):
    def test_code_representation(self):
        number = Number(-2)
        assert_equal(number.as_code(), '-2')

class TestFunction(object):
    def test_code_representation(self):
        function = Function(Label('e?'), [Label('f')], [Number(0)])
        assert_equal(function.as_code(), '(define e? (f)\n  0)')


