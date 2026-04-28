#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Token 模块 - 定义 Token 类型和 Token 类
用于 Lua 解释器的词法分析

使用方法:
    python src/token.py              # 运行单元测试
    python src/token.py -t           # 运行测试
    python src/token.py -c "test"    # 测试特定功能
"""

import sys
import argparse
from enum import Enum, auto
from typing import Any, Optional, Callable


class TokenType(Enum):
    """Token类型枚举 - 可扩展"""
    EOF = auto()
    UNKNOWN = auto()
    
    KEYWORD = auto()
    IDENTIFIER = auto()
    
    NUMBER = auto()
    STRING = auto()
    BOOLEAN = auto()
    NIL = auto()
    
    OP_PLUS = auto()
    OP_MINUS = auto()
    OP_MULT = auto()
    OP_DIV = auto()
    OP_MOD = auto()
    OP_POW = auto()
    OP_CONCAT = auto()
    
    OP_EQ = auto()
    OP_NE = auto()
    OP_LT = auto()
    OP_GT = auto()
    OP_LE = auto()
    OP_GE = auto()
    
    OP_AND = auto()
    OP_OR = auto()
    OP_NOT = auto()
    
    ASSIGN = auto()
    
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    
    COMMA = auto()
    SEMICOLON = auto()
    COLON = auto()
    DOT = auto()
    DOUBLE_DOT = auto()
    
    TABLE_START = auto()
    TABLE_END = auto()
    
    FUNCTION = auto()
    RETURN = auto()
    
    IF = auto()
    ELSE = auto()
    ELSEIF = auto()
    THEN = auto()
    END = auto()
    WHILE = auto()
    DO = auto()
    FOR = auto()
    IN = auto()
    REPEAT = auto()
    UNTIL = auto()
    BREAK = auto()
    
    LOCAL = auto()
    COMMENT = auto()


class Token:
    """Token类 - 表示一个词法单元"""
    
    def __init__(self, token_type: TokenType, value: Any = None, 
                 line: int = 1, column: int = 1, raw: str = ""):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column
        self.raw = raw or str(value) if value is not None else ""
    
    def __repr__(self) -> str:
        return f"Token({self.type.name}, {repr(self.value)}, line={self.line}, col={self.column})"
    
    def __str__(self) -> str:
        value_str = repr(self.value) if self.value is not None else "None"
        return f"[Line {self.line}:{self.column}] {self.type.name:20} = {value_str}"
    
    def to_dict(self) -> dict:
        """转换为字典，用于测试输出"""
        return {
            'type': self.type.name,
            'value': self.value,
            'line': self.line,
            'column': self.column,
            'raw': self.raw
        }


class LexerRule:
    """词法规则类 - 用于扩展词法分析器"""
    
    def __init__(self, name: str, pattern: str, 
                 handler: Optional[Callable[[str, int, int], Optional[Token]]] = None,
                 token_type: Optional[TokenType] = None,
                 priority: int = 0):
        self.name = name
        self.pattern = pattern
        self.handler = handler
        self.token_type = token_type
        self.priority = priority
    
    def __repr__(self) -> str:
        return f"LexerRule('{self.name}', '{self.pattern}')"


def get_test_cases() -> list:
    """
    获取测试用例 - 方便扩展
    格式: (测试名称, 测试函数, 预期结果)
    """
    return [
        ("TokenType枚举完整性", test_token_type_enum, True),
        ("Token基本创建", test_token_creation, True),
        ("Token字符串表示", test_token_str, True),
        ("Token字典转换", test_token_to_dict, True),
        ("LexerRule创建", test_lexer_rule_creation, True),
        ("TokenType值唯一性", test_token_type_unique, True),
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


def run_tests() -> int:
    """运行所有测试"""
    print("=" * 60)
    print("Token 模块单元测试")
    print("=" * 60)
    
    test_cases = get_test_cases()
    passed = 0
    failed = 0
    
    for name, test_func, _ in test_cases:
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
    print(f"结果: 通过 {passed}, 失败 {failed}, 总计 {len(test_cases)}")
    print(f"{'='*60}")
    
    return 0 if failed == 0 else 1


def main():
    """CLI入口点"""
    parser = argparse.ArgumentParser(
        description='Token 模块 - Lua 词法单元定义',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python src/token.py     # 运行测试
  python src/token.py -t  # 运行测试
        """
    )
    
    parser.add_argument(
        '-t', '--test',
        action='store_true',
        help='运行单元测试（默认行为）'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Token Module v1.0'
    )
    
    args = parser.parse_args()
    return run_tests()


if __name__ == "__main__":
    sys.exit(main())
