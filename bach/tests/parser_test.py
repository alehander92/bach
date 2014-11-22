# -*- encoding: utf-8 -*-
from nose.tools import assert_equal, assert_not_equal, assert_raises, assert_is_instance
from parser import Parser

class TestParser(object):
    def test_init(self):
        parser = Parser('4')
        assert_equal(parser.source, '4')
        assert_not_equal(parser.target, '3')

    def test_parse_labels(self):
        ast = Parser('l\nm?\nweird-name\nname_я').parse()
        assert_is_instance(ast.body[0], bach_ast.Label)
        assert_equal(ast.body[0].label, 'l')
        assert_equal(ast.body[1].label, 'm?')
        assert_equal(ast.body[2].label, 'weird-name')
        assert_equal(ast.body[3].label, 'name_я')

