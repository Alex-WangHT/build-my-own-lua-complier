#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证词法分析器功能
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer, TokenType, Token, LexerRule, get_test_cases

print("=" * 70)
print("Lua Lexer 功能验证")
print("=" * 70)

# 测试1: 基本Token类型
print("\n1. 测试TokenType枚举:")
print(f"   总Token类型数: {len(TokenType)}")
print(f"   示例类型: {list(TokenType)[:5]}")

# 测试2: 创建Lexer实例
print("\n2. 测试Lexer实例创建:")
lexer = Lexer()
print(f"   ✓ Lexer创建成功")
print(f"   ✓ 默认规则数: {len(lexer.rules)}")

# 测试3: 简单代码分析
print("\n3. 测试简单代码分析:")
test_code = "local x = 10 + 5"
print(f"   输入代码: {test_code}")

tokens = lexer.tokenize(test_code)
print(f"   ✓ 生成Token数: {len(tokens)}")
print("\n   Token列表:")
for i, token in enumerate(tokens, 1):
    print(f"      {i}. {token}")

# 测试4: 数据类型解析
print("\n4. 测试数据类型解析:")
test_cases = [
    ("整数", "local a = 42"),
    ("浮点数", "local b = 3.14159"),
    ("十六进制", "local c = 0xFF"),
    ("科学计数法", "local d = 1e-5"),
    ("字符串", 'local e = "Hello World"'),
    ("布尔值true", "local f = true"),
    ("布尔值false", "local g = false"),
    ("nil值", "local h = nil"),
]

for name, code in test_cases:
    lexer.reset(code)
    tokens = lexer.tokenize()
    
    # 检查是否有数字/字符串/布尔值/nil token
    has_valid = False
    for token in tokens:
        if token.type in [TokenType.NUMBER, TokenType.STRING, 
                          TokenType.BOOLEAN, TokenType.NIL]:
            has_valid = True
            print(f"   ✓ {name}: {repr(token.value)} (类型: {token.type.name})")
            break
    
    if not has_valid:
        print(f"   ✗ {name}: 未找到有效Token")

# 测试5: 预定义测试用例
print("\n5. 测试预定义测试用例:")
test_cases = get_test_cases()
print(f"   预定义测试用例数: {len(test_cases)}")
print(f"   示例测试用例: {test_cases[0][1]}")

# 测试6: 规则管理
print("\n6. 测试规则管理:")
print(f"   当前规则数: {len(lexer.rules)}")
print(f"\n   规则列表 (优先级从高到低):")
for i, rule in enumerate(lexer.rules, 1):
    print(f"      {i}. {rule.name:20} (优先级: {rule.priority})")

# 测试7: 添加自定义规则
print("\n7. 测试添加自定义规则:")

# 定义一个自定义规则，用于识别Lua的长字符串 [[...]]
def handle_long_string(text, line, column):
    # 简单处理 [[...]] 格式的字符串
    content = text[2:-2]  # 移除 [[ 和 ]]
    return Token(TokenType.STRING, content, line, column, text)

custom_rule = LexerRule(
    name='long_string',
    pattern=r'\[\[[^\]]*\]\]',
    handler=handle_long_string,
    priority=15  # 比默认规则优先级高
)

lexer.add_rule(custom_rule)
print(f"   ✓ 添加自定义规则: {custom_rule.name}")
print(f"   ✓ 当前规则数: {len(lexer.rules)}")

# 测试自定义规则
test_long_string = "[[Hello long string]]"
lexer.reset(test_long_string)
tokens = lexer.tokenize()
print(f"\n   测试长字符串: {test_long_string}")
for token in tokens:
    if token.type == TokenType.STRING:
        print(f"   ✓ 解析结果: {repr(token.value)}")

# 测试8: 移除规则
print("\n8. 测试移除规则:")
lexer.remove_rule('long_string')
print(f"   ✓ 移除规则: long_string")
print(f"   ✓ 当前规则数: {len(lexer.rules)}")

print("\n" + "=" * 70)
print("验证完成!")
print("=" * 70)
