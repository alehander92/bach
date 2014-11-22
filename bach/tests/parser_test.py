# -*- encoding: utf-8 -*-
from nose.tools import assert_equal, assert_not_equal, assert_raises, assert_is_instance
from parser import Parser

class TestParser(object):
    def test_init(self):
        parser = Parser('4')
        assert_equal(parser.source, '4')
        assert_not_equal(parser.target, '3')

    def test_parse_labels(self):
        ast = Parser(['l', 'm?', 'weird-name', 'name_я']).parse()
        assert_is_instance(ast.body[0], bach_ast.Label)
        assert_equal(ast.body[0].label, 'l')
        assert_equal(ast.body[1].label, 'm?')
        assert_equal(ast.body[2].label, 'weird-name')
        assert_equal(ast.body[3].label, 'name_я')

    def test_parse_booleans(self):
        ast = Parser(['#t', '#f']).parse()
        assert_equal(ast.body[0].value, True)
        assert_equal(ast.body[1].value, False)
    
    def test_parse_numbers(self):
        ast = Parser(['2', '-0.3', '2.2']).parse()
        assert_equal(ast.body[0].value, 2)
        assert_equal(ast.body[1].value, -0.3)
        assert_equal(ast.body[2].value, 2.2)
