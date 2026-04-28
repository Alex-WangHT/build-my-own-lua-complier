#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lexer 模块 - Lua 词法分析器
用于将 Lua 源代码转换为 Token 流

使用方法:
    python src/lexer.py              # 运行测试
    python src/lexer.py -t           # 运行测试
    python src/lexer.py -c "code"    # 分析代码
    python src/lexer.py -i           # 交互式模式
"""

import sys
import os
import re
import argparse
from typing import Any, Optional, List, Tuple

# 添加 src 目录到路径，方便导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from token import TokenType, Token, LexerRule


class Lexer:
    """可扩展的Lua词法分析器"""
    
    LUA_KEYWORDS = {
        'and': TokenType.OP_AND,
        'break': TokenType.BREAK,
        'do': TokenType.DO,
        'else': TokenType.ELSE,
        'elseif': TokenType.ELSEIF,
        'end': TokenType.END,
        'false': TokenType.BOOLEAN,
        'for': TokenType.FOR,
        'function': TokenType.FUNCTION,
        'if': TokenType.IF,
        'in': TokenType.IN,
        'local': TokenType.LOCAL,
        'nil': TokenType.NIL,
        'not': TokenType.OP_NOT,
        'or': TokenType.OP_OR,
        'repeat': TokenType.REPEAT,
        'return': TokenType.RETURN,
        'then': TokenType.THEN,
        'true': TokenType.BOOLEAN,
        'until': TokenType.UNTIL,
        'while': TokenType.WHILE,
    }
    
    def __init__(self, source: str = ""):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = None
        self.rules: List[LexerRule] = []
        self._init_default_rules()
        
        if source:
            self._init_source(source)
    
    def _init_source(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        if len(source) > 0:
            self.current_char = source[0]
        else:
            self.current_char = None
    
    def _init_default_rules(self):
        self.add_rule(LexerRule(
            name='number',
            pattern=r'\d+(\.\d+)?([eE][+-]?\d+)?|0x[0-9a-fA-F]+',
            handler=self._handle_number,
            priority=10
        ))
        
        self.add_rule(LexerRule(
            name='string_double',
            pattern=r'"[^"\\]*(\\.[^"\\]*)*"',
            handler=self._handle_string,
            priority=9
        ))
        
        self.add_rule(LexerRule(
            name='string_single',
            pattern=r"'[^'\\]*(\\.[^'\\]*)*'",
            handler=self._handle_string,
            priority=9
        ))
        
        self.add_rule(LexerRule(
            name='identifier',
            pattern=r'[a-zA-Z_][a-zA-Z0-9_]*',
            handler=self._handle_identifier,
            priority=8
        ))
        
        self.add_rule(LexerRule(
            name='double_char_ops',
            pattern=r'==|~=|<=|>=|\.\.',
            handler=self._handle_double_char_op,
            priority=7
        ))
        
        self.add_rule(LexerRule(
            name='single_char_ops',
            pattern=r'[+\-*/%^#=<>(){}[\];:,]',
            handler=self._handle_single_char_op,
            priority=6
        ))
        
        self.add_rule(LexerRule(
            name='comment',
            pattern=r'--.*?(?=\n|$)',
            handler=self._handle_comment,
            priority=5
        ))
        
        self.add_rule(LexerRule(
            name='whitespace',
            pattern=r'[ \t]+',
            handler=self._handle_whitespace,
            priority=4
        ))
        
        self.add_rule(LexerRule(
            name='newline',
            pattern=r'\n|\r\n?',
            handler=self._handle_newline,
            priority=4
        ))
    
    def add_rule(self, rule: LexerRule):
        inserted = False
        for i, existing in enumerate(self.rules):
            if rule.priority > existing.priority:
                self.rules.insert(i, rule)
                inserted = True
                break
        if not inserted:
            self.rules.append(rule)
    
    def remove_rule(self, name: str):
        self.rules = [r for r in self.rules if r.name != name]
    
    def _advance(self, count: int = 1):
        for _ in range(count):
            if self.pos < len(self.source) - 1:
                self.pos += 1
                self.current_char = self.source[self.pos]
                self.column += 1
            else:
                self.current_char = None
                break
    
    def _handle_number(self, text: str, line: int, column: int) -> Optional[Token]:
        try:
            if text.startswith('0x') or text.startswith('0X'):
                value = int(text, 16)
            elif '.' in text or 'e' in text.lower():
                value = float(text)
            else:
                value = int(text)
            return Token(TokenType.NUMBER, value, line, column, text)
        except ValueError:
            return None
    
    def _handle_string(self, text: str, line: int, column: int) -> Optional[Token]:
        quote = text[0]
        content = text[1:-1]
        
        result = ""
        i = 0
        while i < len(content):
            if content[i] == '\\' and i + 1 < len(content):
                next_char = content[i + 1]
                escape_map = {
                    'n': '\n', 't': '\t', 'r': '\r',
                    '\\': '\\', '"': '"', "'": "'", '0': '\0',
                }
                if next_char in escape_map:
                    result += escape_map[next_char]
                    i += 2
                else:
                    result += next_char
                    i += 2
            else:
                result += content[i]
                i += 1
        
        return Token(TokenType.STRING, result, line, column, text)
    
    def _handle_identifier(self, text: str, line: int, column: int) -> Optional[Token]:
        if text in self.LUA_KEYWORDS:
            token_type = self.LUA_KEYWORDS[text]
            if token_type == TokenType.BOOLEAN:
                value = (text == 'true')
                return Token(token_type, value, line, column, text)
            elif token_type == TokenType.NIL:
                return Token(token_type, None, line, column, text)
            else:
                return Token(token_type, text, line, column, text)
        else:
            return Token(TokenType.IDENTIFIER, text, line, column, text)
    
    def _handle_double_char_op(self, text: str, line: int, column: int) -> Optional[Token]:
        op_map = {
            '==': TokenType.OP_EQ,
            '~=': TokenType.OP_NE,
            '<=': TokenType.OP_LE,
            '>=': TokenType.OP_GE,
            '..': TokenType.OP_CONCAT,
        }
        if text in op_map:
            return Token(op_map[text], text, line, column, text)
        return None
    
    def _handle_single_char_op(self, text: str, line: int, column: int) -> Optional[Token]:
        op_map = {
            '+': TokenType.OP_PLUS, '-': TokenType.OP_MINUS,
            '*': TokenType.OP_MULT, '/': TokenType.OP_DIV,
            '%': TokenType.OP_MOD, '^': TokenType.OP_POW,
            '#': TokenType.OP_CONCAT, '=': TokenType.ASSIGN,
            '<': TokenType.OP_LT, '>': TokenType.OP_GT,
            '(': TokenType.LPAREN, ')': TokenType.RPAREN,
            '{': TokenType.LBRACE, '}': TokenType.RBRACE,
            '[': TokenType.LBRACKET, ']': TokenType.RBRACKET,
            ';': TokenType.SEMICOLON, ':': TokenType.COLON,
            ',': TokenType.COMMA, '.': TokenType.DOT,
        }
        if text in op_map:
            return Token(op_map[text], text, line, column, text)
        return None
    
    def _handle_comment(self, text: str, line: int, column: int) -> Optional[Token]:
        return None
    
    def _handle_whitespace(self, text: str, line: int, column: int) -> Optional[Token]:
        return None
    
    def _handle_newline(self, text: str, line: int, column: int) -> Optional[Token]:
        return None
    
    def _try_match_rule(self, rule: LexerRule) -> Tuple[Optional[Token], bool]:
        original_pos = self.pos
        remaining = self.source[self.pos:]
        match = re.match('^' + rule.pattern, remaining)
        
        if match:
            matched_text = match.group(0)
            matched_len = len(matched_text)
            
            original_line = self.line
            original_column = self.column
            
            new_pos = self.pos + matched_len
            new_line = self.line
            new_column = self.column
            
            for char in matched_text:
                if char == '\n':
                    new_line += 1
                    new_column = 1
                elif char != '\r':
                    new_column += 1
            
            if rule.handler:
                token = rule.handler(matched_text, original_line, original_column)
            elif rule.token_type:
                token = Token(rule.token_type, matched_text, original_line, original_column, matched_text)
            else:
                token = None
            
            self.pos = new_pos
            self.line = new_line
            self.column = new_column
            if self.pos < len(self.source):
                self.current_char = self.source[self.pos]
            else:
                self.current_char = None
            
            advanced = (self.pos != original_pos)
            return (token, advanced)
        
        return (None, False)
    
    def get_next_token(self) -> Token:
        while self.current_char is not None:
            advanced_any = False
            
            for rule in self.rules:
                token, advanced = self._try_match_rule(rule)
                
                if token is not None:
                    return token
                
                if advanced:
                    advanced_any = True
                    break
            
            if not advanced_any:
                token = Token(
                    TokenType.UNKNOWN, 
                    self.current_char, 
                    self.line, 
                    self.column,
                    self.current_char
                )
                self._advance()
                return token
        
        return Token(TokenType.EOF, None, self.line, self.column, "")
    
    def tokenize(self, source: str = None) -> List[Token]:
        if source is not None:
            self._init_source(source)
        
        tokens = []
        while True:
            token = self.get_next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        
        return tokens
    
    def reset(self, source: str = ""):
        if source:
            self._init_source(source)
        else:
            self._init_source(self.source)


def get_test_cases() -> list:
    """
    获取测试用例 - 方便扩展
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


def analyze_code(lexer: Lexer, source: str, show_details: bool = True) -> list:
    """分析代码并返回Token列表"""
    tokens = lexer.tokenize(source)
    
    if show_details:
        print(f"\n输入: {repr(source)}")
        print(f"Token数: {len(tokens)}")
        for i, token in enumerate(tokens):
            print(f"  {i+1:2d}. {token}")
    
    return tokens


def run_tests() -> int:
    """运行所有测试"""
    print("=" * 60)
    print("Lexer 模块单元测试")
    print("=" * 60)
    
    lexer = Lexer()
    test_cases = get_test_cases()
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
    print(f"结果: 通过 {passed}, 失败 {failed}, 总计 {len(test_cases)}")
    print(f"{'='*60}")
    
    return 0 if failed == 0 else 1


def interactive_mode():
    """交互式模式"""
    print("=" * 60)
    print("Lua Lexer 交互式模式")
    print("=" * 60)
    print("输入代码进行分析，输入 'quit' 退出")
    
    lexer = Lexer()
    
    while True:
        try:
            user_input = input("\n>>> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ('quit', 'exit', 'q'):
                print("再见!")
                break
            
            analyze_code(lexer, user_input)
            
        except KeyboardInterrupt:
            print("\n再见!")
            break
        except EOFError:
            print("\n再见!")
            break


def main():
    """CLI入口点"""
    parser = argparse.ArgumentParser(
        description='Lua Lexer - 词法分析器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python src/lexer.py              # 运行测试
  python src/lexer.py -t           # 运行测试
  python src/lexer.py -i           # 交互式模式
  python src/lexer.py -c "local x = 10"  # 分析代码
        """
    )
    
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('-t', '--test', action='store_true', help='运行单元测试')
    mode_group.add_argument('-i', '--interactive', action='store_true', help='交互式模式')
    mode_group.add_argument('-c', '--code', type=str, metavar='CODE', help='分析代码')
    
    parser.add_argument('--version', action='version', version='Lua Lexer v1.0')
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
        return 0
    elif args.code:
        lexer = Lexer()
        analyze_code(lexer, args.code)
        return 0
    else:
        return run_tests()


if __name__ == "__main__":
    sys.exit(main())
