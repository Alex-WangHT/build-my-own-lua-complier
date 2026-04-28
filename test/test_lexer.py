#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lexer 模块单元测试

该模块支持以下测试方式：
1. 运行所有测试
2. 按函数/方法测试（如只测试 _handle_number、_handle_string 等）
3. 按代码模式测试（如测试变量定义、字符串处理等）
4. 按特定测试用例测试

使用方法:
    python -m pytest test/test_lexer.py -v
    python test/test_lexer.py
    python test/test_lexer.py --function _handle_number
    python test/test_lexer.py --function _handle_string
    python test/test_lexer.py --pattern "变量定义"
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from lexer import Lexer
from token import TokenType, Token, LexerRule


def get_basic_test_cases() -> list:
    """
    获取基础测试用例列表
    格式: (测试名称, 源代码, 预期Token类型列表)
    """
    return [
        ("变量定义", "local x = 10", 
         [TokenType.LOCAL, TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.NUMBER]),
        
        ("字符串", 'local s = "hello"', 
         [TokenType.LOCAL, TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.STRING]),
        
        ("布尔值", "local flag = true", 
         [TokenType.LOCAL, TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.BOOLEAN]),
        
        ("nil值", "local n = nil", 
         [TokenType.LOCAL, TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.NIL]),
        
        ("算术运算符", "a + b * c", 
         [TokenType.IDENTIFIER, TokenType.OP_PLUS, TokenType.IDENTIFIER, 
          TokenType.OP_MULT, TokenType.IDENTIFIER]),
        
        ("比较运算符", "x == y", 
         [TokenType.IDENTIFIER, TokenType.OP_EQ, TokenType.IDENTIFIER]),
        
        ("不等于运算符", "x ~= y", 
         [TokenType.IDENTIFIER, TokenType.OP_NE, TokenType.IDENTIFIER]),
        
        ("函数定义", "function add() end", 
         [TokenType.FUNCTION, TokenType.IDENTIFIER, TokenType.LPAREN, 
          TokenType.RPAREN, TokenType.END]),
        
        ("数字", "42", [TokenType.NUMBER]),
        
        ("浮点数", "3.14159", [TokenType.NUMBER]),
        
        ("十六进制", "0xFF", [TokenType.NUMBER]),
        
        ("科学计数法", "1e-5", [TokenType.NUMBER]),
        
        ("字符串连接", '"Hello" .. "World"', 
         [TokenType.STRING, TokenType.OP_CONCAT, TokenType.STRING]),
        
        ("注释跳过", "-- This is a comment\nlocal x = 1", 
         [TokenType.LOCAL, TokenType.IDENTIFIER, TokenType.ASSIGN, TokenType.NUMBER]),
        
        ("表构造", "{1, 2, 3}", 
         [TokenType.LBRACE, TokenType.NUMBER, TokenType.COMMA, 
          TokenType.NUMBER, TokenType.COMMA, TokenType.NUMBER, TokenType.RBRACE]),
    ]


def get_function_test_cases() -> dict:
    """
    获取按函数/方法分类的测试用例
    格式: {函数名称: [(测试名称, 测试函数), ...]}
    """
    return {
        '_handle_number': [
            ("整数解析", test_handle_number_int),
            ("浮点数解析", test_handle_number_float),
            ("十六进制解析", test_handle_number_hex),
            ("科学计数法解析", test_handle_number_scientific),
        ],
        '_handle_string': [
            ("双引号字符串", test_handle_string_double),
            ("单引号字符串", test_handle_string_single),
            ("转义字符处理", test_handle_string_escape),
            ("空字符串", test_handle_string_empty),
        ],
        '_handle_identifier': [
            ("普通标识符", test_handle_identifier_normal),
            ("关键字识别", test_handle_identifier_keyword),
            ("布尔值识别", test_handle_identifier_boolean),
            ("nil识别", test_handle_identifier_nil),
        ],
        '_handle_operator': [
            ("单字符运算符", test_handle_operator_single),
            ("双字符运算符", test_handle_operator_double),
        ],
        '_init_default_rules': [
            ("规则初始化", test_init_default_rules),
            ("规则优先级", test_rule_priority),
        ],
        'add_rule': [
            ("添加自定义规则", test_add_custom_rule),
        ],
        'tokenize': [
            ("完整词法分析", test_tokenize_full),
            ("空源代码", test_tokenize_empty),
        ],
        'get_next_token': [
            ("逐个获取Token", test_get_next_token_sequence),
        ],
    }


def get_advanced_test_cases() -> list:
    """
    获取高级测试用例列表
    格式: (测试名称, 测试函数)
    """
    return [
        ("Lexer初始化", test_lexer_init),
        ("Token位置信息", test_token_position),
        ("规则添加移除", test_rule_management),
        ("未知字符处理", test_unknown_char),
        ("空字符串", test_empty_source),
        ("多行代码", test_multiline_source),
    ]


def get_all_functions() -> list:
    """获取所有支持的函数名称"""
    return list(get_function_test_cases().keys())


def get_all_patterns() -> list:
    """获取所有测试模式名称"""
    return [name for name, _, _ in get_basic_test_cases()]


# ============================================================================
# 基础测试辅助函数
# ============================================================================

def run_basic_test(name: str, source: str, expected_types: list) -> bool:
    """
    运行单个基础测试

    Args:
        name (str): 测试名称
        source (str): 源代码
        expected_types (list): 预期的 TokenType 列表

    Returns:
        bool: 测试是否通过
    """
    lexer = Lexer()
    try:
        tokens = lexer.tokenize(source)
        actual_types = [t.type for t in tokens if t.type != TokenType.EOF]

        if actual_types == expected_types:
            print(f"  PASS: {name} - 通过 ({len(tokens)} 个Token)")
            return True
        else:
            print(f"  FAIL: {name}")
            print(f"    预期: {[t.name for t in expected_types]}")
            print(f"    实际: {[t.name for t in actual_types]}")
            return False

    except Exception as e:
        print(f"  FAIL: {name} - 异常: {e}")
        return False


# ============================================================================
# 函数测试 - _handle_number
# ============================================================================

def test_handle_number_int() -> bool:
    """测试 _handle_number 方法 - 整数解析"""
    lexer = Lexer()
    token = lexer._handle_number("42", 1, 1)
    
    if token and token.type == TokenType.NUMBER and token.value == 42:
        print(f"  PASS: 整数解析 - 42 -> {token.value}")
        return True
    print(f"  FAIL: 整数解析失败")
    return False


def test_handle_number_float() -> bool:
    """测试 _handle_number 方法 - 浮点数解析"""
    lexer = Lexer()
    token = lexer._handle_number("3.14159", 1, 1)
    
    if token and token.type == TokenType.NUMBER and abs(token.value - 3.14159) < 0.00001:
        print(f"  PASS: 浮点数解析 - 3.14159 -> {token.value}")
        return True
    print(f"  FAIL: 浮点数解析失败")
    return False


def test_handle_number_hex() -> bool:
    """测试 _handle_number 方法 - 十六进制解析"""
    lexer = Lexer()
    token = lexer._handle_number("0xFF", 1, 1)
    
    if token and token.type == TokenType.NUMBER and token.value == 255:
        print(f"  PASS: 十六进制解析 - 0xFF -> {token.value}")
        return True
    print(f"  FAIL: 十六进制解析失败")
    return False


def test_handle_number_scientific() -> bool:
    """测试 _handle_number 方法 - 科学计数法解析"""
    lexer = Lexer()
    token = lexer._handle_number("1e-5", 1, 1)
    
    if token and token.type == TokenType.NUMBER and token.value == 1e-5:
        print(f"  PASS: 科学计数法解析 - 1e-5 -> {token.value}")
        return True
    print(f"  FAIL: 科学计数法解析失败")
    return False


# ============================================================================
# 函数测试 - _handle_string
# ============================================================================

def test_handle_string_double() -> bool:
    """测试 _handle_string 方法 - 双引号字符串"""
    lexer = Lexer()
    token = lexer._handle_string('"hello world"', 1, 1)
    
    if token and token.type == TokenType.STRING and token.value == "hello world":
        print(f"  PASS: 双引号字符串 - {repr(token.value)}")
        return True
    print(f"  FAIL: 双引号字符串解析失败")
    return False


def test_handle_string_single() -> bool:
    """测试 _handle_string 方法 - 单引号字符串"""
    lexer = Lexer()
    token = lexer._handle_string("'lua is fun'", 1, 1)
    
    if token and token.type == TokenType.STRING and token.value == "lua is fun":
        print(f"  PASS: 单引号字符串 - {repr(token.value)}")
        return True
    print(f"  FAIL: 单引号字符串解析失败")
    return False


def test_handle_string_escape() -> bool:
    """测试 _handle_string 方法 - 转义字符处理"""
    lexer = Lexer()
    token = lexer._handle_string('"line1\\nline2\\ttab"', 1, 1)
    
    if token and token.type == TokenType.STRING:
        if '\n' in token.value and '\t' in token.value:
            print(f"  PASS: 转义字符处理 - {repr(token.value)}")
            return True
    print(f"  FAIL: 转义字符处理失败")
    return False


def test_handle_string_empty() -> bool:
    """测试 _handle_string 方法 - 空字符串"""
    lexer = Lexer()
    token = lexer._handle_string('""', 1, 1)
    
    if token and token.type == TokenType.STRING and token.value == "":
        print(f"  PASS: 空字符串 - {repr(token.value)}")
        return True
    print(f"  FAIL: 空字符串解析失败")
    return False


# ============================================================================
# 函数测试 - _handle_identifier
# ============================================================================

def test_handle_identifier_normal() -> bool:
    """测试 _handle_identifier 方法 - 普通标识符"""
    lexer = Lexer()
    token = lexer._handle_identifier("myVariable", 1, 1)
    
    if token and token.type == TokenType.IDENTIFIER and token.value == "myVariable":
        print(f"  PASS: 普通标识符 - {token.value}")
        return True
    print(f"  FAIL: 普通标识符解析失败")
    return False


def test_handle_identifier_keyword() -> bool:
    """测试 _handle_identifier 方法 - 关键字识别"""
    lexer = Lexer()
    token = lexer._handle_identifier("local", 1, 1)
    
    if token and token.type == TokenType.LOCAL and token.value == "local":
        print(f"  PASS: 关键字识别 - local -> {token.type.name}")
        return True
    print(f"  FAIL: 关键字识别失败")
    return False


def test_handle_identifier_boolean() -> bool:
    """测试 _handle_identifier 方法 - 布尔值识别"""
    lexer = Lexer()
    token_true = lexer._handle_identifier("true", 1, 1)
    token_false = lexer._handle_identifier("false", 1, 1)
    
    if (token_true and token_true.type == TokenType.BOOLEAN and token_true.value is True and
        token_false and token_false.type == TokenType.BOOLEAN and token_false.value is False):
        print(f"  PASS: 布尔值识别 - true={token_true.value}, false={token_false.value}")
        return True
    print(f"  FAIL: 布尔值识别失败")
    return False


def test_handle_identifier_nil() -> bool:
    """测试 _handle_identifier 方法 - nil识别"""
    lexer = Lexer()
    token = lexer._handle_identifier("nil", 1, 1)
    
    if token and token.type == TokenType.NIL and token.value is None:
        print(f"  PASS: nil识别 - nil -> {token.value}")
        return True
    print(f"  FAIL: nil识别失败")
    return False


# ============================================================================
# 函数测试 - _handle_operator
# ============================================================================

def test_handle_operator_single() -> bool:
    """测试单字符运算符处理"""
    lexer = Lexer()
    token_plus = lexer._handle_single_char_op("+", 1, 1)
    token_mult = lexer._handle_single_char_op("*", 1, 1)
    
    if (token_plus and token_plus.type == TokenType.OP_PLUS and
        token_mult and token_mult.type == TokenType.OP_MULT):
        print(f"  PASS: 单字符运算符 - +={token_plus.type.name}, *={token_mult.type.name}")
        return True
    print(f"  FAIL: 单字符运算符处理失败")
    return False


def test_handle_operator_double() -> bool:
    """测试双字符运算符处理"""
    lexer = Lexer()
    token_eq = lexer._handle_double_char_op("==", 1, 1)
    token_ne = lexer._handle_double_char_op("~=", 1, 1)
    
    if (token_eq and token_eq.type == TokenType.OP_EQ and
        token_ne and token_ne.type == TokenType.OP_NE):
        print(f"  PASS: 双字符运算符 - ==={token_eq.type.name}, ~={token_ne.type.name}")
        return True
    print(f"  FAIL: 双字符运算符处理失败")
    return False


# ============================================================================
# 函数测试 - _init_default_rules
# ============================================================================

def test_init_default_rules() -> bool:
    """测试规则初始化"""
    lexer = Lexer()
    
    if len(lexer.rules) >= 9:  # 默认有9个规则
        print(f"  PASS: 规则初始化 - {len(lexer.rules)} 个规则")
        return True
    print(f"  FAIL: 规则初始化失败 - 只有 {len(lexer.rules)} 个规则")
    return False


def test_rule_priority() -> bool:
    """测试规则优先级"""
    lexer = Lexer()
    
    # 检查规则是否按优先级排序
    priorities = [rule.priority for rule in lexer.rules]
    is_sorted = all(priorities[i] >= priorities[i + 1] for i in range(len(priorities) - 1))
    
    if is_sorted:
        print(f"  PASS: 规则优先级正确 - {priorities}")
        return True
    print(f"  FAIL: 规则优先级错误 - {priorities}")
    return False


# ============================================================================
# 函数测试 - add_rule
# ============================================================================

def test_add_custom_rule() -> bool:
    """测试添加自定义规则"""
    lexer = Lexer()
    initial_count = len(lexer.rules)
    
    def custom_handler(text, line, col):
        return Token(TokenType.IDENTIFIER, text.upper(), line, col, text)
    
    custom_rule = LexerRule(
        name='test_rule',
        pattern=r'@\w+',
        handler=custom_handler,
        priority=15
    )
    
    lexer.add_rule(custom_rule)
    
    if len(lexer.rules) == initial_count + 1:
        print(f"  PASS: 添加自定义规则成功")
        return True
    print(f"  FAIL: 添加自定义规则失败")
    return False


# ============================================================================
# 函数测试 - tokenize
# ============================================================================

def test_tokenize_full() -> bool:
    """测试完整词法分析"""
    lexer = Lexer()
    tokens = lexer.tokenize("local x = 10 + 5")
    
    expected_types = [
        TokenType.LOCAL, TokenType.IDENTIFIER, TokenType.ASSIGN,
        TokenType.NUMBER, TokenType.OP_PLUS, TokenType.NUMBER, TokenType.EOF
    ]
    
    actual_types = [t.type for t in tokens]
    
    if actual_types == expected_types:
        print(f"  PASS: 完整词法分析 - {len(tokens)} 个Token")
        return True
    print(f"  FAIL: 完整词法分析失败")
    return False


def test_tokenize_empty() -> bool:
    """测试空源代码"""
    lexer = Lexer()
    tokens = lexer.tokenize("")
    
    if len(tokens) == 1 and tokens[0].type == TokenType.EOF:
        print(f"  PASS: 空源代码处理 - 只有 EOF Token")
        return True
    print(f"  FAIL: 空源代码处理失败")
    return False


# ============================================================================
# 函数测试 - get_next_token
# ============================================================================

def test_get_next_token_sequence() -> bool:
    """测试逐个获取Token"""
    lexer = Lexer("a + b")
    
    token1 = lexer.get_next_token()
    token2 = lexer.get_next_token()
    token3 = lexer.get_next_token()
    token4 = lexer.get_next_token()
    
    if (token1.type == TokenType.IDENTIFIER and
        token2.type == TokenType.OP_PLUS and
        token3.type == TokenType.IDENTIFIER and
        token4.type == TokenType.EOF):
        print(f"  PASS: 逐个获取Token - 顺序正确")
        return True
    print(f"  FAIL: 逐个获取Token失败")
    return False


# ============================================================================
# 高级测试函数
# ============================================================================

def test_lexer_init() -> bool:
    """测试 Lexer 初始化"""
    try:
        lexer = Lexer()
        assert lexer.source == ""
        assert lexer.pos == 0
        assert lexer.line == 1
        assert len(lexer.rules) > 0
        
        lexer2 = Lexer("local x = 10")
        assert lexer2.source == "local x = 10"
        print(f"  PASS: Lexer 初始化正确")
        return True
    except Exception as e:
        print(f"  FAIL: Lexer 初始化失败 - {e}")
        return False


def test_token_position() -> bool:
    """测试 Token 位置信息"""
    try:
        lexer = Lexer("local x = 10")
        tokens = lexer.tokenize()
        
        assert tokens[0].line == 1
        assert tokens[0].column == 1
        assert tokens[1].line == 1
        assert tokens[1].column == 7
        print(f"  PASS: Token 位置信息正确")
        return True
    except Exception as e:
        print(f"  FAIL: Token 位置信息失败 - {e}")
        return False


def test_rule_management() -> bool:
    """测试规则添加和移除"""
    try:
        lexer = Lexer()
        initial_count = len(lexer.rules)
        
        def custom_handler(text, line, col):
            return Token(TokenType.IDENTIFIER, text, line, col, text)
        
        custom_rule = LexerRule(
            name='custom_rule',
            pattern=r'@\w+',
            handler=custom_handler,
            priority=15
        )
        
        lexer.add_rule(custom_rule)
        assert len(lexer.rules) == initial_count + 1
        
        lexer.remove_rule('custom_rule')
        assert len(lexer.rules) == initial_count
        
        print(f"  PASS: 规则管理正确")
        return True
    except Exception as e:
        print(f"  FAIL: 规则管理失败 - {e}")
        return False


def test_unknown_char() -> bool:
    """测试未知字符处理"""
    try:
        lexer = Lexer("@")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.UNKNOWN
        print(f"  PASS: 未知字符处理正确")
        return True
    except Exception as e:
        print(f"  FAIL: 未知字符处理失败 - {e}")
        return False


def test_empty_source() -> bool:
    """测试空源代码"""
    try:
        lexer = Lexer("")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF
        print(f"  PASS: 空源代码处理正确")
        return True
    except Exception as e:
        print(f"  FAIL: 空源代码处理失败 - {e}")
        return False


def test_multiline_source() -> bool:
    """测试多行源代码"""
    try:
        source = """local x = 1
local y = 2"""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        lines = [t.line for t in tokens if t.type != TokenType.EOF]
        assert 1 in lines
        assert 2 in lines
        print(f"  PASS: 多行代码处理正确")
        return True
    except Exception as e:
        print(f"  FAIL: 多行代码处理失败 - {e}")
        return False


# ============================================================================
# 测试运行函数
# ============================================================================

def run_basic_tests(pattern: str = None) -> tuple:
    """
    运行基础测试用例

    Args:
        pattern (str, optional): 只运行匹配该模式的测试用例

    Returns:
        tuple: (通过数, 失败数, 结果列表)
    """
    test_cases = get_basic_test_cases()
    
    if pattern:
        test_cases = [(name, src, exp) for name, src, exp in test_cases if pattern.lower() in name.lower()]
        if not test_cases:
            print(f"错误: 找不到匹配的测试模式 '{pattern}'")
            print(f"支持的模式: {', '.join(get_all_patterns())}")
            return 0, 1, []
    
    passed = 0
    failed = 0
    results = []

    print("=" * 60)
    print("Lexer 模块 - 基础测试")
    print("=" * 60)

    for name, source, expected_types in test_cases:
        print(f"\n测试: {name}")
        if run_basic_test(name, source, expected_types):
            passed += 1
            results.append((name, True))
        else:
            failed += 1
            results.append((name, False))

    return passed, failed, results


def run_function_tests(func_name: str = None) -> tuple:
    """
    运行指定函数的测试

    Args:
        func_name (str, optional): 函数名称，如果为 None 则运行所有函数测试

    Returns:
        tuple: (通过数, 失败数, 结果列表)
    """
    func_test_cases = get_function_test_cases()
    
    if func_name:
        if func_name not in func_test_cases:
            print(f"错误: 未知的函数名称 '{func_name}'")
            print(f"支持的函数: {', '.join(get_all_functions())}")
            return 0, 1, []
        
        test_cases = {func_name: func_test_cases[func_name]}
    else:
        test_cases = func_test_cases

    passed = 0
    failed = 0
    results = []

    if func_name:
        print("=" * 60)
        print(f"Lexer 模块 - 函数测试: {func_name}")
        print("=" * 60)
    else:
        print("=" * 60)
        print("Lexer 模块 - 所有函数测试")
        print("=" * 60)

    for func, tests in test_cases.items():
        print(f"\n[{func}]")
        for name, test_func in tests:
            print(f"\n  测试: {name}")
            try:
                if test_func():
                    passed += 1
                    results.append((f"{func}: {name}", True))
                else:
                    failed += 1
                    results.append((f"{func}: {name}", False))
            except Exception as e:
                print(f"    FAIL: 异常 - {e}")
                failed += 1
                results.append((f"{func}: {name}", False))

    return passed, failed, results


def run_advanced_tests() -> tuple:
    """
    运行高级测试用例

    Returns:
        tuple: (通过数, 失败数, 结果列表)
    """
    test_cases = get_advanced_test_cases()
    passed = 0
    failed = 0
    results = []

    print("\n" + "=" * 60)
    print("Lexer 模块 - 高级测试")
    print("=" * 60)

    for name, test_func in test_cases:
        print(f"\n测试: {name}")
        try:
            if test_func():
                passed += 1
                results.append((name, True))
            else:
                failed += 1
                results.append((name, False))
        except Exception as e:
            print(f"  FAIL: 异常 - {e}")
            failed += 1
            results.append((name, False))

    return passed, failed, results


def run_tests(func_name: str = None, pattern: str = None, test_case: str = None) -> tuple:
    """
    运行测试

    Args:
        func_name (str, optional): 只运行指定函数的测试
        pattern (str, optional): 只运行匹配该模式的基础测试
        test_case (str, optional): 只运行指定名称的测试用例

    Returns:
        tuple: (通过数, 失败数, 结果列表)
    """
    if func_name:
        return run_function_tests(func_name)
    
    if pattern:
        return run_basic_tests(pattern)
    
    if test_case:
        print("=" * 60)
        print(f"Lexer 模块 - 特定测试用例: {test_case}")
        print("=" * 60)
        
        # 查找所有测试用例
        all_test_cases = {}
        
        # 基础测试
        for name, source, expected in get_basic_test_cases():
            all_test_cases[name] = lambda n=name, s=source, e=expected: run_basic_test(n, s, e)
        
        # 函数测试
        for func, tests in get_function_test_cases().items():
            for name, test_func in tests:
                all_test_cases[f"{func}: {name}"] = test_func
        
        # 高级测试
        for name, test_func in get_advanced_test_cases():
            all_test_cases[name] = test_func
        
        if test_case in all_test_cases:
            try:
                if all_test_cases[test_case]():
                    return 1, 0, [(test_case, True)]
                else:
                    return 0, 1, [(test_case, False)]
            except Exception as e:
                print(f"  FAIL: 异常 - {e}")
                return 0, 1, [(test_case, False)]
        else:
            print(f"错误: 找不到测试用例 '{test_case}'")
            return 0, 1, []
    
    # 默认运行所有测试
    basic_passed, basic_failed, basic_results = run_basic_tests()
    func_passed, func_failed, func_results = run_function_tests()
    advanced_passed, advanced_failed, advanced_results = run_advanced_tests()
    
    total_passed = basic_passed + func_passed + advanced_passed
    total_failed = basic_failed + func_failed + advanced_failed
    
    print("\n" + "=" * 60)
    print(f"总测试结果")
    print("=" * 60)
    print(f"基础测试: 通过 {basic_passed}, 失败 {basic_failed}")
    print(f"函数测试: 通过 {func_passed}, 失败 {func_failed}")
    print(f"高级测试: 通过 {advanced_passed}, 失败 {advanced_failed}")
    print(f"总计: 通过 {total_passed}, 失败 {total_failed}")
    print("=" * 60)
    
    return total_passed, total_failed, basic_results + func_results + advanced_results


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Lexer 模块单元测试',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
示例:
  python test/test_lexer.py                    # 运行所有测试
  python test/test_lexer.py --function _handle_number  # 只测试 _handle_number 函数
  python test/test_lexer.py --function _handle_string  # 只测试 _handle_string 函数
  python test/test_lexer.py --pattern "变量定义"  # 只测试变量定义模式
  python test/test_lexer.py --list-functions    # 列出所有支持的函数
  python test/test_lexer.py --list-patterns     # 列出所有支持的测试模式

支持的函数:
  {', '.join(get_all_functions())}

支持的测试模式:
  {', '.join(get_all_patterns())}
        """
    )
    
    parser.add_argument(
        '-f', '--function',
        type=str,
        metavar='FUNC',
        help='只运行指定函数的测试'
    )
    
    parser.add_argument(
        '-p', '--pattern',
        type=str,
        metavar='PATTERN',
        help='只运行匹配该模式的基础测试'
    )
    
    parser.add_argument(
        '-c', '--test-case',
        type=str,
        metavar='NAME',
        help='只运行指定名称的测试用例'
    )
    
    parser.add_argument(
        '--list-functions',
        action='store_true',
        help='列出所有支持的函数名称'
    )
    
    parser.add_argument(
        '--list-patterns',
        action='store_true',
        help='列出所有支持的测试模式'
    )
    
    args = parser.parse_args()
    
    if args.list_functions:
        print("支持的函数名称:")
        for f in get_all_functions():
            print(f"  - {f}")
        return 0
    
    if args.list_patterns:
        print("支持的测试模式:")
        for p in get_all_patterns():
            print(f"  - {p}")
        return 0
    
    passed, failed, _ = run_tests(
        func_name=args.function,
        pattern=args.pattern,
        test_case=args.test_case
    )
    
    if failed == 0:
        print("\n🎉 所有测试通过!")
    else:
        print(f"\n❌ 有 {failed} 个测试失败")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
