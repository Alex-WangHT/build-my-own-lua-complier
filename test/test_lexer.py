#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lexer 模块单元测试 - 支持自动化注册测试用例

该模块支持以下测试方式：
1. 使用装饰器 @test_case 自动注册普通测试用例
2. 使用装饰器 @function_test(func) 自动注册按函数分类的测试用例
3. 使用装饰器 @pattern_test(pattern) 自动注册按测试模式分类的测试用例
4. 按函数名前缀 test_ 自动发现测试用例
5. 手动注册（向后兼容）

使用方法:
    python test/test_lexer.py                    # 运行所有测试
    python test/test_lexer.py --function _handle_number  # 只测试指定函数
    python test/test_lexer.py --pattern "变量定义"        # 只测试指定模式
    python test/test_lexer.py --list-functions             # 列出所有函数
"""

import sys
import os
import argparse
import inspect
from typing import Dict, List, Tuple, Callable, Optional

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from lexer import Lexer
from token import TokenType, Token


# ============================================================================
# 测试用例装饰器系统 - 自动化注册
# ============================================================================

# 存储自动注册的测试用例
_general_tests: List[Tuple[str, Callable]] = []
_function_tests: Dict[str, List[Tuple[str, Callable]]] = {}
_pattern_tests: Dict[str, List[Tuple[str, Callable]]] = {}


def test_case(name: Optional[str] = None):
    """
    测试用例装饰器 - 自动注册普通测试用例

    使用示例:
        @test_case("测试名称")
        def test_something():
            assert True

        @test_case()  # 自动使用函数名作为测试名称
        def test_another():
            assert True

    Args:
        name (str, optional): 测试用例名称，如果不提供则使用函数名
    """
    def decorator(func: Callable) -> Callable:
        # 确定测试名称
        test_name = name if name else func.__name__
        
        # 自动注册到通用测试列表
        _general_tests.append((test_name, func))
        
        return func
    
    # 处理两种使用方式：@test_case 和 @test_case("name")
    if callable(name):
        # 直接装饰：@test_case
        func = name
        return decorator(func)
    else:
        # 带参数：@test_case("name")
        return decorator


def function_test(function_name: str, name: Optional[str] = None):
    """
    函数测试装饰器 - 自动注册按函数分类的测试用例

    使用示例:
        @function_test("_handle_number", "整数解析")
        def test_number_int():
            assert True

        @function_test("_handle_number")  # 自动使用函数名作为测试名称
        def test_number_float():
            assert True

    Args:
        function_name (str): 函数名称（如 "_handle_number", "tokenize" 等）
        name (str, optional): 测试用例名称，如果不提供则使用函数名
    """
    def decorator(func: Callable) -> Callable:
        # 确定测试名称
        test_name = name if name else func.__name__
        
        # 自动注册到对应函数的测试列表
        if function_name not in _function_tests:
            _function_tests[function_name] = []
        _function_tests[function_name].append((test_name, func))
        
        return func
    
    return decorator


def pattern_test(pattern: str, name: Optional[str] = None):
    """
    测试模式装饰器 - 自动注册按测试模式分类的测试用例

    使用示例:
        @pattern_test("变量定义", "局部变量声明")
        def test_local_var():
            assert True

        @pattern_test("变量定义")  # 自动使用函数名作为测试名称
        def test_local_multi():
            assert True

    Args:
        pattern (str): 测试模式名称（如 "变量定义", "字符串" 等）
        name (str, optional): 测试用例名称，如果不提供则使用函数名
    """
    def decorator(func: Callable) -> Callable:
        # 确定测试名称
        test_name = name if name else func.__name__
        
        # 自动注册到对应测试模式的测试列表
        if pattern not in _pattern_tests:
            _pattern_tests[pattern] = []
        _pattern_tests[pattern].append((test_name, func))
        
        return func
    
    return decorator


def auto_discover_tests(module_name: str = __name__):
    """
    自动发现测试用例 - 按函数名前缀 test_ 发现

    该函数会扫描当前模块，找到所有以 test_ 开头的函数，
    并尝试根据函数名自动分类：
    - test_handle_number_xxx → 自动注册到 function: _handle_number
    - test_tokenize_xxx → 自动注册到 function: tokenize
    - test_xxx → 通用测试

    Args:
        module_name (str): 模块名称，默认为当前模块
    """
    import sys
    
    module = sys.modules.get(module_name)
    if not module:
        return
    
    # 有效函数名称映射
    valid_functions = {
        'handle_number': '_handle_number',
        'handle_string': '_handle_string',
        'handle_identifier': '_handle_identifier',
        'handle_operator': '_handle_operator',
        'handle_keyword': '_handle_keyword',
        'init_rules': '_init_default_rules',
        'add_rule': 'add_rule',
        'tokenize': 'tokenize',
        'get_next_token': 'get_next_token',
    }
    
    # 遍历模块中的所有成员
    for name, obj in inspect.getmembers(module):
        # 只处理函数，且以 test_ 开头
        if inspect.isfunction(obj) and name.startswith("test_"):
            # 尝试根据函数名自动分类
            parts = name.split("_")
            if len(parts) >= 2:
                # 检查是否是函数测试
                # 格式：test_{function}_{name} 或 test_{function}
                possible_func = "_".join(parts[1:-1]) if len(parts) > 2 else parts[1]
                
                # 检查是否是有效的函数名（去除下划线）
                func_key = "_".join(parts[1:])
                func_key_clean = func_key.replace("_", "")
                
                for alias, real_name in valid_functions.items():
                    alias_clean = alias.replace("_", "")
                    real_clean = real_name.replace("_", "")
                    
                    if (alias_clean in func_key_clean.lower() or 
                        real_clean in func_key_clean.lower()):
                        # 提取测试名称
                        if len(parts) >= 3:
                            test_name = " ".join(parts[2:]).replace("_", " ").title()
                        else:
                            test_name = name.replace("_", " ").title()
                        
                        # 注册到对应函数
                        if real_name not in _function_tests:
                            _function_tests[real_name] = []
                        _function_tests[real_name].append((test_name, obj))
                        continue
            
            # 默认注册为通用测试
            test_name = name.replace("_", " ").title()
            _general_tests.append((test_name, obj))


# ============================================================================
# 测试用例获取函数 - 支持自动发现和手动注册
# ============================================================================

def get_general_test_cases() -> List[Tuple[str, Callable]]:
    """
    获取通用测试用例列表

    优先返回装饰器注册的测试用例，如果没有则尝试自动发现。

    Returns:
        List[Tuple[str, Callable]]: 测试用例列表
    """
    if not _general_tests:
        auto_discover_tests()
    
    return _general_tests.copy()


def get_function_test_cases() -> Dict[str, List[Tuple[str, Callable]]]:
    """
    获取按函数分类的测试用例

    优先返回装饰器注册的测试用例，如果没有则尝试自动发现。

    Returns:
        Dict[str, List[Tuple[str, Callable]]]: 按函数分类的测试用例字典
    """
    if not _function_tests:
        auto_discover_tests()
    
    return {k: v.copy() for k, v in _function_tests.items()}


def get_pattern_test_cases() -> Dict[str, List[Tuple[str, Callable]]]:
    """
    获取按测试模式分类的测试用例

    优先返回装饰器注册的测试用例。

    Returns:
        Dict[str, List[Tuple[str, Callable]]]: 按测试模式分类的测试用例字典
    """
    return {k: v.copy() for k, v in _pattern_tests.items()}


def get_all_functions() -> List[str]:
    """
    获取所有支持的函数名称

    Returns:
        List[str]: 函数名称列表
    """
    if not _function_tests:
        get_function_test_cases()
    
    return list(_function_tests.keys())


def get_all_patterns() -> List[str]:
    """
    获取所有支持的测试模式

    Returns:
        List[str]: 测试模式列表
    """
    return list(_pattern_tests.keys())


def add_general_test(name: str, func: Callable):
    """
    手动添加通用测试用例（向后兼容）

    Args:
        name (str): 测试用例名称
        func (Callable): 测试函数
    """
    _general_tests.append((name, func))


def add_function_test(function_name: str, name: str, func: Callable):
    """
    手动添加函数测试用例（向后兼容）

    Args:
        function_name (str): 函数名称
        name (str): 测试用例名称
        func (Callable): 测试函数
    """
    if function_name not in _function_tests:
        _function_tests[function_name] = []
    _function_tests[function_name].append((name, func))


def add_pattern_test(pattern: str, name: str, func: Callable):
    """
    手动添加测试模式用例（向后兼容）

    Args:
        pattern (str): 测试模式
        name (str): 测试用例名称
        func (Callable): 测试函数
    """
    if pattern not in _pattern_tests:
        _pattern_tests[pattern] = []
    _pattern_tests[pattern].append((name, func))


# ============================================================================
# 测试用例 - 使用装饰器自动注册
# ============================================================================

# ------------------------------
# 通用测试用例
# ------------------------------

@test_case("Lexer初始化")
def test_lexer_init() -> bool:
    """测试 Lexer 初始化"""
    try:
        lexer = Lexer()
        assert lexer.pos == 0
        assert lexer.line == 1
        assert lexer.column == 1
        assert lexer.source == ""
        print(f"  PASS: Lexer 初始化成功")
        return True
    except Exception as e:
        print(f"  FAIL: Lexer 初始化失败 - {e}")
        return False


@test_case("Lexer重置")
def test_lexer_reset() -> bool:
    """测试 Lexer 重置"""
    try:
        lexer = Lexer("local x = 10")
        lexer.tokenize()
        assert lexer.pos > 0
        
        lexer.reset("local y = 20")
        assert lexer.pos == 0
        assert lexer.line == 1
        assert lexer.column == 1
        assert lexer.source == "local y = 20"
        print(f"  PASS: Lexer 重置成功")
        return True
    except Exception as e:
        print(f"  FAIL: Lexer 重置失败 - {e}")
        return False


# ------------------------------
# _handle_number 函数测试用例
# ------------------------------

@function_test("_handle_number", "整数解析")
@pattern_test("数字", "整数解析")
def test_handle_number_int() -> bool:
    """测试整数解析"""
    try:
        lexer = Lexer("42")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 42
        print(f"  PASS: 整数解析成功 - 42 → {tokens[0].value}")
        return True
    except Exception as e:
        print(f"  FAIL: 整数解析失败 - {e}")
        return False


@function_test("_handle_number", "浮点数解析")
@pattern_test("数字", "浮点数解析")
def test_handle_number_float() -> bool:
    """测试浮点数解析"""
    try:
        lexer = Lexer("3.14159")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.NUMBER
        assert abs(tokens[0].value - 3.14159) < 0.0001
        print(f"  PASS: 浮点数解析成功 - 3.14159 → {tokens[0].value}")
        return True
    except Exception as e:
        print(f"  FAIL: 浮点数解析失败 - {e}")
        return False


@function_test("_handle_number", "十六进制解析")
@pattern_test("数字", "十六进制解析")
def test_handle_number_hex() -> bool:
    """测试十六进制解析"""
    try:
        lexer = Lexer("0xFF")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 255
        print(f"  PASS: 十六进制解析成功 - 0xFF → {tokens[0].value}")
        return True
    except Exception as e:
        print(f"  FAIL: 十六进制解析失败 - {e}")
        return False


@function_test("_handle_number", "科学计数法解析")
@pattern_test("数字", "科学计数法解析")
def test_handle_number_scientific() -> bool:
    """测试科学计数法解析"""
    try:
        lexer = Lexer("1e10")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 1e10
        print(f"  PASS: 科学计数法解析成功 - 1e10 → {tokens[0].value}")
        return True
    except Exception as e:
        print(f"  FAIL: 科学计数法解析失败 - {e}")
        return False


# ------------------------------
# _handle_string 函数测试用例
# ------------------------------

@function_test("_handle_string", "双引号字符串")
@pattern_test("字符串", "双引号字符串")
def test_handle_string_double() -> bool:
    """测试双引号字符串"""
    try:
        lexer = Lexer('"hello world"')
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "hello world"
        print(f"  PASS: 双引号字符串解析成功 - {tokens[0].value!r}")
        return True
    except Exception as e:
        print(f"  FAIL: 双引号字符串解析失败 - {e}")
        return False


@function_test("_handle_string", "单引号字符串")
@pattern_test("字符串", "单引号字符串")
def test_handle_string_single() -> bool:
    """测试单引号字符串"""
    try:
        lexer = Lexer("'hello world'")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "hello world"
        print(f"  PASS: 单引号字符串解析成功 - {tokens[0].value!r}")
        return True
    except Exception as e:
        print(f"  FAIL: 单引号字符串解析失败 - {e}")
        return False


@function_test("_handle_string", "转义字符处理")
@pattern_test("字符串", "转义字符处理")
def test_handle_string_escape() -> bool:
    """测试转义字符处理"""
    try:
        lexer = Lexer('"hello\\nworld"')
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.STRING
        print(f"  PASS: 转义字符处理成功 - {tokens[0].value!r}")
        return True
    except Exception as e:
        print(f"  FAIL: 转义字符处理失败 - {e}")
        return False


@function_test("_handle_string", "空字符串")
@pattern_test("字符串", "空字符串")
def test_handle_string_empty() -> bool:
    """测试空字符串"""
    try:
        lexer = Lexer('""')
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == ""
        print(f"  PASS: 空字符串解析成功 - {tokens[0].value!r}")
        return True
    except Exception as e:
        print(f"  FAIL: 空字符串解析失败 - {e}")
        return False


# ------------------------------
# _handle_identifier 函数测试用例
# ------------------------------

@function_test("_handle_identifier", "普通标识符")
@pattern_test("标识符", "普通标识符")
def test_handle_identifier_normal() -> bool:
    """测试普通标识符"""
    try:
        lexer = Lexer("myVariable")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "myVariable"
        print(f"  PASS: 普通标识符解析成功 - {tokens[0].value}")
        return True
    except Exception as e:
        print(f"  FAIL: 普通标识符解析失败 - {e}")
        return False


@function_test("_handle_identifier", "关键字识别")
@pattern_test("关键字", "关键字识别")
def test_handle_identifier_keyword() -> bool:
    """测试关键字识别"""
    try:
        lexer = Lexer("local function if else while for return end")
        tokens = lexer.tokenize()
        expected_types = [
            TokenType.LOCAL, TokenType.FUNCTION, TokenType.IF,
            TokenType.ELSE, TokenType.WHILE, TokenType.FOR,
            TokenType.RETURN, TokenType.END
        ]
        for i, token in enumerate(tokens):
            assert token.type == expected_types[i], f"期望 {expected_types[i]}, 实际 {token.type}"
        print(f"  PASS: 关键字识别成功 - {len(tokens)} 个关键字")
        return True
    except Exception as e:
        print(f"  FAIL: 关键字识别失败 - {e}")
        return False


@function_test("_handle_identifier", "布尔值识别")
@pattern_test("关键字", "布尔值识别")
def test_handle_identifier_boolean() -> bool:
    """测试布尔值识别"""
    try:
        lexer = Lexer("true false")
        tokens = lexer.tokenize()
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.BOOLEAN
        assert tokens[0].value == True
        assert tokens[1].type == TokenType.BOOLEAN
        assert tokens[1].value == False
        print(f"  PASS: 布尔值识别成功 - true={tokens[0].value}, false={tokens[1].value}")
        return True
    except Exception as e:
        print(f"  FAIL: 布尔值识别失败 - {e}")
        return False


@function_test("_handle_identifier", "nil识别")
@pattern_test("关键字", "nil识别")
def test_handle_identifier_nil() -> bool:
    """测试 nil 识别"""
    try:
        lexer = Lexer("nil")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.NIL
        assert tokens[0].value is None
        print(f"  PASS: nil 识别成功 - {tokens[0].value}")
        return True
    except Exception as e:
        print(f"  FAIL: nil 识别失败 - {e}")
        return False


# ------------------------------
# _handle_operator 函数测试用例
# ------------------------------

@function_test("_handle_operator", "单字符运算符")
@pattern_test("运算符", "单字符运算符")
def test_handle_operator_single() -> bool:
    """测试单字符运算符"""
    try:
        lexer = Lexer("+ - * / = < >")
        tokens = lexer.tokenize()
        assert len(tokens) == 7
        print(f"  PASS: 单字符运算符解析成功 - {len(tokens)} 个运算符")
        return True
    except Exception as e:
        print(f"  FAIL: 单字符运算符解析失败 - {e}")
        return False


@function_test("_handle_operator", "双字符运算符")
@pattern_test("运算符", "双字符运算符")
def test_handle_operator_double() -> bool:
    """测试双字符运算符"""
    try:
        lexer = Lexer("== ~= <= >= ..")
        tokens = lexer.tokenize()
        assert len(tokens) == 5
        print(f"  PASS: 双字符运算符解析成功 - {len(tokens)} 个运算符")
        return True
    except Exception as e:
        print(f"  FAIL: 双字符运算符解析失败 - {e}")
        return False


# ------------------------------
# tokenize 函数测试用例
# ------------------------------

@function_test("tokenize", "完整词法分析")
@pattern_test("变量定义", "局部变量声明")
def test_tokenize_local_var() -> bool:
    """测试局部变量声明"""
    try:
        lexer = Lexer("local x = 10")
        tokens = lexer.tokenize()
        assert len(tokens) == 4
        assert tokens[0].type == TokenType.LOCAL
        assert tokens[1].type == TokenType.IDENTIFIER
        assert tokens[2].type == TokenType.OP_EQ
        assert tokens[3].type == TokenType.NUMBER
        print(f"  PASS: 局部变量声明分析成功 - {len(tokens)} 个 Token")
        return True
    except Exception as e:
        print(f"  FAIL: 局部变量声明分析失败 - {e}")
        return False


@function_test("tokenize", "多变量声明")
@pattern_test("变量定义", "多变量声明")
def test_tokenize_local_multi() -> bool:
    """测试多变量声明"""
    try:
        lexer = Lexer("local x, y = 10, 20")
        tokens = lexer.tokenize()
        assert len(tokens) >= 4
        print(f"  PASS: 多变量声明分析成功 - {len(tokens)} 个 Token")
        return True
    except Exception as e:
        print(f"  FAIL: 多变量声明分析失败 - {e}")
        return False


@function_test("tokenize", "函数定义")
@pattern_test("函数", "函数定义")
def test_tokenize_function() -> bool:
    """测试函数定义"""
    try:
        lexer = Lexer("function add(a, b) return a + b end")
        tokens = lexer.tokenize()
        assert len(tokens) >= 5
        assert tokens[0].type == TokenType.FUNCTION
        print(f"  PASS: 函数定义分析成功 - {len(tokens)} 个 Token")
        return True
    except Exception as e:
        print(f"  FAIL: 函数定义分析失败 - {e}")
        return False


@function_test("tokenize", "空源代码")
def test_tokenize_empty() -> bool:
    """测试空源代码"""
    try:
        lexer = Lexer("")
        tokens = lexer.tokenize()
        assert len(tokens) == 0
        print(f"  PASS: 空源代码分析成功 - {len(tokens)} 个 Token")
        return True
    except Exception as e:
        print(f"  FAIL: 空源代码分析失败 - {e}")
        return False


@function_test("tokenize", "注释跳过")
@pattern_test("注释", "单行注释")
def test_tokenize_comment() -> bool:
    """测试注释跳过"""
    try:
        lexer = Lexer("local x = 10 -- 这是注释")
        tokens = lexer.tokenize()
        assert len(tokens) == 4
        print(f"  PASS: 注释跳过成功 - {len(tokens)} 个 Token")
        return True
    except Exception as e:
        print(f"  FAIL: 注释跳过失败 - {e}")
        return False


# ------------------------------
# get_next_token 函数测试用例
# ------------------------------

@function_test("get_next_token", "逐个获取Token")
def test_get_next_token() -> bool:
    """测试逐个获取 Token"""
    try:
        lexer = Lexer("local x = 10")
        tokens = []
        while True:
            token = lexer.get_next_token()
            if token.type == TokenType.EOF:
                break
            tokens.append(token)
        
        assert len(tokens) == 4
        assert tokens[0].type == TokenType.LOCAL
        print(f"  PASS: 逐个获取 Token 成功 - {len(tokens)} 个 Token")
        return True
    except Exception as e:
        print(f"  FAIL: 逐个获取 Token 失败 - {e}")
        return False


# ------------------------------
# add_rule 函数测试用例
# ------------------------------

@function_test("add_rule", "添加自定义规则")
def test_add_rule() -> bool:
    """测试添加自定义规则"""
    try:
        from token import TokenType, Token, LexerRule
        
        lexer = Lexer()
        
        def custom_handler(text, line, col):
            return Token(TokenType.IDENTIFIER, "CUSTOM_" + text, line, col, text)
        
        lexer.add_rule(LexerRule(
            name='custom_identifier',
            pattern=r'[A-Z][A-Z0-9]*',
            handler=custom_handler,
            priority=100
        ))
        
        lexer.reset("HELLO")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].value == "CUSTOM_HELLO"
        print(f"  PASS: 添加自定义规则成功 - {tokens[0].value}")
        return True
    except Exception as e:
        print(f"  FAIL: 添加自定义规则失败 - {e}")
        return False


# ============================================================================
# 测试运行函数
# ============================================================================

def run_general_tests() -> Tuple[int, int, List[Tuple[str, bool]]]:
    """
    运行通用测试

    Returns:
        Tuple[int, int, List[Tuple[str, bool]]]: (通过数, 失败数, 结果列表)
    """
    test_cases = get_general_test_cases()
    passed = 0
    failed = 0
    results = []

    print("=" * 60)
    print("Lexer 模块 - 通用测试")
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


def run_function_tests(function_name: Optional[str] = None) -> Tuple[int, int, List[Tuple[str, bool]]]:
    """
    运行指定函数的测试

    Args:
        function_name (str, optional): 函数名称，如果为 None 则运行所有函数

    Returns:
        Tuple[int, int, List[Tuple[str, bool]]]: (通过数, 失败数, 结果列表)
    """
    func_test_cases = get_function_test_cases()
    
    if function_name:
        if function_name not in func_test_cases:
            print(f"错误: 未知的函数 '{function_name}'")
            print(f"支持的函数: {', '.join(get_all_functions())}")
            return 0, 1, []
        
        test_cases = {function_name: func_test_cases[function_name]}
    else:
        test_cases = func_test_cases

    passed = 0
    failed = 0
    results = []

    if function_name:
        print("=" * 60)
        print(f"Lexer 模块 - {function_name} 函数测试")
        print("=" * 60)
    else:
        print("=" * 60)
        print("Lexer 模块 - 所有函数测试")
        print("=" * 60)

    for func_name, tests in test_cases.items():
        print(f"\n[{func_name}]")
        for name, test_func in tests:
            print(f"\n  测试: {name}")
            try:
                if test_func():
                    passed += 1
                    results.append((f"{func_name}: {name}", True))
                else:
                    failed += 1
                    results.append((f"{func_name}: {name}", False))
            except Exception as e:
                print(f"    FAIL: 异常 - {e}")
                failed += 1
                results.append((f"{func_name}: {name}", False))

    return passed, failed, results


def run_pattern_tests(pattern: Optional[str] = None) -> Tuple[int, int, List[Tuple[str, bool]]]:
    """
    运行指定测试模式的测试

    Args:
        pattern (str, optional): 测试模式，如果为 None 则运行所有模式

    Returns:
        Tuple[int, int, List[Tuple[str, bool]]]: (通过数, 失败数, 结果列表)
    """
    pattern_test_cases = get_pattern_test_cases()
    
    if not pattern_test_cases:
        print("提示: 没有定义测试模式的测试用例")
        return 0, 0, []
    
    if pattern:
        if pattern not in pattern_test_cases:
            print(f"错误: 未知的测试模式 '{pattern}'")
            print(f"支持的模式: {', '.join(get_all_patterns())}")
            return 0, 1, []
        
        test_cases = {pattern: pattern_test_cases[pattern]}
    else:
        test_cases = pattern_test_cases

    passed = 0
    failed = 0
    results = []

    if pattern:
        print("=" * 60)
        print(f"Lexer 模块 - {pattern} 模式测试")
        print("=" * 60)
    else:
        print("=" * 60)
        print("Lexer 模块 - 所有模式测试")
        print("=" * 60)

    for pattern_name, tests in test_cases.items():
        print(f"\n[{pattern_name}]")
        for name, test_func in tests:
            print(f"\n  测试: {name}")
            try:
                if test_func():
                    passed += 1
                    results.append((f"{pattern_name}: {name}", True))
                else:
                    failed += 1
                    results.append((f"{pattern_name}: {name}", False))
            except Exception as e:
                print(f"    FAIL: 异常 - {e}")
                failed += 1
                results.append((f"{pattern_name}: {name}", False))

    return passed, failed, results


def run_tests(function_name: Optional[str] = None, 
              pattern: Optional[str] = None,
              test_case: Optional[str] = None) -> Tuple[int, int, List[Tuple[str, bool]]]:
    """
    运行测试

    Args:
        function_name (str, optional): 只运行指定函数的测试
        pattern (str, optional): 只运行指定测试模式的测试
        test_case (str, optional): 只运行指定名称的测试用例

    Returns:
        Tuple[int, int, List[Tuple[str, bool]]]: (通过数, 失败数, 结果列表)
    """
    if test_case:
        print("=" * 60)
        print(f"Lexer 模块 - 特定测试用例: {test_case}")
        print("=" * 60)
        
        # 构建所有测试用例的查找表
        all_test_cases = {}
        
        for name, func in get_general_test_cases():
            all_test_cases[name] = func
        
        for func_name, tests in get_function_test_cases().items():
            for name, func in tests:
                all_test_cases[f"{func_name}: {name}"] = func
        
        for pattern_name, tests in get_pattern_test_cases().items():
            for name, func in tests:
                all_test_cases[f"{pattern_name}: {name}"] = func
        
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
    
    if function_name:
        return run_function_tests(function_name)
    elif pattern:
        return run_pattern_tests(pattern)
    else:
        general_passed, general_failed, general_results = run_general_tests()
        func_passed, func_failed, func_results = run_function_tests()
        
        total_passed = general_passed + func_passed
        total_failed = general_failed + func_failed
        
        print("\n" + "=" * 60)
        print(f"总测试结果")
        print("=" * 60)
        print(f"通用测试: 通过 {general_passed}, 失败 {general_failed}")
        print(f"函数测试: 通过 {func_passed}, 失败 {func_failed}")
        print(f"总计: 通过 {total_passed}, 失败 {total_failed}")
        print("=" * 60)
        
        return total_passed, total_failed, general_results + func_results


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Lexer 模块单元测试 - 支持自动化注册',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
使用示例:
  # 运行所有测试
  python test/test_lexer.py
  
  # 只测试指定函数
  python test/test_lexer.py --function _handle_number
  python test/test_lexer.py --function tokenize
  
  # 只测试指定测试模式
  python test/test_lexer.py --pattern "变量定义"
  python test/test_lexer.py --pattern "字符串"
  
  # 只运行指定测试用例
  python test/test_lexer.py --test-case "Lexer初始化"
  
  # 列出所有支持的函数
  python test/test_lexer.py --list-functions
  
  # 列出所有支持的测试模式
  python test/test_lexer.py --list-patterns

测试用例注册方式:
  1. 使用装饰器自动注册（推荐）:
     @test_case("测试名称")
     def test_something():
         pass
     
     @function_test("_handle_number", "测试名称")
     def test_number():
         pass
     
     @pattern_test("变量定义", "测试名称")
     def test_local_var():
         pass
  
  2. 按函数名自动发现:
     def test_lexer_xxx():  # 自动注册为通用测试
         pass
     
     def test_handle_number_xxx():  # 自动注册到 function: _handle_number
         pass

支持的函数:
  {', '.join(get_all_functions())}

支持的测试模式:
  {', '.join(get_all_patterns()) if get_all_patterns() else '(无)'}
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
        help='只运行指定测试模式的测试'
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
        help='列出所有支持的函数'
    )
    
    parser.add_argument(
        '--list-patterns',
        action='store_true',
        help='列出所有支持的测试模式'
    )
    
    args = parser.parse_args()
    
    if args.list_functions:
        print("支持的函数:")
        for f in get_all_functions():
            print(f"  - {f}")
        return 0
    
    if args.list_patterns:
        patterns = get_all_patterns()
        if patterns:
            print("支持的测试模式:")
            for p in patterns:
                print(f"  - {p}")
        else:
            print("没有定义测试模式的测试用例")
        return 0
    
    passed, failed, _ = run_tests(
        function_name=args.function,
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
