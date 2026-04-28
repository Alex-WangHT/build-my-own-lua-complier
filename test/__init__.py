#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试包 - 包含所有单元测试

该包包含以下模块:
    - test_token.py: Token 模块单元测试
    - test_lexer.py: Lexer 模块单元测试
    - __main__.py: CLI 入口

使用方法:
    python -m test              # 运行所有测试
    python -m test -m token     # 只运行 token 测试
    python -m test -m lexer     # 只运行 lexer 测试
    python -m test -c "code"    # 分析代码
"""

from .test_token import run_tests as run_token_tests, get_test_cases as get_token_cases
from .test_lexer import run_tests as run_lexer_tests, get_test_cases as get_lexer_cases

__all__ = [
    'run_token_tests',
    'run_lexer_tests',
    'get_token_cases',
    'get_lexer_cases',
]
