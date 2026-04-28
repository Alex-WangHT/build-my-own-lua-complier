#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单元测试 - 测试 Token 模块和 Lexer 模块

使用方法:
    python test.py              # 运行所有测试
    python test.py -t           # 运行所有测试
    python test.py -m token     # 只测试 token 模块
    python test.py -m lexer     # 只测试 lexer 模块
    python test.py -c "local x = 10"  # 分析代码
    python test.py -i           # 交互式模式
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from token import TokenType, Token, LexerRule
from lexer import Lexer


# ============================================================================
# Token 模块测试用例
# ============================================================================

def get_token_test_cases() -> list:
    """
    获取 Token 模块测试用例
    格式: (测试名称, 测试函数)
    """
    return [
        ("TokenType枚举完整性", test_token_type_enum),
        ("Token基本创建", test_token_creation),
        ("Token字符串表示", test_token_str),
        ("Token字典转换", test_token_to_dict),
        ("LexerRule创建", test_lexer_rule_creation),
        ("TokenType值唯一性", test_token_type_unique),
    ]


def test_token_type_enum() -> bool:
    """测试TokenType枚举是否包含必要的类型"""
    required = ['EOF', 'NUMBER', 'STRING', 'IDENTIFIER', 'BOOLEAN', 'NIL']
    for req in required:
        if not hasattr(TokenType, req):
            print(f"  ✗ 缺少 TokenType: {req}")
            return False
    print(f"  ✓ TokenType 包含 {len(TokenType)} 个类型")
    return True


def test_token_creation() -> bool:
    """测试Token创建"""
    try:
        token = Token(TokenType.NUMBER, 42, line=1, column=5, raw="42")
        assert token.type == TokenType.NUMBER
        assert token.value == 42
        assert token.line == 1
        assert token.column == 5
        assert token.raw == "42"
        print("  ✓ Token 创建成功")
        return True
    except Exception as e:
        print(f"  ✗ Token 创建失败: {e}")
        return False


def test_token_str() -> bool:
    """测试Token字符串表示"""
    try:
        token = Token(TokenType.STRING, "hello", line=2, column=10)
        str_repr = str(token)
        assert "STRING" in str_repr
        assert "hello" in str_repr
        assert "2:10" in str_repr
        print("  ✓ Token 字符串表示正确")
        return True
    except Exception as e:
        print(f"  ✗ Token 字符串表示失败: {e}")
        return False


def test_token_to_dict() -> bool:
    """测试Token转换为字典"""
    try:
        token = Token(TokenType.IDENTIFIER, "x", line=3, column=1, raw="x")
        d = token.to_dict()
        assert d['type'] == 'IDENTIFIER'
        assert d['value'] == 'x'
        assert d['line'] == 3
        assert d['column'] == 1
        print("  ✓ Token 字典转换正确")
        return True
    except Exception as e:
        print(f"  ✗ Token 字典转换失败: {e}")
        return False


def test_lexer_rule_creation() -> bool:
    """测试LexerRule创建"""
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
        print("  ✓ LexerRule 创建成功")
        return True
    except Exception as e:
        print(f"  ✗ LexerRule 创建失败: {e}")
        return False


def test_token_type_unique() -> bool:
    """测试TokenType值是否唯一"""
    try:
        values = [t.value for t in TokenType]
        assert len(values) == len(set(values))
        print(f"  ✓ TokenType 值唯一 ({len(values)} 个)")
        return True
    except Exception as e:
        print(f"  ✗ TokenType 值不唯一: {e}")
        return False


# ============================================================================
# Lexer 模块测试用例
# ============================================================================

def get_lexer_test_cases() -> list:
    """
    获取 Lexer 模块测试用例
    格式: (测试名称, 源代码, 预期Token类型列表)
    """
    return [
        ("变量定义", "local x = 10", [TokenType.LOCAL, TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.NUMBER]),
        ("字符串", 'local s = "hello"', [TokenType.LOCAL, TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.STRING]),
        ("布尔值", "local flag = true", [TokenType.LOCAL, TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.BOOLEAN]),
        ("nil值", "local n = nil", [TokenType.LOCAL, TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.NIL]),
        ("运算符", "a + b * c", [TokenType.IDENTIFIER, TokenType.OP_PLUS, TokenType.IDENTIFIER, TokenType.OP_MULT, TokenType.IDENTIFIER]),
        ("比较运算符", "x == y", [TokenType.IDENTIFIER, TokenType.OP_EQ, TokenType.IDENTIFIER]),
        ("函数定义", "function add() end", [TokenType.FUNCTION, TokenType.IDENTIFIER, TokenType.LPAREN, TokenType.RPAREN, TokenType.END]),
    ]


# ============================================================================
# 测试运行函数
# ============================================================================

def run_token_tests() -> tuple:
    """运行 Token 模块测试"""
    print("=" * 60)
    print("Token 模块测试")
    print("=" * 60)
    
    test_cases = get_token_test_cases()
    passed = 0
    failed = 0
    
    for name, test_func in test_cases:
        print(f"\n测试: {name}")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ✗ 异常: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Token 测试结果: 通过 {passed}, 失败 {failed}")
    print(f"{'='*60}")
    
    return passed, failed


def run_lexer_tests() -> tuple:
    """运行 Lexer 模块测试"""
    print("=" * 60)
    print("Lexer 模块测试")
    print("=" * 60)
    
    lexer = Lexer()
    test_cases = get_lexer_test_cases()
    passed = 0
    failed = 0
    
    for name, source, expected_types in test_cases:
        print(f"\n测试: {name}")
        try:
            tokens = lexer.tokenize(source)
            actual_types = [t.type for t in tokens if t.type != TokenType.EOF]
            
            if actual_types == expected_types:
                print(f"  ✓ 通过 ({len(tokens)} 个Token)")
                passed += 1
            else:
                print(f"  ✗ 失败")
                print(f"    预期: {[t.name for t in expected_types]}")
                print(f"    实际: {[t.name for t in actual_types]}")
                failed += 1
                
        except Exception as e:
            print(f"  ✗ 异常: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Lexer 测试结果: 通过 {passed}, 失败 {failed}")
    print(f"{'='*60}")
    
    return passed, failed


def analyze_code(source: str):
    """分析代码并显示结果"""
    lexer = Lexer()
    tokens = lexer.tokenize(source)
    
    print(f"\n输入: {repr(source)}")
    print(f"Token数: {len(tokens)}")
    for i, token in enumerate(tokens):
        print(f"  {i+1:2d}. {token}")
    
    return tokens


def interactive_mode():
    """交互式模式"""
    print("=" * 60)
    print("Lua Lexer 测试 - 交互式模式")
    print("=" * 60)
    print("输入代码进行分析，输入 'quit' 退出")
    
    while True:
        try:
            user_input = input("\n>>> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ('quit', 'exit', 'q'):
                print("再见!")
                break
            
            analyze_code(user_input)
            
        except KeyboardInterrupt:
            print("\n再见!")
            break
        except EOFError:
            print("\n再见!")
            break


# ============================================================================
# 主函数
# ============================================================================

def main():
    """CLI入口点"""
    parser = argparse.ArgumentParser(
        description='Lua 解释器单元测试',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python test.py              # 运行所有测试
  python test.py -t           # 运行所有测试
  python test.py -m token     # 只测试 token 模块
  python test.py -m lexer     # 只测试 lexer 模块
  python test.py -c "local x = 10"  # 分析代码
  python test.py -i           # 交互式模式
        """
    )
    
    parser.add_argument(
        '-t', '--test',
        action='store_true',
        help='运行所有测试（默认行为）'
    )
    
    parser.add_argument(
        '-m', '--module',
        type=str,
        choices=['token', 'lexer'],
        metavar='MODULE',
        help='指定测试模块: token 或 lexer'
    )
    
    parser.add_argument(
        '-c', '--code',
        type=str,
        metavar='CODE',
        help='分析指定的Lua代码'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='进入交互式模式'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Lua Test v1.0'
    )
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
        return 0
    elif args.code:
        analyze_code(args.code)
        return 0
    elif args.module == 'token':
        passed, failed = run_token_tests()
        return 0 if failed == 0 else 1
    elif args.module == 'lexer':
        passed, failed = run_lexer_tests()
        return 0 if failed == 0 else 1
    else:
        # 默认运行所有测试
        print("=" * 60)
        print("运行所有单元测试")
        print("=" * 60)
        
        token_passed, token_failed = run_token_tests()
        lexer_passed, lexer_failed = run_lexer_tests()
        
        total_passed = token_passed + lexer_passed
        total_failed = token_failed + lexer_failed
        
        print("\n" + "=" * 60)
        print("总测试结果")
        print("=" * 60)
        print(f"Token 模块: 通过 {token_passed}, 失败 {token_failed}")
        print(f"Lexer 模块: 通过 {lexer_passed}, 失败 {lexer_failed}")
        print(f"总计: 通过 {total_passed}, 失败 {total_failed}")
        print("=" * 60)
        
        if total_failed == 0:
            print("\n🎉 所有测试通过!")
            return 0
        else:
            print(f"\n❌ 有 {total_failed} 个测试失败")
            return 1


if __name__ == "__main__":
    sys.exit(main())
