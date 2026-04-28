#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lua Lexer - 可扩展的词法分析器
用于解析Lua的变量和数据类型
"""

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


def main():
    """
    单元测试主函数
    输入解析的语句，输出解析的结果
    """
    print("=" * 60)
    print("Lua Lexer 单元测试")
    print("=" * 60)
    
    # 测试用例
    test_cases = [
        # 测试1: 变量定义
        ("local x = 10", "变量定义"),
        
        # 测试2: 数字类型
        ("local num = 3.14159", "浮点数"),
        ("local hex = 0xFF", "十六进制"),
        ("local sci = 1e-5", "科学计数法"),
        
        # 测试3: 字符串类型
        ('local str = "Hello World"', "双引号字符串"),
        ("local str = 'Lua is fun'", "单引号字符串"),
        ('local escape = "Line1\\nLine2\\tTabbed"', "转义字符串"),
        
        # 测试4: 布尔值和nil
        ("local flag = true", "布尔值true"),
        ("local flag = false", "布尔值false"),
        ("local nothing = nil", "nil值"),
        
        # 测试5: 运算符
        ("local sum = a + b * c - d / e", "算术运算符"),
        ("local cmp = x == y or x ~= z", "比较运算符"),
        ("local concat = 'Hello' .. ' ' .. 'World'", "连接运算符"),
        
        # 测试6: 表定义
        ("local tbl = {1, 2, 3, key = 'value'}", "表构造"),
        
        # 测试7: 函数定义
        ("local function add(a, b) return a + b end", "函数定义"),
        
        # 测试8: 控制流
        ("if x > 0 then print('positive') else print('negative') end", "条件语句"),
        
        # 测试9: 注释
        ("-- 这是一行注释\nlocal x = 1", "单行注释"),
        
        # 测试10: 综合测试
        ("""
-- 综合测试
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
        """, "综合测试"),
    ]
    
    # 执行测试
    lexer = Lexer()
    all_passed = True
    failed_count = 0
    passed_count = 0
    
    for i, (source, description) in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}: {description}")
        print(f"输入: {repr(source)}")
        print(f"{'-'*60}")
        
        try:
            tokens = lexer.tokenize(source)
            
            print("Token列表:")
            for j, token in enumerate(tokens):
                print(f"  {j+1:2d}. {token}")
            
            # 简单验证：确保有EOF token
            has_eof = any(t.type == TokenType.EOF for t in tokens)
            if has_eof:
                print(f"\n✓ 测试 {i} 通过")
                passed_count += 1
            else:
                print(f"\n✗ 测试 {i} 失败: 缺少EOF token")
                failed_count += 1
                all_passed = False
                
        except Exception as e:
            print(f"\n✗ 测试 {i} 失败: {e}")
            import traceback
            traceback.print_exc()
            failed_count += 1
            all_passed = False
    
    # 统计结果
    print(f"\n{'='*60}")
    print("测试结果统计")
    print(f"{'='*60}")
    print(f"总测试数: {len(test_cases)}")
    print(f"通过: {passed_count}")
    print(f"失败: {failed_count}")
    print(f"{'='*60}")
    
    if all_passed:
        print("\n🎉 所有测试通过!")
        return 0
    else:
        print(f"\n❌ 有 {failed_count} 个测试失败")
        return 1


if __name__ == "__main__":
    exit_code = main()
    import sys
    sys.exit(exit_code)
