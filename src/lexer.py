#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lexer 模块 - Lua 词法分析器实现

该模块负责将 Lua 源代码转换为 Token 流，是解释器的第一个阶段。

核心组件:
    - Lexer: 词法分析器主类，包含所有词法分析逻辑
    - 各种处理方法: 用于处理不同类型的 Token

词法分析流程:
    1. 从源代码读取字符
    2. 根据预定义的规则匹配 Token
    3. 生成 Token 对象并记录位置信息
    4. 跳过空白和注释

使用示例:
    >>> from lexer import Lexer
    >>> lexer = Lexer()
    >>> tokens = lexer.tokenize("local x = 10")
    >>> for token in tokens:
    ...     print(token)
    [Line 1:1] LOCAL                = 'local'
    [Line 1:7] IDENTIFIER           = 'x'
    [Line 1:9] ASSIGN               = '='
    [Line 1:11] NUMBER              = 10
    [Line 1:13] EOF                  = None
"""

import sys
import os
import re
from typing import Any, Optional, List, Tuple, Dict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from token import TokenType, Token, LexerRule


class Lexer:
    """
    Lua 词法分析器类，用于将源代码转换为 Token 流。

    Lexer 是一个可扩展的词法分析器，支持通过添加自定义规则来扩展功能。
    它使用正则表达式匹配规则，并按照优先级顺序尝试匹配。

    属性:
        source (str): 当前分析的源代码字符串
        pos (int): 当前读取位置的索引
        line (int): 当前行号，从 1 开始
        column (int): 当前列号，从 1 开始
        current_char (str): 当前字符
        rules (List[LexerRule]): 词法规则列表，按优先级排序
        LUA_KEYWORDS (Dict[str, TokenType]): Lua 关键字映射表

    示例:
        >>> # 创建词法分析器
        >>> lexer = Lexer()
        >>>
        >>> # 分析一段代码
        >>> tokens = lexer.tokenize("local name = 'Lua'")
        >>> len(tokens)
        5
        >>> tokens[0].type
        <TokenType.LOCAL: 92>
        >>> tokens[0].value
        'local'

        >>> # 逐个获取 Token
        >>> lexer.reset("a + b")
        >>> token1 = lexer.get_next_token()
        >>> token1.type
        <TokenType.IDENTIFIER: 3>
    """

    LUA_KEYWORDS: Dict[str, TokenType] = {
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
    """
    Lua 关键字映射表。

    该字典将 Lua 关键字字符串映射到对应的 TokenType 枚举值。
    在词法分析过程中，标识符会首先检查是否是关键字。
    """

    def __init__(self, source: str = ""):
        """
        初始化词法分析器实例。

        Args:
            source (str, optional): 要分析的源代码字符串，默认为空字符串

        示例:
            >>> # 创建空的词法分析器
            >>> lexer1 = Lexer()
            >>>
            >>> # 带有源代码的词法分析器
            >>> lexer2 = Lexer("local x = 10")
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
        """
        初始化源代码，重置分析器状态。

        该方法会重置位置、行号、列号等状态，并设置当前字符。

        Args:
            source (str): 要分析的源代码字符串
        """
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        if len(source) > 0:
            self.current_char = source[0]
        else:
            self.current_char = None

    def _init_default_rules(self):
        """
        初始化默认的词法规则。

        该方法会添加以下规则（按优先级从高到低）：
        1. 数字规则 (优先级 10)
        2. 字符串规则 - 双引号 (优先级 9)
        3. 字符串规则 - 单引号 (优先级 9)
        4. 标识符和关键字规则 (优先级 8)
        5. 双字符运算符规则 (优先级 7)
        6. 单字符运算符规则 (优先级 6)
        7. 注释规则 (优先级 5)
        8. 空白字符规则 (优先级 4)
        9. 换行符规则 (优先级 4)
        """
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
        """
        添加一个词法规则到规则列表。

        规则会按照优先级插入到正确的位置，高优先级的规则会先被尝试匹配。

        Args:
            rule (LexerRule): 要添加的词法规则对象

        示例:
            >>> from lexer import Lexer, LexerRule, TokenType, Token
            >>>
            >>> # 定义一个处理函数
            >>> def custom_handler(text, line, column):
            ...     return Token(TokenType.IDENTIFIER, text, line, column, text)
            >>>
            >>> # 创建规则
            >>> custom_rule = LexerRule(
            ...     name='custom',
            ...     pattern=r'@\w+',
            ...     handler=custom_handler,
            ...     priority=15
            ... )
            >>>
            >>> # 添加到词法分析器
            >>> lexer = Lexer()
            >>> lexer.add_rule(custom_rule)
        """
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
        移除指定名称的词法规则。

        Args:
            name (str): 要移除的规则名称

        示例:
            >>> lexer = Lexer()
            >>> lexer.remove_rule('comment')  # 移除注释规则
        """
        self.rules = [r for r in self.rules if r.name != name]

    def _advance(self, count: int = 1):
        """
        前进到下一个字符。

        Args:
            count (int, optional): 前进的字符数，默认为 1
        """
        for _ in range(count):
            if self.pos < len(self.source) - 1:
                self.pos += 1
                self.current_char = self.source[self.pos]
                self.column += 1
            else:
                self.current_char = None
                break

    def _handle_number(self, text: str, line: int, column: int) -> Optional[Token]:
        """
        处理数字 Token。

        支持以下数字格式：
        - 整数: 123
        - 浮点数: 3.14, 1.5e-10
        - 十六进制: 0xFF, 0x1A3

        Args:
            text (str): 匹配的数字文本
            line (int): 行号
            column (int): 列号

        Returns:
            Optional[Token]: 数字 Token，解析失败时返回 None

        示例:
            >>> lexer = Lexer()
            >>> token = lexer._handle_number("42", 1, 1)
            >>> token.type
            <TokenType.NUMBER: 4>
            >>> token.value
            42
            >>>
            >>> token2 = lexer._handle_number("0xFF", 1, 1)
            >>> token2.value
            255
            >>>
            >>> token3 = lexer._handle_number("3.14", 1, 1)
            >>> token3.value
            3.14
        """
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
        """
        处理字符串 Token。

        支持以下转义字符：
        - \\n: 换行
        - \\t: 制表符
        - \\r: 回车
        - \\\\: 反斜杠
        - \\": 双引号
        - \\': 单引号
        - \\0: 空字符

        Args:
            text (str): 匹配的字符串文本（包含引号）
            line (int): 行号
            column (int): 列号

        Returns:
            Optional[Token]: 字符串 Token

        示例:
            >>> lexer = Lexer()
            >>> token = lexer._handle_string('"hello"', 1, 1)
            >>> token.type
            <TokenType.STRING: 5>
            >>> token.value
            'hello'
            >>>
            >>> token2 = lexer._handle_string('"line1\\nline2"', 1, 1)
            >>> token2.value
            'line1\\nline2'
        """
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
        """
        处理标识符和关键字 Token。

        该方法会首先检查文本是否是 Lua 关键字：
        - 如果是关键字，返回对应的关键字 Token
        - 如果是布尔值 (true/false)，返回 BOOLEAN 类型
        - 如果是 nil，返回 NIL 类型
        - 否则返回 IDENTIFIER 类型

        Args:
            text (str): 匹配的标识符文本
            line (int): 行号
            column (int): 列号

        Returns:
            Optional[Token]: 标识符或关键字 Token

        示例:
            >>> lexer = Lexer()
            >>>
            >>> # 普通标识符
            >>> token1 = lexer._handle_identifier("myVar", 1, 1)
            >>> token1.type
            <TokenType.IDENTIFIER: 3>
            >>> token1.value
            'myVar'
            >>>
            >>> # 关键字
            >>> token2 = lexer._handle_identifier("local", 1, 1)
            >>> token2.type
            <TokenType.LOCAL: 92>
            >>>
            >>> # 布尔值
            >>> token3 = lexer._handle_identifier("true", 1, 1)
            >>> token3.type
            <TokenType.BOOLEAN: 6>
            >>> token3.value
            True
            >>>
            >>> # nil
            >>> token4 = lexer._handle_identifier("nil", 1, 1)
            >>> token4.type
            <TokenType.NIL: 7>
            >>> token4.value
            None
        """
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
        """
        处理双字符运算符 Token。

        支持的双字符运算符：
        - ==: 相等
        - ~=: 不等
        - <=: 小于等于
        - >=: 大于等于
        - ..: 字符串连接

        Args:
            text (str): 匹配的运算符文本
            line (int): 行号
            column (int): 列号

        Returns:
            Optional[Token]: 运算符 Token

        示例:
            >>> lexer = Lexer()
            >>> token = lexer._handle_double_char_op("==", 1, 1)
            >>> token.type
            <TokenType.OP_EQ: 39>
            >>>
            >>> token2 = lexer._handle_double_char_op("..", 1, 1)
            >>> token2.type
            <TokenType.OP_CONCAT: 36>
        """
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
        """
        处理单字符运算符 Token。

        支持的单字符运算符和分隔符：
        - 算术运算符: +, -, *, /, %, ^, #
        - 比较运算符: <, >, =
        - 括号: ( ), { }, [ ]
        - 分隔符: ;, :, ,, .

        Args:
            text (str): 匹配的字符文本
            line (int): 行号
            column (int): 列号

        Returns:
            Optional[Token]: 运算符或分隔符 Token
        """
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
        """
        处理注释。

        默认情况下，注释会被跳过（返回 None），不生成 Token。
        如果需要保留注释，可以重写此方法或修改规则。

        Args:
            text (str): 匹配的注释文本
            line (int): 行号
            column (int): 列号

        Returns:
            Optional[Token]: 默认返回 None（跳过注释）
        """
        return None

    def _handle_whitespace(self, text: str, line: int, column: int) -> Optional[Token]:
        """
        处理空白字符（空格和制表符）。

        默认情况下，空白字符会被跳过（返回 None），不生成 Token。

        Args:
            text (str): 匹配的空白文本
            line (int): 行号
            column (int): 列号

        Returns:
            Optional[Token]: 默认返回 None（跳过空白）
        """
        return None

    def _handle_newline(self, text: str, line: int, column: int) -> Optional[Token]:
        """
        处理换行符。

        默认情况下，换行符会被跳过（返回 None），不生成 Token。
        行号会在匹配过程中自动更新。

        Args:
            text (str): 匹配的换行文本
            line (int): 行号
            column (int): 列号

        Returns:
            Optional[Token]: 默认返回 None（跳过换行）
        """
        return None

    def _try_match_rule(self, rule: LexerRule) -> Tuple[Optional[Token], bool]:
        """
        尝试匹配指定的词法规则。

        该方法会从当前位置开始尝试匹配规则的正则表达式模式。
        如果匹配成功，会调用规则的处理函数并更新分析器状态。

        Args:
            rule (LexerRule): 要尝试匹配的词法规则

        Returns:
            Tuple[Optional[Token], bool]: 包含两个元素的元组：
                - 第一个元素: 匹配的 Token（如果有），否则为 None
                - 第二个元素: 布尔值，表示位置是否前进了（即使匹配被跳过）

        注意:
            - 即使处理函数返回 None（表示跳过），位置也会前进
            - 这用于处理注释、空白等需要跳过的内容
        """
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
        """
        获取下一个 Token。

        该方法会按优先级顺序尝试所有规则，直到找到匹配的 Token。
        如果没有规则匹配，会返回 UNKNOWN 类型的 Token。

        Returns:
            Token: 下一个 Token，到达文件末尾时返回 EOF Token

        示例:
            >>> lexer = Lexer("local x = 10")
            >>> token1 = lexer.get_next_token()
            >>> token1.type
            <TokenType.LOCAL: 92>
            >>>
            >>> token2 = lexer.get_next_token()
            >>> token2.type
            <TokenType.IDENTIFIER: 3>
        """
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
        """
        对源代码进行词法分析，返回所有 Token 列表。

        这是最常用的方法，会一次性将所有源代码转换为 Token 列表。

        Args:
            source (str, optional): 源代码字符串，如果为 None 则使用初始化时的 source

        Returns:
            List[Token]: Token 列表，最后一个元素是 EOF Token

        示例:
            >>> lexer = Lexer()
            >>> tokens = lexer.tokenize("local a = 1 + 2")
            >>> len(tokens)
            7
            >>> [t.type.name for t in tokens]
            ['LOCAL', 'IDENTIFIER', 'ASSIGN', 'NUMBER', 'OP_PLUS', 'NUMBER', 'EOF']
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
        重置词法分析器状态。

        Args:
            source (str, optional): 新的源代码字符串，默认为空字符串
        """
        if source:
            self._init_source(source)
        else:
            self._init_source(self.source)
