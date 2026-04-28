#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Token 模块 - 定义 Lua 解释器的词法单元类型和数据结构

该模块包含以下核心组件:
    - TokenType: 枚举类，定义所有可能的 Token 类型
    - Token: 词法单元类，表示源代码中的一个词法元素
    - LexerRule: 词法规则类，用于扩展词法分析器的匹配规则

使用示例:
    >>> from token import TokenType, Token, LexerRule
    >>> token = Token(TokenType.NUMBER, 42, line=1, column=1)
    >>> print(token)
    [Line 1:1] NUMBER               = 42
"""

from enum import Enum, auto
from typing import Any, Optional, Callable, Dict


class TokenType(Enum):
    """
    Token 类型枚举类，定义 Lua 语言中所有可能的词法单元类型。

    该枚举用于标识词法分析器生成的每个 Token 的类型，包括：
    - 基础类型 (EOF, UNKNOWN)
    - 关键字和标识符
    - 数据类型字面量
    - 各种运算符
    - 括号和分隔符

    属性:
        每个枚举成员自动分配唯一的整数值。

    示例:
        >>> from token import TokenType
        >>> TokenType.NUMBER
        <TokenType.NUMBER: 4>
        >>> TokenType.STRING.name
        'STRING'
    """
    
    EOF = auto()
    """文件结束标记，表示已到达源代码末尾"""
    
    UNKNOWN = auto()
    """未知类型，用于无法识别的字符"""
    
    KEYWORD = auto()
    """关键字类型（已弃用，现使用具体的关键字类型）"""
    
    IDENTIFIER = auto()
    """标识符类型，表示变量名、函数名等用户定义的名称"""
    
    NUMBER = auto()
    """数字类型，包括整数、浮点数、十六进制数"""
    
    STRING = auto()
    """字符串类型，包括单引号和双引号包裹的字符串"""
    
    BOOLEAN = auto()
    """布尔类型，表示 true 或 false"""
    
    NIL = auto()
    """空值类型，表示 nil"""
    
    OP_PLUS = auto()
    """加法运算符 +"""
    
    OP_MINUS = auto()
    """减法运算符 -"""
    
    OP_MULT = auto()
    """乘法运算符 *"""
    
    OP_DIV = auto()
    """除法运算符 /"""
    
    OP_MOD = auto()
    """取模运算符 %"""
    
    OP_POW = auto()
    """幂运算符 ^"""
    
    OP_CONCAT = auto()
    """字符串连接运算符 .. 或 #"""
    
    OP_EQ = auto()
    """相等运算符 =="""
    
    OP_NE = auto()
    """不等运算符 ~="""
    
    OP_LT = auto()
    """小于运算符 <"""
    
    OP_GT = auto()
    """大于运算符 >"""
    
    OP_LE = auto()
    """小于等于运算符 <="""
    
    OP_GE = auto()
    """大于等于运算符 >="""
    
    OP_AND = auto()
    """逻辑与运算符 and"""
    
    OP_OR = auto()
    """逻辑或运算符 or"""
    
    OP_NOT = auto()
    """逻辑非运算符 not"""
    
    ASSIGN = auto()
    """赋值运算符 ="""
    
    LPAREN = auto()
    """左括号 ("""
    
    RPAREN = auto()
    """右括号 )"""
    
    LBRACKET = auto()
    """左方括号 ["""
    
    RBRACKET = auto()
    """右方括号 ]"""
    
    LBRACE = auto()
    """左花括号 {"""
    
    RBRACE = auto()
    """右花括号 }"""
    
    COMMA = auto()
    """逗号 ,"""
    
    SEMICOLON = auto()
    """分号 ;"""
    
    COLON = auto()
    """冒号 :"""
    
    DOT = auto()
    """点号 ."""
    
    DOUBLE_DOT = auto()
    """双点号 ..（已弃用，使用 OP_CONCAT）"""
    
    TABLE_START = auto()
    """表开始标记（已弃用，使用 LBRACE）"""
    
    TABLE_END = auto()
    """表结束标记（已弃用，使用 RBRACE）"""
    
    FUNCTION = auto()
    """函数关键字 function"""
    
    RETURN = auto()
    """返回关键字 return"""
    
    IF = auto()
    """条件关键字 if"""
    
    ELSE = auto()
    """否则关键字 else"""
    
    ELSEIF = auto()
    """否则如果关键字 elseif"""
    
    THEN = auto()
    """那么关键字 then"""
    
    END = auto()
    """结束关键字 end"""
    
    WHILE = auto()
    """循环关键字 while"""
    
    DO = auto()
    """执行关键字 do"""
    
    FOR = auto()
    """循环关键字 for"""
    
    IN = auto()
    """范围关键字 in"""
    
    REPEAT = auto()
    """重复关键字 repeat"""
    
    UNTIL = auto()
    """直到关键字 until"""
    
    BREAK = auto()
    """跳出关键字 break"""
    
    LOCAL = auto()
    """局部变量关键字 local"""
    
    COMMENT = auto()
    """注释类型"""


class Token:
    """
    词法单元类，表示源代码中的一个词法元素。

    Token 是词法分析的基本单位，包含以下信息：
    - 类型 (type): TokenType 枚举值
    - 值 (value): 解析后的值（如数字 42，字符串 "hello"）
    - 位置信息 (line, column): 在源代码中的行列位置
    - 原始文本 (raw): 源代码中的原始字符串

    属性:
        type (TokenType): Token 的类型
        value (Any): Token 的值，类型取决于具体的 TokenType
        line (int): 所在行号，从 1 开始
        column (int): 所在列号，从 1 开始
        raw (str): 源代码中的原始文本

    示例:
        >>> # 创建一个数字 Token
        >>> num_token = Token(TokenType.NUMBER, 42, line=1, column=5, raw="42")
        >>> print(num_token.type)
        TokenType.NUMBER
        >>> print(num_token.value)
        42
        >>> print(num_token)
        [Line 1:5] NUMBER               = 42

        >>> # 创建一个字符串 Token
        >>> str_token = Token(TokenType.STRING, "hello", line=2, column=1, raw='"hello"')
        >>> print(str_token.value)
        hello
        >>> print(str_token.raw)
        "hello"
    """

    def __init__(self, token_type: TokenType, value: Any = None,
                 line: int = 1, column: int = 1, raw: str = ""):
        """
        初始化一个 Token 实例。

        Args:
            token_type (TokenType): Token 的类型，必须是 TokenType 枚举值
            value (Any, optional): Token 的值，默认为 None
            line (int, optional): 所在行号，从 1 开始，默认为 1
            column (int, optional): 所在列号，从 1 开始，默认为 1
            raw (str, optional): 源代码中的原始文本，默认为空字符串

        示例:
            >>> # 创建一个标识符 Token
            >>> token = Token(TokenType.IDENTIFIER, "myVar", line=3, column=10, raw="myVar")
            >>> token.type
            <TokenType.IDENTIFIER: 3>
            >>> token.value
            'myVar'
        """
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column
        self.raw = raw or str(value) if value is not None else ""

    def __repr__(self) -> str:
        """
        返回 Token 的官方字符串表示，可用于调试。

        Returns:
            str: 包含类型、值、行号、列号的字符串表示

        示例:
            >>> token = Token(TokenType.NUMBER, 42, line=1, column=1)
            >>> repr(token)
            "Token(NUMBER, 42, line=1, col=1)"
        """
        return f"Token({self.type.name}, {repr(self.value)}, line={self.line}, col={self.column})"

    def __str__(self) -> str:
        """
        返回 Token 的可读字符串表示，用于输出显示。

        Returns:
            str: 格式化的字符串，包含位置、类型和值

        示例:
            >>> token = Token(TokenType.STRING, "hello", line=2, column=5)
            >>> str(token)
            '[Line 2:5] STRING               = 'hello''
        """
        value_str = repr(self.value) if self.value is not None else "None"
        return f"[Line {self.line}:{self.column}] {self.type.name:20} = {value_str}"

    def to_dict(self) -> Dict[str, Any]:
        """
        将 Token 转换为字典表示，便于序列化和测试。

        Returns:
            Dict[str, Any]: 包含所有属性的字典

        示例:
            >>> token = Token(TokenType.NUMBER, 42, line=1, column=5, raw="42")
            >>> token.to_dict()
            {'type': 'NUMBER', 'value': 42, 'line': 1, 'column': 5, 'raw': '42'}
        """
        return {
            'type': self.type.name,
            'value': self.value,
            'line': self.line,
            'column': self.column,
            'raw': self.raw
        }


class LexerRule:
    """
    词法规则类，用于定义和扩展词法分析器的匹配规则。

    LexerRule 允许用户动态添加自定义的词法规则，而无需修改词法分析器的核心代码。
    每个规则包含：
    - 名称 (name): 用于标识规则
    - 正则表达式模式 (pattern): 用于匹配源代码
    - 处理函数 (handler): 用于将匹配的文本转换为 Token
    - 优先级 (priority): 控制规则的匹配顺序

    属性:
        name (str): 规则的唯一名称
        pattern (str): 正则表达式模式字符串
        handler (Optional[Callable]): 处理函数，签名为 (text, line, column) -> Optional[Token]
        token_type (Optional[TokenType]): 默认的 Token 类型（当没有 handler 时使用）
        priority (int): 优先级，数字越大优先级越高

    示例:
        >>> # 创建一个自定义规则来匹配十六进制数字
        >>> def hex_handler(text: str, line: int, column: int):
        ...     value = int(text, 16)
        ...     return Token(TokenType.NUMBER, value, line, column, text)
        >>>
        >>> rule = LexerRule(
        ...     name='hex_number',
        ...     pattern=r'0x[0-9a-fA-F]+',
        ...     handler=hex_handler,
        ...     priority=15
        ... )
        >>>
        >>> print(rule.name)
        hex_number
        >>> print(rule.priority)
        15
    """

    def __init__(self, name: str, pattern: str,
                 handler: Optional[Callable[[str, int, int], Optional[Token]]] = None,
                 token_type: Optional[TokenType] = None,
                 priority: int = 0):
        """
        初始化一个词法规则实例。

        Args:
            name (str): 规则的唯一名称，用于标识和管理规则
            pattern (str): 正则表达式模式，用于匹配源代码中的文本
            handler (Optional[Callable], optional): 处理函数，接收 (匹配文本, 行号, 列号)，
                返回 Token 或 None（表示跳过匹配的文本）。默认为 None
            token_type (Optional[TokenType], optional): 默认的 Token 类型，
                当没有 handler 时使用此类型创建 Token。默认为 None
            priority (int, optional): 优先级，数字越大优先级越高，
                高优先级的规则会先被尝试匹配。默认为 0

        注意:
            - 如果提供了 handler，它将被调用来处理匹配的文本
            - 如果没有 handler 但提供了 token_type，将使用该类型创建简单的 Token
            - 如果两者都没有提供，匹配的文本将被跳过（不生成 Token）

        示例:
            >>> # 创建一个简单规则，使用 token_type
            >>> rule1 = LexerRule(
            ...     name='identifier',
            ...     pattern=r'[a-zA-Z_][a-zA-Z0-9_]*',
            ...     token_type=TokenType.IDENTIFIER,
            ...     priority=8
            ... )

            >>> # 创建一个规则，使用自定义 handler
            >>> def number_handler(text, line, column):
            ...     return Token(TokenType.NUMBER, int(text), line, column, text)
            >>>
            >>> rule2 = LexerRule(
            ...     name='number',
            ...     pattern=r'\d+',
            ...     handler=number_handler,
            ...     priority=10
            ... )
        """
        self.name = name
        self.pattern = pattern
        self.handler = handler
        self.token_type = token_type
        self.priority = priority

    def __repr__(self) -> str:
        """
        返回 LexerRule 的官方字符串表示。

        Returns:
            str: 包含名称和模式的字符串表示

        示例:
            >>> rule = LexerRule('number', r'\d+', priority=10)
            >>> repr(rule)
            "LexerRule('number', '\\d+')"
        """
        return f"LexerRule('{self.name}', '{self.pattern}')"
