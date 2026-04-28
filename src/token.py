#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Token 模块 - 定义 Token 类型和 Token 类
用于 Lua 解释器的词法分析
"""

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
        """转换为字典"""
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
