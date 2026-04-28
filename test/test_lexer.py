#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lexer 模块单元测试

使用方法:
    python -m pytest test/test_lexer.py -v
    python test/test_lexer.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from lexer import Lexer
from token import TokenType, Token, LexerRule


def get_test_cases() -> list:
    """
    获取测试用例列表
    格式: (测试名称, 源代码, 预期Token类型列表)
    """
    return [
        ("变量定义", "local x = 10", 
         [TokenType.LOCAL, TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.NUMBER]),
        
        ("字符串", 'local s = "hello"', 
         [TokenType.LOCAL, TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.STRING]),
        
        ("布尔值", "local flag = true", 
         [TokenType.LOCAL, TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.BOOLEAN]),
        
        ("nil值", "local n = nil", 
         [TokenType.LOCAL, TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.NIL]),
        
        ("算术运算符", "a + b * c", 
         [TokenType.IDENTIFIER, TokenType.OP_PLUS, TokenType.IDENTIFIER, 
          TokenType.OP_MULT, TokenType.IDENTIFIER]),
        
        ("比较运算符", "x == y", 
         [TokenType.IDENTIFIER, TokenType.OP_EQ, TokenType.IDENTIFIER]),
        
        ("不等于运算符", "x ~= y", 
         [TokenType.IDENTIFIER, TokenType.OP_NE, TokenType.IDENTIFIER]),
        
        ("函数定义", "function add() end", 
         [TokenType.FUNCTION, TokenType.IDENTIFIER, TokenType.LPAREN, 
          TokenType.RPAREN, TokenType.END]),
        
        ("数字", "42", [TokenType.NUMBER]),
        
        ("浮点数", "3.14159", [TokenType.NUMBER]),
        
        ("十六进制", "0xFF", [TokenType.NUMBER]),
        
        ("科学计数法", "1e-5", [TokenType.NUMBER]),
        
        ("字符串连接", '"Hello" .. "World"', 
         [TokenType.STRING, TokenType.OP_CONCAT, TokenType.STRING]),
        
        ("注释跳过", "-- This is a comment\nlocal x = 1", 
         [TokenType.LOCAL, TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.NUMBER]),
        
        ("表构造", "{1, 2, 3}", 
         [TokenType.LBRACE, TokenType.NUMBER, TokenType.COMMA, 
          TokenType.NUMBER, TokenType.COMMA, TokenType.NUMBER, TokenType.RBRACE]),
    ]


def get_advanced_test_cases() -> list:
    """
    获取高级测试用例列表
    格式: (测试名称, 测试函数)
    """
    return [
        ("Lexer初始化", test_lexer_init),
        ("Token位置信息", test_token_position),
        ("规则添加移除", test_rule_management),
        ("未知字符处理", test_unknown_char),
        ("空字符串", test_empty_source),
        ("多行代码", test_multiline_source),
    ]


def test_lexer_init() -> bool:
    """测试 Lexer 初始化"""
    try:
        lexer = Lexer()
        assert lexer.source == ""
        assert lexer.pos == 0
        assert lexer.line == 1
        assert len(lexer.rules) > 0
        
        lexer2 = Lexer("local x = 10")
        assert lexer2.source == "local x = 10"
        print(f"  PASS: Lexer 初始化正确")
        return True
    except Exception as e:
        print(f"  FAIL: Lexer 初始化失败 - {e}")
        return False


def test_token_position() -> bool:
    """测试 Token 位置信息"""
    try:
        lexer = Lexer("local x = 10")
        tokens = lexer.tokenize()
        
        assert tokens[0].line == 1
        assert tokens[0].column == 1
        assert tokens[1].line == 1
        assert tokens[1].column == 7
        print(f"  PASS: Token 位置信息正确")
        return True
    except Exception as e:
        print(f"  FAIL: Token 位置信息失败 - {e}")
        return False


def test_rule_management() -> bool:
    """测试规则添加和移除"""
    try:
        lexer = Lexer()
        initial_count = len(lexer.rules)
        
        def custom_handler(text, line, col):
            return Token(TokenType.IDENTIFIER, text, line, col, text)
        
        custom_rule = LexerRule(
            name='custom_rule',
            pattern=r'@\w+',
            handler=custom_handler,
            priority=15
        )
        
        lexer.add_rule(custom_rule)
        assert len(lexer.rules) == initial_count + 1
        
        lexer.remove_rule('custom_rule')
        assert len(lexer.rules) == initial_count
        
        print(f"  PASS: 规则管理正确")
        return True
    except Exception as e:
        print(f"  FAIL: 规则管理失败 - {e}")
        return False


def test_unknown_char() -> bool:
    """测试未知字符处理"""
    try:
        lexer = Lexer("@")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.UNKNOWN
        print(f"  PASS: 未知字符处理正确")
        return True
    except Exception as e:
        print(f"  FAIL: 未知字符处理失败 - {e}")
        return False


def test_empty_source() -> bool:
    """测试空源代码"""
    try:
        lexer = Lexer("")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF
        print(f"  PASS: 空源代码处理正确")
        return True
    except Exception as e:
        print(f"  FAIL: 空源代码处理失败 - {e}")
        return False


def test_multiline_source() -> bool:
    """测试多行源代码"""
    try:
        source = """local x = 1
local y = 2"""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        lines = [t.line for t in tokens if t.type != TokenType.EOF]
        assert 1 in lines
        assert 2 in lines
        print(f"  PASS: 多行代码处理正确")
        return True
    except Exception as e:
        print(f"  FAIL: 多行代码处理失败 - {e}")
        return False


def run_basic_tests() -> tuple:
    """
    运行基础测试用例

    Returns:
        tuple: (通过数, 失败数, 测试用例列表)
    """
    lexer = Lexer()
    test_cases = get_test_cases()
    passed = 0
    failed = 0
    results = []

    print("=" * 60)
    print("Lexer 基础测试")
    print("=" * 60)

    for name, source, expected_types in test_cases:
        print(f"\n测试: {name}")
        try:
            tokens = lexer.tokenize(source)
            actual_types = [t.type for t in tokens if t.type != TokenType.EOF]

            if actual_types == expected_types:
                print(f"  PASS: 通过 ({len(tokens)} 个Token)")
                passed += 1
                results.append((name, True))
            else:
                print(f"  FAIL: 失败")
                print(f"    预期: {[t.name for t in expected_types]}")
                print(f"    实际: {[t.name for t in actual_types]}")
                failed += 1
                results.append((name, False))

        except Exception as e:
            print(f"  FAIL: 异常 - {e}")
            failed += 1
            results.append((name, False))

    return passed, failed, results


def run_advanced_tests() -> tuple:
    """
    运行高级测试用例

    Returns:
        tuple: (通过数, 失败数, 测试用例列表)
    """
    test_cases = get_advanced_test_cases()
    passed = 0
    failed = 0
    results = []

    print("\n" + "=" * 60)
    print("Lexer 高级测试")
    print("=" * 60)

    for name, test_func in test_cases:
        print(f"\n测试: {name}")
        try:
            if test_func():
                passed += 1
                results.append((name, True))
            else:
                failed += 1
                results.append((name, False))
        except Exception as e:
            print(f"  FAIL: 异常 - {e}")
            failed += 1
            results.append((name, False))

    return passed, failed, results


def run_tests() -> tuple:
    """
    运行所有测试

    Returns:
        tuple: (通过数, 失败数, 测试用例列表)
    """
    basic_passed, basic_failed, basic_results = run_basic_tests()
    advanced_passed, advanced_failed, advanced_results = run_advanced_tests()

    total_passed = basic_passed + advanced_passed
    total_failed = basic_failed + advanced_failed
    total_tests = len(get_test_cases()) + len(get_advanced_test_cases())

    print("\n" + "=" * 60)
    print(f"总测试结果")
    print("=" * 60)
    print(f"基础测试: 通过 {basic_passed}, 失败 {basic_failed}")
    print(f"高级测试: 通过 {advanced_passed}, 失败 {advanced_failed}")
    print(f"总计: 通过 {total_passed}, 失败 {total_failed}, 总计 {total_tests}")
    print("=" * 60)

    return total_passed, total_failed, basic_results + advanced_results


def main():
    """主函数"""
    passed, failed, _ = run_tests()
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
