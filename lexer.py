#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lua Lexer - 可扩展的词法分析器
用于解析Lua的变量和数据类型

使用方法:
    python lexer.py              # 进入交互式模式
    python lexer.py -i           # 进入交互式模式
    python lexer.py -t           # 运行预定义测试用例
    python lexer.py -f file.lua  # 分析文件
    python lexer.py -c "code"    # 分析命令行代码
    python lexer.py -r           # 查看已定义的规则
    python lexer.py -h           # 显示帮助信息
"""

import argparse
import sys
import os
from enum import Enum, auto
from typing import Any, Optional, List, Callable


class TokenType(Enum):
    """Token类型枚举 - 可扩展"""
    # 基础类型
    EOF = auto()
    UNKNOWN = auto()
    
    # 关键字
    KEYWORD = auto()
    
    # 标识符
    IDENTIFIER = auto()
    
    # 数据类型字面量
    NUMBER = auto()
    STRING = auto()
    BOOLEAN = auto()
    NIL = auto()
    
    # 运算符
    OP_PLUS = auto()
    OP_MINUS = auto()
    OP_MULT = auto()
    OP_DIV = auto()
    OP_MOD = auto()
    OP_POW = auto()
    OP_CONCAT = auto()
    
    # 比较运算符
    OP_EQ = auto()
    OP_NE = auto()
    OP_LT = auto()
    OP_GT = auto()
    OP_LE = auto()
    OP_GE = auto()
    
    # 逻辑运算符
    OP_AND = auto()
    OP_OR = auto()
    OP_NOT = auto()
    
    # 赋值运算符
    ASSIGN = auto()
    
    # 括号
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    
    # 分隔符
    COMMA = auto()
    SEMICOLON = auto()
    COLON = auto()
    DOT = auto()
    DOUBLE_DOT = auto()
    
    # 表构造
    TABLE_START = auto()
    TABLE_END = auto()
    
    # 函数相关
    FUNCTION = auto()
    RETURN = auto()
    
    # 控制流
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
    
    # 作用域
    LOCAL = auto()
    
    # 注释
    COMMENT = auto()


class Token:
    """Token类 - 表示一个词法单元"""
    
    def __init__(self, token_type: TokenType, value: Any = None, 
                 line: int = 1, column: int = 1, raw: str = ""):
        """
        初始化Token
        
        Args:
            token_type: Token类型
            value: Token的值（解析后的值）
            line: 所在行号
            column: 所在列号
            raw: 原始字符串
        """
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column
        self.raw = raw or str(value) if value is not None else ""
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"Token({self.type.name}, {repr(self.value)}, line={self.line}, col={self.column})"
    
    def __str__(self) -> str:
        """可读字符串表示"""
        value_str = repr(self.value) if self.value is not None else "None"
        return f"[Line {self.line}:{self.column}] {self.type.name:20} = {value_str}"


class LexerRule:
    """词法规则类 - 用于扩展词法分析器"""
    
    def __init__(self, name: str, pattern: str, 
                 handler: Optional[Callable[[str, int, int], Optional[Token]]] = None,
                 token_type: Optional[TokenType] = None,
                 priority: int = 0):
        """
        初始化词法规则
        
        Args:
            name: 规则名称
            pattern: 正则表达式模式
            handler: 自定义处理函数，接收(匹配文本, 行号, 列号)，返回Token或None
            token_type: 如果没有handler，直接使用此类型创建Token
            priority: 优先级，数字越大优先级越高
        """
        self.name = name
        self.pattern = pattern
        self.handler = handler
        self.token_type = token_type
        self.priority = priority
    
    def __repr__(self) -> str:
        return f"LexerRule('{self.name}', '{self.pattern}')"


class Lexer:
    """可扩展的Lua词法分析器"""
    
    # Lua关键字
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
        """
        初始化词法分析器
        
        Args:
            source: 要分析的源代码字符串
        """
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
        """初始化源代码"""
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        if len(source) > 0:
            self.current_char = source[0]
        else:
            self.current_char = None
    
    def _init_default_rules(self):
        """初始化默认词法规则"""
        # 数字规则
        self.add_rule(LexerRule(
            name='number',
            pattern=r'\d+(\.\d+)?([eE][+-]?\d+)?|0x[0-9a-fA-F]+',
            handler=self._handle_number,
            priority=10
        ))
        
        # 字符串规则 - 双引号
        self.add_rule(LexerRule(
            name='string_double',
            pattern=r'"([^"\\]|\\.)*"',
            handler=self._handle_string,
            priority=9
        ))
        
        # 字符串规则 - 单引号
        self.add_rule(LexerRule(
            name='string_single',
            pattern=r"'([^'\\]|\\.)*'",
            handler=self._handle_string,
            priority=9
        ))
        
        # 标识符和关键字规则
        self.add_rule(LexerRule(
            name='identifier',
            pattern=r'[a-zA-Z_][a-zA-Z0-9_]*',
            handler=self._handle_identifier,
            priority=8
        ))
        
        # 双字符运算符规则
        self.add_rule(LexerRule(
            name='double_char_ops',
            pattern=r'==|~=|<=|>=|\.\.',
            handler=self._handle_double_char_op,
            priority=7
        ))
        
        # 单字符运算符规则
        self.add_rule(LexerRule(
            name='single_char_ops',
            pattern=r'[+\-*/%^#=<>(){}[\];:,]',
            handler=self._handle_single_char_op,
            priority=6
        ))
        
        # 注释规则
        self.add_rule(LexerRule(
            name='comment',
            pattern=r'--.*?(?=\n|$)',
            handler=self._handle_comment,
            priority=5
        ))
        
        # 空白字符规则
        self.add_rule(LexerRule(
            name='whitespace',
            pattern=r'[ \t]+',
            handler=self._handle_whitespace,
            priority=4
        ))
        
        # 换行符规则
        self.add_rule(LexerRule(
            name='newline',
            pattern=r'\n|\r\n?',
            handler=self._handle_newline,
            priority=4
        ))
    
    def add_rule(self, rule: LexerRule):
        """
        添加词法规则
        
        Args:
            rule: 词法规则对象
        """
        # 按优先级插入
        inserted = False
        for i, existing in enumerate(self.rules):
            if rule.priority > existing.priority:
                self.rules.insert(i, rule)
                inserted = True
                break
        if not inserted:
            self.rules.append(rule)
    
    def remove_rule(self, name: str):
        """
        移除指定名称的词法规则
        
        Args:
            name: 规则名称
        """
        self.rules = [r for r in self.rules if r.name != name]
    
    def get_rule(self, name: str) -> Optional[LexerRule]:
        """
        获取指定名称的词法规则
        
        Args:
            name: 规则名称
        
        Returns:
            规则对象或None
        """
        for rule in self.rules:
            if rule.name == name:
                return rule
        return None
    
    def _advance(self, count: int = 1):
        """
        前进到下一个字符
        
        Args:
            count: 前进的字符数
        """
        for _ in range(count):
            if self.pos < len(self.source) - 1:
                self.pos += 1
                self.current_char = self.source[self.pos]
                self.column += 1
            else:
                self.current_char = None
                break
    
    def _peek(self, offset: int = 1) -> Optional[str]:
        """
        查看下一个字符但不前进
        
        Args:
            offset: 偏移量
        
        Returns:
            下一个字符或None
        """
        peek_pos = self.pos + offset
        if peek_pos < len(self.source):
            return self.source[peek_pos]
        return None
    
    def _skip_whitespace(self):
        """跳过空白字符"""
        while self.current_char and self.current_char.isspace():
            if self.current_char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self._advance()
    
    def _handle_number(self, text: str, line: int, column: int) -> Optional[Token]:
        """处理数字Token"""
        try:
            if text.startswith('0x') or text.startswith('0X'):
                # 十六进制
                value = int(text, 16)
            elif '.' in text or 'e' in text.lower():
                # 浮点数
                value = float(text)
            else:
                # 整数
                value = int(text)
            return Token(TokenType.NUMBER, value, line, column, text)
        except ValueError:
            return None
    
    def _handle_string(self, text: str, line: int, column: int) -> Optional[Token]:
        """处理字符串Token"""
        # 移除首尾引号
        quote = text[0]
        content = text[1:-1]
        
        # 处理转义字符
        result = ""
        i = 0
        while i < len(content):
            if content[i] == '\\' and i + 1 < len(content):
                next_char = content[i + 1]
                escape_map = {
                    'n': '\n',
                    't': '\t',
                    'r': '\r',
                    '\\': '\\',
                    '"': '"',
                    "'": "'",
                    '0': '\0',
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
        """处理标识符和关键字Token"""
        if text in self.LUA_KEYWORDS:
            # 关键字
            token_type = self.LUA_KEYWORDS[text]
            if token_type == TokenType.BOOLEAN:
                value = (text == 'true')
                return Token(token_type, value, line, column, text)
            elif token_type == TokenType.NIL:
                return Token(token_type, None, line, column, text)
            else:
                return Token(token_type, text, line, column, text)
        else:
            # 普通标识符
            return Token(TokenType.IDENTIFIER, text, line, column, text)
    
    def _handle_double_char_op(self, text: str, line: int, column: int) -> Optional[Token]:
        """处理双字符运算符"""
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
        """处理单字符运算符"""
        op_map = {
            '+': TokenType.OP_PLUS,
            '-': TokenType.OP_MINUS,
            '*': TokenType.OP_MULT,
            '/': TokenType.OP_DIV,
            '%': TokenType.OP_MOD,
            '^': TokenType.OP_POW,
            '#': TokenType.OP_CONCAT,
            '=': TokenType.ASSIGN,
            '<': TokenType.OP_LT,
            '>': TokenType.OP_GT,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            '[': TokenType.LBRACKET,
            ']': TokenType.RBRACKET,
            ';': TokenType.SEMICOLON,
            ':': TokenType.COLON,
            ',': TokenType.COMMA,
            '.': TokenType.DOT,
        }
        if text in op_map:
            return Token(op_map[text], text, line, column, text)
        return None
    
    def _handle_comment(self, text: str, line: int, column: int) -> Optional[Token]:
        """处理注释 - 默认跳过"""
        return None
    
    def _handle_whitespace(self, text: str, line: int, column: int) -> Optional[Token]:
        """处理空白字符 - 默认跳过"""
        return None
    
    def _handle_newline(self, text: str, line: int, column: int) -> Optional[Token]:
        """处理换行符 - 只更新状态，不生成Token"""
        return None
    
    def _try_match_rule(self, rule: LexerRule) -> Optional[Token]:
        """
        尝试匹配指定规则
        
        Args:
            rule: 词法规则
        
        Returns:
            匹配的Token或None
        """
        import re
        
        # 从当前位置开始匹配
        remaining = self.source[self.pos:]
        match = re.match('^' + rule.pattern, remaining)
        
        if match:
            matched_text = match.group(0)
            matched_len = len(matched_text)
            
            # 保存当前状态
            original_line = self.line
            original_column = self.column
            
            # 计算新的位置和行列
            new_pos = self.pos + matched_len
            new_line = self.line
            new_column = self.column
            
            # 计算匹配文本中的换行
            for char in matched_text:
                if char == '\n':
                    new_line += 1
                    new_column = 1
                elif char == '\r':
                    pass  # 单独的\r或\r\n中的\r
                else:
                    new_column += 1
            
            # 调用处理器
            if rule.handler:
                token = rule.handler(matched_text, original_line, original_column)
            elif rule.token_type:
                token = Token(rule.token_type, matched_text, original_line, original_column, matched_text)
            else:
                token = None
            
            if token is not None:
                # 更新位置
                self.pos = new_pos
                self.line = new_line
                self.column = new_column
                if self.pos < len(self.source):
                    self.current_char = self.source[self.pos]
                else:
                    self.current_char = None
                return token
            else:
                # 处理器返回None，表示跳过
                self.pos = new_pos
                self.line = new_line
                self.column = new_column
                if self.pos < len(self.source):
                    self.current_char = self.source[self.pos]
                else:
                    self.current_char = None
                return None
        
        return None
    
    def get_next_token(self) -> Token:
        """
        获取下一个Token
        
        Returns:
            下一个Token
        """
        # 尝试匹配所有规则
        while self.current_char is not None:
            matched = False
            
            for rule in self.rules:
                token = self._try_match_rule(rule)
                if token is not None:
                    return token
                elif token is None and self.pos > 0:
                    # 规则匹配并跳过了一些字符
                    matched = True
                    break
            
            if not matched:
                # 没有匹配到任何规则，返回UNKNOWN token
                token = Token(
                    TokenType.UNKNOWN, 
                    self.current_char, 
                    self.line, 
                    self.column,
                    self.current_char
                )
                self._advance()
                return token
        
        # 返回EOF token
        return Token(TokenType.EOF, None, self.line, self.column, "")
    
    def tokenize(self, source: str = None) -> List[Token]:
        """
        对源代码进行词法分析，返回所有Token列表
        
        Args:
            source: 源代码字符串，如果为None则使用初始化时的source
        
        Returns:
            Token列表
        """
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
        """
        重置词法分析器
        
        Args:
            source: 新的源代码
        """
        if source:
            self._init_source(source)
        else:
            self._init_source(self.source)


def get_test_cases() -> List[tuple]:
    """
    获取预定义的测试用例
    方便扩展 - 添加新测试用例只需在此函数中添加
    
    Returns:
        测试用例列表，每个元素为 (源代码, 描述)
    """
    test_cases = [
        # 基础变量定义
        ("local x = 10", "变量定义 - 整数"),
        ("local pi = 3.14159", "变量定义 - 浮点数"),
        ("local hex_num = 0xFF", "变量定义 - 十六进制"),
        ("local sci_num = 1e-5", "变量定义 - 科学计数法"),
        
        # 字符串类型
        ('local str = "Hello World"', "字符串 - 双引号"),
        ("local str = 'Lua is fun'", "字符串 - 单引号"),
        ('local escape = "Line1\\nLine2\\tTabbed"', "字符串 - 转义字符"),
        
        # 布尔值和nil
        ("local is_active = true", "布尔值 - true"),
        ("local is_valid = false", "布尔值 - false"),
        ("local nothing = nil", "nil值"),
        
        # 运算符
        ("local result = a + b * c - d / e % f ^ g", "运算符 - 算术"),
        ("local cmp = x == y or x ~= z and x < y", "运算符 - 比较和逻辑"),
        ("local concat = 'Hello' .. ' ' .. 'World'", "运算符 - 字符串连接"),
        
        # 表构造
        ("local arr = {1, 2, 3, 4, 5}", "表 - 数组形式"),
        ("local dict = {name = 'Lua', version = 5.4}", "表 - 字典形式"),
        ("local mixed = {1, 2, key = 'value', 3}", "表 - 混合形式"),
        
        # 函数定义
        ("local function add(a, b) return a + b end", "函数 - 简单定义"),
        ("function greet(name) print('Hello, ' .. name) end", "函数 - 全局函数"),
        
        # 控制流
        ("if x > 0 then print('positive') else print('negative') end", "控制流 - if-else"),
        ("while i < 10 do i = i + 1 end", "控制流 - while循环"),
        ("for i = 1, 10 do print(i) end", "控制流 - for循环"),
        
        # 注释
        ("-- 这是一行注释\nlocal x = 1", "注释 - 单行"),
        
        # 综合测试
        ("""
-- 综合测试：计算函数
local function calculate(a, b)
    local sum = a + b
    local product = a * b
    local result = {
        sum = sum,
        product = product,
        difference = a - b
    }
    return result
end

local data = calculate(10, 5)
print("Sum:", data.sum)
print("Product:", data.product)
        """, "综合测试 - 完整函数"),
    ]
    
    return test_cases


def print_tokens(tokens: List[Token], show_details: bool = True):
    """
    格式化打印Token列表
    
    Args:
        tokens: Token列表
        show_details: 是否显示详细信息
    """
    if not tokens:
        print("  (无Token)")
        return
    
    # 统计信息
    token_counts = {}
    for token in tokens:
        token_type = token.type.name
        token_counts[token_type] = token_counts.get(token_type, 0) + 1
    
    # 打印详细信息
    if show_details:
        print(f"\n  {'='*70}")
        print(f"  {'#':<4} {'位置':<12} {'类型':<20} {'值':<30}")
        print(f"  {'='*70}")
        
        for i, token in enumerate(tokens, 1):
            value_str = repr(token.value) if token.value is not None else "None"
            # 截断过长的值
            if len(value_str) > 28:
                value_str = value_str[:25] + "..."
            print(f"  {i:<4} [{token.line}:{token.column:<6}] {token.type.name:<20} {value_str:<30}")
        
        print(f"  {'='*70}")
    
    # 打印统计信息
    print(f"\n  统计信息:")
    print(f"  总Token数: {len(tokens)}")
    print(f"  类型分布:")
    for token_type, count in sorted(token_counts.items()):
        print(f"    {token_type:<20}: {count}")


def analyze_code(lexer: Lexer, source: str, description: str = "输入代码"):
    """
    分析一段Lua代码
    
    Args:
        lexer: 词法分析器实例
        source: Lua源代码
        description: 代码描述
    """
    print(f"\n{'='*70}")
    print(f"分析: {description}")
    print(f"{'='*70}")
    print(f"\n输入代码:")
    # 显示带行号的代码
    lines = source.split('\n')
    for i, line in enumerate(lines, 1):
        print(f"  {i:3d} | {line}")
    
    try:
        tokens = lexer.tokenize(source)
        print_tokens(tokens)
        
        # 验证
        has_eof = any(t.type == TokenType.EOF for t in tokens)
        has_unknown = any(t.type == TokenType.UNKNOWN for t in tokens)
        
        if has_unknown:
            print(f"\n  ⚠ 警告: 存在未知Token!")
            unknown_tokens = [t for t in tokens if t.type == TokenType.UNKNOWN]
            for t in unknown_tokens:
                print(f"    位置 [{t.line}:{t.column}]: {repr(t.value)}")
        
        if has_eof:
            print(f"\n  ✓ 分析完成，共 {len(tokens)} 个Token")
            return True
        else:
            print(f"\n  ✗ 分析失败: 缺少EOF Token")
            return False
            
    except Exception as e:
        print(f"\n  ✗ 分析异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_tests(lexer: Lexer):
    """
    运行预定义的测试用例
    
    Args:
        lexer: 词法分析器实例
    """
    test_cases = get_test_cases()
    
    print("=" * 70)
    print("Lua Lexer 单元测试")
    print(f"测试用例数: {len(test_cases)}")
    print("=" * 70)
    
    passed_count = 0
    failed_count = 0
    failed_tests = []
    
    for i, (source, description) in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"测试 {i}/{len(test_cases)}: {description}")
        print(f"{'='*70}")
        
        try:
            tokens = lexer.tokenize(source)
            
            # 验证
            has_eof = any(t.type == TokenType.EOF for t in tokens)
            has_unknown = any(t.type == TokenType.UNKNOWN for t in tokens)
            
            if has_eof and not has_unknown:
                print(f"  ✓ 通过 ({len(tokens)} 个Token)")
                passed_count += 1
            else:
                print(f"  ✗ 失败")
                if not has_eof:
                    print(f"    原因: 缺少EOF Token")
                if has_unknown:
                    print(f"    原因: 存在未知Token")
                failed_count += 1
                failed_tests.append((i, description))
                
        except Exception as e:
            print(f"  ✗ 异常: {e}")
            failed_count += 1
            failed_tests.append((i, description))
    
    # 统计结果
    print(f"\n{'='*70}")
    print("测试结果统计")
    print(f"{'='*70}")
    print(f"  总测试数: {len(test_cases)}")
    print(f"  通过: {passed_count}")
    print(f"  失败: {failed_count}")
    print(f"  成功率: {passed_count/len(test_cases)*100:.1f}%")
    print(f"{'='*70}")
    
    if failed_tests:
        print(f"\n失败的测试:")
        for i, desc in failed_tests:
            print(f"  {i}. {desc}")
        return 1
    else:
        print(f"\n🎉 所有测试通过!")
        return 0


def interactive_mode(lexer: Lexer):
    """
    交互式模式 - 实时输入Lua代码进行词法分析
    
    Args:
        lexer: 词法分析器实例
    """
    print("=" * 70)
    print("Lua Lexer 交互式模式")
    print("=" * 70)
    print("\n使用说明:")
    print("  - 直接输入Lua代码，按Enter进行词法分析")
    print("  - 输入多行代码: 先输入 '{'，然后输入代码，最后输入 '}'")
    print("  - 特殊命令:")
    print("    help 或 ?    显示帮助信息")
    print("    rules        显示已定义的词法规则")
    print("    tokens       显示所有Token类型")
    print("    test         运行单元测试")
    print("    clear 或 cls 清空屏幕")
    print("    quit 或 exit 退出交互式模式")
    print(f"\n{'='*70}")
    
    while True:
        try:
            # 读取输入
            user_input = input("\n>>> ").strip()
            
            # 处理空输入
            if not user_input:
                continue
            
            # 处理特殊命令
            if user_input.lower() in ('quit', 'exit', 'q'):
                print("再见!")
                break
            
            elif user_input.lower() in ('help', '?'):
                print("\n帮助信息:")
                print("  输入Lua代码进行词法分析")
                print("  输入 '{' 开始多行输入模式，输入 '}' 结束")
                print("  特殊命令: help, rules, tokens, test, clear, quit")
            
            elif user_input.lower() in ('rules', 'r'):
                print(f"\n已定义的词法规则 ({len(lexer.rules)} 个):")
                print(f"{'='*70}")
                print(f"{'优先级':<8} {'名称':<20} {'模式':<40}")
                print(f"{'='*70}")
                for rule in lexer.rules:
                    pattern = rule.pattern[:37] + "..." if len(rule.pattern) > 40 else rule.pattern
                    print(f"{rule.priority:<8} {rule.name:<20} {pattern:<40}")
                print(f"{'='*70}")
            
            elif user_input.lower() in ('tokens', 't'):
                print(f"\n所有Token类型 ({len(TokenType)} 个):")
                print(f"{'='*70}")
                for i, token_type in enumerate(TokenType, 1):
                    print(f"  {i:3d}. {token_type.name}")
                print(f"{'='*70}")
            
            elif user_input.lower() == 'test':
                run_tests(lexer)
            
            elif user_input.lower() in ('clear', 'cls'):
                # 清空屏幕（跨平台）
                os.system('cls' if os.name == 'nt' else 'clear')
                print("=" * 70)
                print("Lua Lexer 交互式模式")
                print("=" * 70)
            
            elif user_input == '{':
                # 多行输入模式
                print("多行输入模式 (输入 '}' 结束):")
                lines = []
                while True:
                    line = input("... ")
                    if line.strip() == '}':
                        break
                    lines.append(line)
                
                source = '\n'.join(lines)
                if source.strip():
                    analyze_code(lexer, source, "多行输入")
            
            else:
                # 普通代码分析
                analyze_code(lexer, user_input, "单行输入")
                
        except KeyboardInterrupt:
            print("\n\n已中断 (按 Ctrl+D 或输入 'quit' 退出)")
        except EOFError:
            print("\n再见!")
            break
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()
    
    return 0


def analyze_file(lexer: Lexer, file_path: str):
    """
    分析文件中的Lua代码
    
    Args:
        lexer: 词法分析器实例
        file_path: 文件路径
    """
    print(f"=" * 70)
    print(f"文件分析: {file_path}")
    print(f"=" * 70)
    
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在: {file_path}")
        return 1
    
    if not os.path.isfile(file_path):
        print(f"错误: 不是文件: {file_path}")
        return 1
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        return 0 if analyze_code(lexer, source, f"文件: {file_path}") else 1
        
    except Exception as e:
        print(f"错误: 读取文件失败 - {e}")
        return 1


def main():
    """
    主函数 - CLI入口点
    支持多种模式：交互式、测试、文件分析、命令行代码分析
    """
    parser = argparse.ArgumentParser(
        description='Lua Lexer - 可扩展的Lua词法分析器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python lexer.py              # 进入交互式模式
  python lexer.py -i           # 进入交互式模式
  python lexer.py -t           # 运行单元测试
  python lexer.py -c "local x = 10"  # 分析命令行代码
  python lexer.py -f test.lua  # 分析文件
  python lexer.py -r           # 查看已定义的规则
        """
    )
    
    # 模式选择（互斥）
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='进入交互式模式（默认）'
    )
    mode_group.add_argument(
        '-t', '--test',
        action='store_true',
        help='运行预定义的单元测试'
    )
    mode_group.add_argument(
        '-f', '--file',
        type=str,
        metavar='FILE',
        help='分析指定的Lua文件'
    )
    mode_group.add_argument(
        '-c', '--code',
        type=str,
        metavar='CODE',
        help='分析命令行提供的Lua代码'
    )
    mode_group.add_argument(
        '-r', '--rules',
        action='store_true',
        help='显示已定义的词法规则'
    )
    
    # 其他选项
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细输出'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='Lua Lexer v1.0'
    )
    
    # 解析参数
    args = parser.parse_args()
    
    # 创建词法分析器实例
    lexer = Lexer()
    
    # 根据模式执行
    if args.test:
        # 测试模式
        sys.exit(run_tests(lexer))
    
    elif args.file:
        # 文件模式
        sys.exit(analyze_file(lexer, args.file))
    
    elif args.code:
        # 命令行代码模式
        success = analyze_code(lexer, args.code, "命令行输入")
        sys.exit(0 if success else 1)
    
    elif args.rules:
        # 显示规则
        print(f"\n已定义的词法规则 ({len(lexer.rules)} 个):")
        print(f"{'='*80}")
        print(f"{'优先级':<8} {'名称':<20} {'模式':<50}")
        print(f"{'='*80}")
        for rule in lexer.rules:
            pattern = rule.pattern[:47] + "..." if len(rule.pattern) > 50 else rule.pattern
            print(f"{rule.priority:<8} {rule.name:<20} {pattern:<50}")
        print(f"{'='*80}")
        sys.exit(0)
    
    else:
        # 默认：交互式模式
        sys.exit(interactive_mode(lexer))


if __name__ == "__main__":
    main()
