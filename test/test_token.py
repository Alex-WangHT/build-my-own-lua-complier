#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Token 模块单元测试

使用方法:
    python -m pytest test/test_token.py -v
    python test/test_token.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from token import TokenType, Token, LexerRule


def get_test_cases() -> list:
    """
    获取测试用例列表
    格式: (测试名称, 测试函数)
    """
    return [
        ("TokenType枚举完整性", test_token_type_enum),
        ("Token基本创建", test_token_creation),
        ("Token字符串表示", test_token_str),
        ("Token字典转换", test_token_to_dict),
        ("LexerRule创建", test_lexer_rule_creation),
        ("TokenType值唯一性", test_token_type_unique),
        ("Token类型比较", test_token_type_comparison),
        ("Token默认值", test_token_default_values),
    ]


def test_token_type_enum() -> bool:
    """测试 TokenType 枚举是否包含必要的类型"""
    required = ['EOF', 'NUMBER', 'STRING', 'IDENTIFIER', 'BOOLEAN', 'NIL',
                'LOCAL', 'FUNCTION', 'IF', 'ELSE', 'WHILE', 'FOR', 'RETURN', 'END']
    for req in required:
        if not hasattr(TokenType, req):
            print(f"  FAIL: 缺少 TokenType: {req}")
            return False
    print(f"  PASS: TokenType 包含 {len(TokenType)} 个类型")
    return True


def test_token_creation() -> bool:
    """测试 Token 创建"""
    try:
        token = Token(TokenType.NUMBER, 42, line=1, column=5, raw="42")
        assert token.type == TokenType.NUMBER
        assert token.value == 42
        assert token.line == 1
        assert token.column == 5
        assert token.raw == "42"
        print(f"  PASS: Token 创建成功 - value={token.value}")
        return True
    except Exception as e:
        print(f"  FAIL: Token 创建失败 - {e}")
        return False


def test_token_str() -> bool:
    """测试 Token 字符串表示"""
    try:
        token = Token(TokenType.STRING, "hello", line=2, column=10)
        str_repr = str(token)
        assert "STRING" in str_repr
        assert "hello" in str_repr
        assert "2:10" in str_repr
        print(f"  PASS: Token 字符串表示正确")
        return True
    except Exception as e:
        print(f"  FAIL: Token 字符串表示失败 - {e}")
        return False


def test_token_to_dict() -> bool:
    """测试 Token 转换为字典"""
    try:
        token = Token(TokenType.IDENTIFIER, "myVar", line=3, column=1, raw="myVar")
        d = token.to_dict()
        assert d['type'] == 'IDENTIFIER'
        assert d['value'] == 'myVar'
        assert d['line'] == 3
        assert d['column'] == 1
        assert d['raw'] == 'myVar'
        print(f"  PASS: Token 字典转换正确")
        return True
    except Exception as e:
        print(f"  FAIL: Token 字典转换失败 - {e}")
        return False


def test_lexer_rule_creation() -> bool:
    """测试 LexerRule 创建"""
    try:
        def dummy_handler(text, line, col):
            return Token(TokenType.NUMBER, int(text), line, col, text)
        
        rule = LexerRule(
            name='test_number',
            pattern=r'\d+',
            handler=dummy_handler,
            priority=10
        )
        assert rule.name == 'test_number'
        assert rule.pattern == r'\d+'
        assert rule.priority == 10
        print(f"  PASS: LexerRule 创建成功 - name={rule.name}")
        return True
    except Exception as e:
        print(f"  FAIL: LexerRule 创建失败 - {e}")
        return False


def test_token_type_unique() -> bool:
    """测试 TokenType 值是否唯一"""
    try:
        values = [t.value for t in TokenType]
        assert len(values) == len(set(values))
        print(f"  PASS: TokenType 值唯一 ({len(values)} 个)")
        return True
    except Exception as e:
        print(f"  FAIL: TokenType 值不唯一 - {e}")
        return False


def test_token_type_comparison() -> bool:
    """测试 TokenType 比较"""
    try:
        t1 = TokenType.NUMBER
        t2 = TokenType.NUMBER
        t3 = TokenType.STRING
        assert t1 == t2
        assert t1 != t3
        print(f"  PASS: TokenType 比较正确")
        return True
    except Exception as e:
        print(f"  FAIL: TokenType 比较失败 - {e}")
        return False


def test_token_default_values() -> bool:
    """测试 Token 默认值"""
    try:
        token = Token(TokenType.IDENTIFIER)
        assert token.value is None
        assert token.line == 1
        assert token.column == 1
        assert token.raw == ""
        print(f"  PASS: Token 默认值正确")
        return True
    except Exception as e:
        print(f"  FAIL: Token 默认值失败 - {e}")
        return False


def run_tests() -> tuple:
    """
    运行所有测试

    Returns:
        tuple: (通过数, 失败数, 测试用例列表)
    """
    test_cases = get_test_cases()
    passed = 0
    failed = 0
    results = []

    print("=" * 60)
    print("Token 模块测试")
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

    print("\n" + "=" * 60)
    print(f"结果: 通过 {passed}, 失败 {failed}, 总计 {len(test_cases)}")
    print("=" * 60)

    return passed, failed, results


def main():
    """主函数"""
    passed, failed, _ = run_tests()
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
