#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Token 模块单元测试 - 支持自动化注册测试用例

该模块支持以下测试方式：
1. 使用装饰器 @test_case 自动注册普通测试用例
2. 使用装饰器 @token_type_test(type) 自动注册按类型分类的测试用例
3. 按函数名前缀 test_ 自动发现测试用例
4. 手动注册（向后兼容）

使用方法:
    python test/test_token.py                    # 运行所有测试
    python test/test_token.py --token-type NUMBER  # 只测试 NUMBER 类型
    python test/test_token.py --list-types         # 列出所有 Token 类型
"""

import sys
import os
import argparse
import inspect
from typing import Dict, List, Tuple, Callable, Optional

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from token import TokenType, Token, LexerRule


# ============================================================================
# 测试用例装饰器系统 - 自动化注册
# ============================================================================

# 存储自动注册的测试用例
_general_tests: List[Tuple[str, Callable]] = []
_token_type_tests: Dict[str, List[Tuple[str, Callable]]] = {}


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


def token_type_test(token_type: str, name: Optional[str] = None):
    """
    Token 类型测试装饰器 - 自动注册按类型分类的测试用例

    使用示例:
        @token_type_test("NUMBER", "整数解析")
        def test_number_int():
            assert True

        @token_type_test("NUMBER")  # 自动使用函数名作为测试名称
        def test_number_float():
            assert True

    Args:
        token_type (str): Token 类型名称（如 "NUMBER", "STRING" 等）
        name (str, optional): 测试用例名称，如果不提供则使用函数名
    """
    def decorator(func: Callable) -> Callable:
        # 确定测试名称
        test_name = name if name else func.__name__
        
        # 自动注册到对应 Token 类型的测试列表
        if token_type not in _token_type_tests:
            _token_type_tests[token_type] = []
        _token_type_tests[token_type].append((test_name, func))
        
        return func
    
    return decorator


def auto_discover_tests(module_name: str = __name__):
    """
    自动发现测试用例 - 按函数名前缀 test_ 发现

    该函数会扫描当前模块，找到所有以 test_ 开头的函数，
    并尝试根据函数名自动分类：
    - test_number_xxx → NUMBER 类型
    - test_string_xxx → STRING 类型
    - test_xxx → 通用测试

    Args:
        module_name (str): 模块名称，默认为当前模块
    """
    import sys
    
    module = sys.modules.get(module_name)
    if not module:
        return
    
    # 遍历模块中的所有成员
    for name, obj in inspect.getmembers(module):
        # 只处理函数，且以 test_ 开头
        if inspect.isfunction(obj) and name.startswith("test_"):
            # 检查是否已经被装饰器注册过（通过检查函数属性）
            if hasattr(obj, '_registered'):
                continue
            
            # 尝试根据函数名自动分类
            parts = name.split("_")
            if len(parts) >= 2:
                # 检查是否是 Token 类型测试
                # 格式：test_{TYPE}_{name} 或 test_{TYPE}
                possible_type = parts[1].upper()
                
                # 检查是否是有效的 Token 类型
                valid_types = ['NUMBER', 'STRING', 'IDENTIFIER', 'BOOLEAN', 
                              'NIL', 'EOF', 'KEYWORD', 'OPERATOR', 'LOCAL',
                              'FUNCTION', 'IF', 'ELSE', 'WHILE', 'FOR']
                
                if possible_type in valid_types:
                    # 提取测试名称
                    if len(parts) >= 3:
                        test_name = " ".join(parts[2:]).replace("_", " ").title()
                    else:
                        test_name = name.replace("_", " ").title()
                    
                    # 注册到对应类型
                    if possible_type not in _token_type_tests:
                        _token_type_tests[possible_type] = []
                    _token_type_tests[possible_type].append((test_name, obj))
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
        List[Tuple[str, Callable]]: 测试用例列表，格式为 [(测试名称, 测试函数), ...]
    """
    # 如果没有装饰器注册的测试用例，尝试自动发现
    if not _general_tests:
        auto_discover_tests()
    
    return _general_tests.copy()


def get_token_type_test_cases() -> Dict[str, List[Tuple[str, Callable]]]:
    """
    获取按 Token 类型分类的测试用例

    优先返回装饰器注册的测试用例，如果没有则尝试自动发现。

    Returns:
        Dict[str, List[Tuple[str, Callable]]]: 按类型分类的测试用例字典
    """
    # 如果没有装饰器注册的测试用例，尝试自动发现
    if not _token_type_tests:
        auto_discover_tests()
    
    return {k: v.copy() for k, v in _token_type_tests.items()}


def get_all_token_types() -> List[str]:
    """
    获取所有支持的 Token 类型名称

    Returns:
        List[str]: Token 类型名称列表
    """
    # 确保测试用例已加载
    if not _token_type_tests:
        get_token_type_test_cases()
    
    return list(_token_type_tests.keys())


def add_general_test(name: str, func: Callable):
    """
    手动添加通用测试用例（向后兼容）

    Args:
        name (str): 测试用例名称
        func (Callable): 测试函数
    """
    _general_tests.append((name, func))


def add_token_type_test(token_type: str, name: str, func: Callable):
    """
    手动添加 Token 类型测试用例（向后兼容）

    Args:
        token_type (str): Token 类型名称
        name (str): 测试用例名称
        func (Callable): 测试函数
    """
    if token_type not in _token_type_tests:
        _token_type_tests[token_type] = []
    _token_type_tests[token_type].append((name, func))


# ============================================================================
# 测试用例 - 使用装饰器自动注册
# ============================================================================

# ------------------------------
# 通用测试用例
# ------------------------------

@test_case("TokenType枚举完整性")
def test_token_type_enum() -> bool:
    """测试 TokenType 枚举是否包含必要的类型"""
    required = ['EOF', 'NUMBER', 'STRING', 'IDENTIFIER', 'BOOLEAN', 'NIL',
                'LOCAL', 'FUNCTION', 'IF', 'ELSE', 'WHILE', 'FOR', 'RETURN', 'END']
    for req in required:
        if not hasattr(TokenType, req):
            print(f"  FAIL: 缺少 TokenType: {req}")
            return False
    print(f"  PASS: TokenType 包含 {len(TokenType)} 个类型")
    return True


@test_case("TokenType值唯一性")
def test_token_type_unique() -> bool:
    """测试 TokenType 值是否唯一"""
    try:
        values = [t.value for t in TokenType]
        assert len(values) == len(set(values))
        print(f"  PASS: TokenType 值唯一 ({len(values)} 个)")
        return True
    except Exception as e:
        print(f"  FAIL: TokenType 值不唯一 - {e}")
        return False


@test_case("TokenType比较")
def test_token_type_comparison() -> bool:
    """测试 TokenType 比较"""
    try:
        t1 = TokenType.NUMBER
        t2 = TokenType.NUMBER
        t3 = TokenType.STRING
        assert t1 == t2
        assert t1 != t3
        print(f"  PASS: TokenType 比较正确")
        return True
    except Exception as e:
        print(f"  FAIL: TokenType 比较失败 - {e}")
        return False


@test_case("LexerRule创建")
def test_lexer_rule_creation() -> bool:
    """测试 LexerRule 创建"""
    try:
        def dummy_handler(text, line, col):
            return Token(TokenType.NUMBER, int(text), line, col, text)
        
        rule = LexerRule(
            name='test_number',
            pattern=r'\d+',
            handler=dummy_handler,
            priority=10
        )
        assert rule.name == 'test_number'
        assert rule.pattern == r'\d+'
        assert rule.priority == 10
        print(f"  PASS: LexerRule 创建成功 - name={rule.name}")
        return True
    except Exception as e:
        print(f"  FAIL: LexerRule 创建失败 - {e}")
        return False


# ------------------------------
# NUMBER 类型测试用例
# ------------------------------

@token_type_test("NUMBER", "NUMBER类型Token创建")
def test_number_token_creation() -> bool:
    """测试 NUMBER 类型 Token 创建"""
    try:
        token = Token(TokenType.NUMBER, 42, line=1, column=5, raw="42")
        assert token.type == TokenType.NUMBER
        print(f"  PASS: NUMBER 类型 Token 创建成功")
        return True
    except Exception as e:
        print(f"  FAIL: NUMBER 类型 Token 创建失败 - {e}")
        return False


@token_type_test("NUMBER", "NUMBER类型值验证")
def test_number_token_value() -> bool:
    """测试 NUMBER 类型 Token 值验证"""
    try:
        token_int = Token(TokenType.NUMBER, 42)
        assert token_int.value == 42
        
        token_float = Token(TokenType.NUMBER, 3.14159)
        assert token_float.value == 3.14159
        
        token_hex = Token(TokenType.NUMBER, 0xFF)
        assert token_hex.value == 255
        
        print(f"  PASS: NUMBER 类型 Token 值验证成功")
        return True
    except Exception as e:
        print(f"  FAIL: NUMBER 类型 Token 值验证失败 - {e}")
        return False


# ------------------------------
# STRING 类型测试用例
# ------------------------------

@token_type_test("STRING", "STRING类型Token创建")
def test_string_token_creation() -> bool:
    """测试 STRING 类型 Token 创建"""
    try:
        token = Token(TokenType.STRING, "hello", line=1, column=1, raw='"hello"')
        assert token.type == TokenType.STRING
        print(f"  PASS: STRING 类型 Token 创建成功")
        return True
    except Exception as e:
        print(f"  FAIL: STRING 类型 Token 创建失败 - {e}")
        return False


@token_type_test("STRING", "STRING类型值验证")
def test_string_token_value() -> bool:
    """测试 STRING 类型 Token 值验证"""
    try:
        token1 = Token(TokenType.STRING, "hello world")
        assert token1.value == "hello world"
        
        token2 = Token(TokenType.STRING, "")
        assert token2.value == ""
        
        token3 = Token(TokenType.STRING, "line1\nline2")
        assert "\n" in token3.value
        
        print(f"  PASS: STRING 类型 Token 值验证成功")
        return True
    except Exception as e:
        print(f"  FAIL: STRING 类型 Token 值验证失败 - {e}")
        return False


# ------------------------------
# IDENTIFIER 类型测试用例
# ------------------------------

@token_type_test("IDENTIFIER", "IDENTIFIER类型Token创建")
def test_identifier_token_creation() -> bool:
    """测试 IDENTIFIER 类型 Token 创建"""
    try:
        token = Token(TokenType.IDENTIFIER, "myVar", line=1, column=1, raw="myVar")
        assert token.type == TokenType.IDENTIFIER
        assert token.value == "myVar"
        print(f"  PASS: IDENTIFIER 类型 Token 创建成功")
        return True
    except Exception as e:
        print(f"  FAIL: IDENTIFIER 类型 Token 创建失败 - {e}")
        return False


# ------------------------------
# BOOLEAN 类型测试用例
# ------------------------------

@token_type_test("BOOLEAN", "BOOLEAN类型Token创建")
def test_boolean_token_creation() -> bool:
    """测试 BOOLEAN 类型 Token 创建"""
    try:
        token_true = Token(TokenType.BOOLEAN, True, raw="true")
        assert token_true.type == TokenType.BOOLEAN
        
        token_false = Token(TokenType.BOOLEAN, False, raw="false")
        assert token_false.type == TokenType.BOOLEAN
        
        print(f"  PASS: BOOLEAN 类型 Token 创建成功")
        return True
    except Exception as e:
        print(f"  FAIL: BOOLEAN 类型 Token 创建失败 - {e}")
        return False


@token_type_test("BOOLEAN", "BOOLEAN类型True值验证")
def test_boolean_true_value() -> bool:
    """测试 BOOLEAN 类型 True 值验证"""
    try:
        token = Token(TokenType.BOOLEAN, True, raw="true")
        assert token.value is True
        assert token.raw == "true"
        print(f"  PASS: BOOLEAN 类型 True 值验证成功")
        return True
    except Exception as e:
        print(f"  FAIL: BOOLEAN 类型 True 值验证失败 - {e}")
        return False


@token_type_test("BOOLEAN", "BOOLEAN类型False值验证")
def test_boolean_false_value() -> bool:
    """测试 BOOLEAN 类型 False 值验证"""
    try:
        token = Token(TokenType.BOOLEAN, False, raw="false")
        assert token.value is False
        assert token.raw == "false"
        print(f"  PASS: BOOLEAN 类型 False 值验证成功")
        return True
    except Exception as e:
        print(f"  FAIL: BOOLEAN 类型 False 值验证失败 - {e}")
        return False


# ------------------------------
# NIL 类型测试用例
# ------------------------------

@token_type_test("NIL", "NIL类型Token创建")
def test_nil_token_creation() -> bool:
    """测试 NIL 类型 Token 创建"""
    try:
        token = Token(TokenType.NIL, None, raw="nil")
        assert token.type == TokenType.NIL
        print(f"  PASS: NIL 类型 Token 创建成功")
        return True
    except Exception as e:
        print(f"  FAIL: NIL 类型 Token 创建失败 - {e}")
        return False


@token_type_test("NIL", "NIL类型值验证")
def test_nil_token_value() -> bool:
    """测试 NIL 类型 Token 值验证"""
    try:
        token = Token(TokenType.NIL, None, raw="nil")
        assert token.value is None
        assert token.raw == "nil"
        print(f"  PASS: NIL 类型 Token 值验证成功")
        return True
    except Exception as e:
        print(f"  FAIL: NIL 类型 Token 值验证失败 - {e}")
        return False


# ------------------------------
# EOF 类型测试用例
# ------------------------------

@token_type_test("EOF", "EOF类型Token创建")
def test_eof_token_creation() -> bool:
    """测试 EOF 类型 Token 创建"""
    try:
        token = Token(TokenType.EOF, None, line=10, column=5)
        assert token.type == TokenType.EOF
        assert token.value is None
        print(f"  PASS: EOF 类型 Token 创建成功")
        return True
    except Exception as e:
        print(f"  FAIL: EOF 类型 Token 创建失败 - {e}")
        return False


# ------------------------------
# KEYWORD 类型测试用例
# ------------------------------

@token_type_test("KEYWORD", "LOCAL类型Token创建")
def test_local_token_creation() -> bool:
    """测试 LOCAL 类型 Token 创建"""
    try:
        token = Token(TokenType.LOCAL, "local", raw="local")
        assert token.type == TokenType.LOCAL
        assert token.value == "local"
        print(f"  PASS: LOCAL 类型 Token 创建成功")
        return True
    except Exception as e:
        print(f"  FAIL: LOCAL 类型 Token 创建失败 - {e}")
        return False


@token_type_test("KEYWORD", "FUNCTION类型Token创建")
def test_function_token_creation() -> bool:
    """测试 FUNCTION 类型 Token 创建"""
    try:
        token = Token(TokenType.FUNCTION, "function", raw="function")
        assert token.type == TokenType.FUNCTION
        print(f"  PASS: FUNCTION 类型 Token 创建成功")
        return True
    except Exception as e:
        print(f"  FAIL: FUNCTION 类型 Token 创建失败 - {e}")
        return False


@token_type_test("KEYWORD", "IF类型Token创建")
def test_if_token_creation() -> bool:
    """测试 IF 类型 Token 创建"""
    try:
        token = Token(TokenType.IF, "if", raw="if")
        assert token.type == TokenType.IF
        print(f"  PASS: IF 类型 Token 创建成功")
        return True
    except Exception as e:
        print(f"  FAIL: IF 类型 Token 创建失败 - {e}")
        return False


# ------------------------------
# OPERATOR 类型测试用例
# ------------------------------

@token_type_test("OPERATOR", "OP_PLUS类型Token")
def test_op_plus_token() -> bool:
    """测试 OP_PLUS 类型 Token"""
    try:
        token = Token(TokenType.OP_PLUS, "+", raw="+")
        assert token.type == TokenType.OP_PLUS
        assert token.value == "+"
        print(f"  PASS: OP_PLUS 类型 Token 创建成功")
        return True
    except Exception as e:
        print(f"  FAIL: OP_PLUS 类型 Token 创建失败 - {e}")
        return False


@token_type_test("OPERATOR", "OP_MINUS类型Token")
def test_op_minus_token() -> bool:
    """测试 OP_MINUS 类型 Token"""
    try:
        token = Token(TokenType.OP_MINUS, "-", raw="-")
        assert token.type == TokenType.OP_MINUS
        print(f"  PASS: OP_MINUS 类型 Token 创建成功")
        return True
    except Exception as e:
        print(f"  FAIL: OP_MINUS 类型 Token 创建失败 - {e}")
        return False


@token_type_test("OPERATOR", "OP_MULT类型Token")
def test_op_mult_token() -> bool:
    """测试 OP_MULT 类型 Token"""
    try:
        token = Token(TokenType.OP_MULT, "*", raw="*")
        assert token.type == TokenType.OP_MULT
        print(f"  PASS: OP_MULT 类型 Token 创建成功")
        return True
    except Exception as e:
        print(f"  FAIL: OP_MULT 类型 Token 创建失败 - {e}")
        return False


@token_type_test("OPERATOR", "OP_DIV类型Token")
def test_op_div_token() -> bool:
    """测试 OP_DIV 类型 Token"""
    try:
        token = Token(TokenType.OP_DIV, "/", raw="/")
        assert token.type == TokenType.OP_DIV
        print(f"  PASS: OP_DIV 类型 Token 创建成功")
        return True
    except Exception as e:
        print(f"  FAIL: OP_DIV 类型 Token 创建失败 - {e}")
        return False


@token_type_test("OPERATOR", "OP_EQ类型Token")
def test_op_eq_token() -> bool:
    """测试 OP_EQ 类型 Token"""
    try:
        token = Token(TokenType.OP_EQ, "==", raw="==")
        assert token.type == TokenType.OP_EQ
        print(f"  PASS: OP_EQ 类型 Token 创建成功")
        return True
    except Exception as e:
        print(f"  FAIL: OP_EQ 类型 Token 创建失败 - {e}")
        return False


@token_type_test("OPERATOR", "OP_NE类型Token")
def test_op_ne_token() -> bool:
    """测试 OP_NE 类型 Token"""
    try:
        token = Token(TokenType.OP_NE, "~=", raw="~=")
        assert token.type == TokenType.OP_NE
        print(f"  PASS: OP_NE 类型 Token 创建成功")
        return True
    except Exception as e:
        print(f"  FAIL: OP_NE 类型 Token 创建失败 - {e}")
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
    print("Token 模块 - 通用测试")
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


def run_token_type_tests(token_type: Optional[str] = None) -> Tuple[int, int, List[Tuple[str, bool]]]:
    """
    运行指定 Token 类型的测试

    Args:
        token_type (str, optional): Token 类型名称，如果为 None 则运行所有类型

    Returns:
        Tuple[int, int, List[Tuple[str, bool]]]: (通过数, 失败数, 结果列表)
    """
    type_test_cases = get_token_type_test_cases()
    
    if token_type:
        if token_type not in type_test_cases:
            print(f"错误: 未知的 Token 类型 '{token_type}'")
            print(f"支持的类型: {', '.join(get_all_token_types())}")
            return 0, 1, []
        
        test_cases = {token_type: type_test_cases[token_type]}
    else:
        test_cases = type_test_cases

    passed = 0
    failed = 0
    results = []

    if token_type:
        print("=" * 60)
        print(f"Token 模块 - {token_type} 类型测试")
        print("=" * 60)
    else:
        print("=" * 60)
        print("Token 模块 - 所有类型测试")
        print("=" * 60)

    for type_name, tests in test_cases.items():
        print(f"\n[{type_name}]")
        for name, test_func in tests:
            print(f"\n  测试: {name}")
            try:
                if test_func():
                    passed += 1
                    results.append((f"{type_name}: {name}", True))
                else:
                    failed += 1
                    results.append((f"{type_name}: {name}", False))
            except Exception as e:
                print(f"    FAIL: 异常 - {e}")
                failed += 1
                results.append((f"{type_name}: {name}", False))

    return passed, failed, results


def run_tests(token_type: Optional[str] = None, test_case: Optional[str] = None) -> Tuple[int, int, List[Tuple[str, bool]]]:
    """
    运行测试

    Args:
        token_type (str, optional): 只运行指定 Token 类型的测试
        test_case (str, optional): 只运行指定名称的测试用例

    Returns:
        Tuple[int, int, List[Tuple[str, bool]]]: (通过数, 失败数, 结果列表)
    """
    if test_case:
        print("=" * 60)
        print(f"Token 模块 - 特定测试用例: {test_case}")
        print("=" * 60)
        
        # 构建所有测试用例的查找表
        all_test_cases = {}
        
        for name, func in get_general_test_cases():
            all_test_cases[name] = func
        
        for type_name, tests in get_token_type_test_cases().items():
            for name, func in tests:
                all_test_cases[f"{type_name}: {name}"] = func
        
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
    
    if token_type:
        return run_token_type_tests(token_type)
    else:
        general_passed, general_failed, general_results = run_general_tests()
        type_passed, type_failed, type_results = run_token_type_tests()
        
        total_passed = general_passed + type_passed
        total_failed = general_failed + type_failed
        
        print("\n" + "=" * 60)
        print(f"总测试结果")
        print("=" * 60)
        print(f"通用测试: 通过 {general_passed}, 失败 {general_failed}")
        print(f"类型测试: 通过 {type_passed}, 失败 {type_failed}")
        print(f"总计: 通过 {total_passed}, 失败 {total_failed}")
        print("=" * 60)
        
        return total_passed, total_failed, general_results + type_results


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Token 模块单元测试 - 支持自动化注册',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
使用示例:
  # 运行所有测试
  python test/test_token.py
  
  # 只测试指定 Token 类型
  python test/test_token.py --token-type NUMBER
  python test/test_token.py --token-type STRING
  
  # 只运行指定测试用例
  python test/test_token.py --test-case "TokenType枚举完整性"
  
  # 列出所有支持的 Token 类型
  python test/test_token.py --list-types

测试用例注册方式:
  1. 使用装饰器自动注册（推荐）:
     @test_case("测试名称")
     def test_something():
         pass
     
     @token_type_test("NUMBER", "测试名称")
     def test_number():
         pass
  
  2. 按函数名自动发现:
     def test_token_type_xxx():  # 自动注册为通用测试
         pass
     
     def test_number_xxx():  # 自动注册到 NUMBER 类型
         pass

支持的 Token 类型:
  {', '.join(get_all_token_types())}
        """
    )
    
    parser.add_argument(
        '-t', '--token-type',
        type=str,
        metavar='TYPE',
        help='只运行指定 Token 类型的测试'
    )
    
    parser.add_argument(
        '-c', '--test-case',
        type=str,
        metavar='NAME',
        help='只运行指定名称的测试用例'
    )
    
    parser.add_argument(
        '--list-types',
        action='store_true',
        help='列出所有支持的 Token 类型'
    )
    
    args = parser.parse_args()
    
    if args.list_types:
        print("支持的 Token 类型:")
        for t in get_all_token_types():
            print(f"  - {t}")
        return 0
    
    passed, failed, _ = run_tests(
        token_type=args.token_type,
        test_case=args.test_case
    )
    
    if failed == 0:
        print("\n🎉 所有测试通过!")
    else:
        print(f"\n❌ 有 {failed} 个测试失败")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
