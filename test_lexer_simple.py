#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试词法分析器
"""

from lexer import Lexer, TokenType

print("=" * 50)
print("测试1: 变量定义")
print("输入: local x = 10")
print("=" * 50)

lexer = Lexer("local x = 10")
tokens = lexer.tokenize()

for token in tokens:
    print(f"  {token}")

print("\n" + "=" * 50)
print("测试2: 不同数据类型")
print("=" * 50)

test_cases = [
    ("数字", "local num = 3.14159"),
    ("字符串", 'local str = "Hello World"'),
    ("布尔值", "local flag = true"),
    ("nil值", "local nothing = nil"),
]

for name, source in test_cases:
    print(f"\n--- {name} ---")
    print(f"输入: {source}")
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    for token in tokens:
        print(f"  {token}")

print("\n" + "=" * 50)
print("测试3: 运算符")
print("输入: a + b * c - d / e")
print("=" * 50)

lexer = Lexer("a + b * c - d / e")
tokens = lexer.tokenize()
for token in tokens:
    print(f"  {token}")

print("\n" + "=" * 50)
print("所有测试完成!")
print("=" * 50)
