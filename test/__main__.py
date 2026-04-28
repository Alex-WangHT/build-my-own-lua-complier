#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试模块 CLI 入口

该模块提供命令行接口来运行各种测试，支持：
- 运行所有测试
- 只运行 token 模块测试
- 只运行 lexer 模块测试
- 按 Token 类型测试（如只测试 NUMBER、STRING 等）
- 按函数/方法测试（如只测试 _handle_number、_handle_string 等）
- 按测试模式测试
- 按特定测试用例测试
- 分析代码
- JSON 格式输出（用于自动化）

使用方法:
    python -m test              # 运行所有测试
    python -m test -m token     # 只运行 token 测试
    python -m test -m lexer     # 只运行 lexer 测试
    
    # Token 细粒度测试
    python -m test --token-type NUMBER
    python -m test --token-type STRING
    python -m test --list-token-types
    
    # Lexer 细粒度测试
    python -m test --function _handle_number
    python -m test --function _handle_string
    python -m test --pattern "变量定义"
    python -m test --list-functions
    python -m test --list-patterns
    
    # 代码分析
    python -m test -c "local x = 10"
    
    # JSON 输出（用于自动化）
    python -m test --json
    python -m test --token-type NUMBER --json
"""

import sys
import os
import argparse
import json

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

try:
    from test_token import (
        run_tests as run_token_tests,
        get_all_token_types as get_token_types,
        get_general_test_cases as get_token_general_cases,
        get_token_type_test_cases as get_token_type_cases,
    )
except ImportError:
    from .test_token import (
        run_tests as run_token_tests,
        get_all_token_types as get_token_types,
        get_general_test_cases as get_token_general_cases,
        get_token_type_test_cases as get_token_type_cases,
    )

try:
    from test_lexer import (
        run_tests as run_lexer_tests,
        get_all_functions as get_lexer_functions,
        get_all_patterns as get_lexer_patterns,
        get_basic_test_cases as get_lexer_basic_cases,
        get_function_test_cases as get_lexer_function_cases,
        get_advanced_test_cases as get_lexer_advanced_cases,
    )
except ImportError:
    from .test_lexer import (
        run_tests as run_lexer_tests,
        get_all_functions as get_lexer_functions,
        get_all_patterns as get_lexer_patterns,
        get_basic_test_cases as get_lexer_basic_cases,
        get_function_test_cases as get_lexer_function_cases,
        get_advanced_test_cases as get_lexer_advanced_cases,
    )


def analyze_code(source: str) -> dict:
    """
    分析 Lua 代码并返回 Token 信息

    Args:
        source (str): Lua 源代码

    Returns:
        dict: 包含 Token 列表的字典
    """
    from lexer import Lexer
    
    lexer = Lexer()
    tokens = lexer.tokenize(source)
    
    result = {
        'source': source,
        'token_count': len(tokens),
        'tokens': []
    }
    
    for token in tokens:
        result['tokens'].append({
            'type': token.type.name,
            'value': token.value,
            'line': token.line,
            'column': token.column,
            'raw': token.raw
        })
    
    return result


def run_all_tests() -> dict:
    """
    运行所有测试

    Returns:
        dict: 测试结果字典
    """
    print("=" * 60)
    print("运行所有测试")
    print("=" * 60)
    
    token_passed, token_failed, token_results = run_token_tests()
    lexer_passed, lexer_failed, lexer_results = run_lexer_tests()
    
    total_passed = token_passed + lexer_passed
    total_failed = token_failed + lexer_failed
    
    result = {
        'token': {
            'passed': token_passed,
            'failed': token_failed,
            'results': token_results
        },
        'lexer': {
            'passed': lexer_passed,
            'failed': lexer_failed,
            'results': lexer_results
        },
        'total': {
            'passed': total_passed,
            'failed': total_failed,
            'total': total_passed + total_failed
        }
    }
    
    return result


def run_token_tests_cli(token_type: str = None, test_case: str = None) -> dict:
    """
    运行 token 模块测试

    Args:
        token_type (str, optional): 只运行指定 Token 类型的测试
        test_case (str, optional): 只运行指定名称的测试用例

    Returns:
        dict: 测试结果字典
    """
    passed, failed, results = run_token_tests(
        token_type=token_type,
        test_case=test_case
    )
    
    return {
        'passed': passed,
        'failed': failed,
        'results': results,
        'total': passed + failed
    }


def run_lexer_tests_cli(func_name: str = None, pattern: str = None, test_case: str = None) -> dict:
    """
    运行 lexer 模块测试

    Args:
        func_name (str, optional): 只运行指定函数的测试
        pattern (str, optional): 只运行匹配该模式的基础测试
        test_case (str, optional): 只运行指定名称的测试用例

    Returns:
        dict: 测试结果字典
    """
    passed, failed, results = run_lexer_tests(
        func_name=func_name,
        pattern=pattern,
        test_case=test_case
    )
    
    return {
        'passed': passed,
        'failed': failed,
        'results': results,
        'total': passed + failed
    }


def get_all_test_cases() -> dict:
    """
    获取所有测试用例列表（用于 JSON 输出）

    Returns:
        dict: 包含所有测试用例的字典
    """
    return {
        'token': {
            'general': [name for name, _ in get_token_general_cases()],
            'by_type': {
                type_name: [name for name, _ in tests]
                for type_name, tests in get_token_type_cases().items()
            }
        },
        'lexer': {
            'basic': [name for name, _, _ in get_lexer_basic_cases()],
            'by_function': {
                func_name: [name for name, _ in tests]
                for func_name, tests in get_lexer_function_cases().items()
            },
            'advanced': [name for name, _ in get_lexer_advanced_cases()]
        }
    }


def main():
    """
    CLI 主函数
    """
    parser = argparse.ArgumentParser(
        description='Lua 解释器测试 CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
示例:
  # 运行所有测试
  python -m test
  python -m test -m all
  
  # 按模块测试
  python -m test -m token
  python -m test -m lexer
  
  # Token 细粒度测试
  python -m test --token-type NUMBER
  python -m test --token-type STRING
  python -m test --token-type BOOLEAN
  python -m test --test-case "Token基本创建"
  
  # Lexer 细粒度测试
  python -m test --function _handle_number
  python -m test --function _handle_string
  python -m test --pattern "变量定义"
  python -m test --pattern "字符串"
  
  # 列表命令
  python -m test --list-token-types
  python -m test --list-functions
  python -m test --list-patterns
  python -m test --list-all
  
  # 代码分析
  python -m test -c "local x = 10"
  
  # JSON 输出（用于自动化）
  python -m test --json
  python -m test --token-type NUMBER --json
  python -m test -c "local x = 10" --json

支持的 Token 类型:
  {', '.join(get_token_types())}

支持的函数:
  {', '.join(get_lexer_functions())}

支持的测试模式:
  {', '.join(get_lexer_patterns())}
        """
    )
    
    # 模块选择
    parser.add_argument(
        '-m', '--module',
        type=str,
        choices=['token', 'lexer', 'all'],
        default='all',
        help='指定要测试的模块: token, lexer, 或 all（默认）'
    )
    
    # Token 细粒度测试参数
    parser.add_argument(
        '-t', '--token-type',
        type=str,
        metavar='TYPE',
        help='只运行指定 Token 类型的测试（仅 token 模块）'
    )
    
    # Lexer 细粒度测试参数
    parser.add_argument(
        '-f', '--function',
        type=str,
        metavar='FUNC',
        help='只运行指定函数的测试（仅 lexer 模块）'
    )
    
    parser.add_argument(
        '-p', '--pattern',
        type=str,
        metavar='PATTERN',
        help='只运行匹配该模式的基础测试（仅 lexer 模块）'
    )
    
    # 通用测试参数
    parser.add_argument(
        '--test-case',
        type=str,
        metavar='NAME',
        help='只运行指定名称的测试用例'
    )
    
    # 代码分析
    parser.add_argument(
        '-c', '--code',
        type=str,
        metavar='CODE',
        help='分析指定的 Lua 代码'
    )
    
    # 列表命令
    list_group = parser.add_mutually_exclusive_group()
    list_group.add_argument(
        '--list-token-types',
        action='store_true',
        help='列出所有支持的 Token 类型'
    )
    list_group.add_argument(
        '--list-functions',
        action='store_true',
        help='列出所有支持的函数名称'
    )
    list_group.add_argument(
        '--list-patterns',
        action='store_true',
        help='列出所有支持的测试模式'
    )
    list_group.add_argument(
        '--list-all',
        action='store_true',
        help='列出所有测试用例'
    )
    
    # 输出格式
    parser.add_argument(
        '-j', '--json',
        action='store_true',
        help='以 JSON 格式输出结果（用于自动化测试）'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Lua Test CLI v2.0'
    )
    
    args = parser.parse_args()
    
    result = {}
    exit_code = 0
    
    # 列表命令
    if args.list_token_types:
        if args.json:
            result = {'token_types': get_token_types()}
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("支持的 Token 类型:")
            for t in get_token_types():
                print(f"  - {t}")
        return 0
    
    if args.list_functions:
        if args.json:
            result = {'functions': get_lexer_functions()}
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("支持的函数名称:")
            for f in get_lexer_functions():
                print(f"  - {f}")
        return 0
    
    if args.list_patterns:
        if args.json:
            result = {'patterns': get_lexer_patterns()}
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("支持的测试模式:")
            for p in get_lexer_patterns():
                print(f"  - {p}")
        return 0
    
    if args.list_all:
        all_cases = get_all_test_cases()
        if args.json:
            print(json.dumps(all_cases, indent=2, ensure_ascii=False))
        else:
            print("=" * 60)
            print("所有测试用例")
            print("=" * 60)
            
            print("\n【Token 模块 - 通用测试】")
            for name in all_cases['token']['general']:
                print(f"  - {name}")
            
            print("\n【Token 模块 - 按类型分类】")
            for type_name, tests in all_cases['token']['by_type'].items():
                print(f"\n  [{type_name}]")
                for name in tests:
                    print(f"    - {name}")
            
            print("\n【Lexer 模块 - 基础测试】")
            for name in all_cases['lexer']['basic']:
                print(f"  - {name}")
            
            print("\n【Lexer 模块 - 按函数分类】")
            for func_name, tests in all_cases['lexer']['by_function'].items():
                print(f"\n  [{func_name}]")
                for name in tests:
                    print(f"    - {name}")
            
            print("\n【Lexer 模块 - 高级测试】")
            for name in all_cases['lexer']['advanced']:
                print(f"  - {name}")
        return 0
    
    # 代码分析
    if args.code:
        result = analyze_code(args.code)
        
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"\n输入代码: {repr(result['source'])}")
            print(f"Token 数: {result['token_count']}")
            for i, token in enumerate(result['tokens']):
                print(f"  {i+1:2d}. [Line {token['line']}:{token['column']}] "
                      f"{token['type']:20} = {repr(token['value'])}")
        return 0
    
    # 测试执行
    # 细粒度测试优先级高于模块测试
    if args.token_type:
        # Token 类型测试
        result = run_token_tests_cli(token_type=args.token_type)
    elif args.function or args.pattern:
        # Lexer 函数或模式测试
        result = run_lexer_tests_cli(func_name=args.function, pattern=args.pattern)
    elif args.test_case:
        # 特定测试用例
        # 尝试在两个模块中查找
        try:
            result = run_token_tests_cli(test_case=args.test_case)
            if result.get('total', 0) == 0:
                result = run_lexer_tests_cli(test_case=args.test_case)
        except:
            result = run_lexer_tests_cli(test_case=args.test_case)
    else:
        # 模块测试
        if args.module == 'token':
            result = run_token_tests_cli()
        elif args.module == 'lexer':
            result = run_lexer_tests_cli()
        else:
            result = run_all_tests()
    
    # 输出结果
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if 'total' in result and isinstance(result['total'], dict):
            total = result['total']
            if total['failed'] == 0:
                print("\n🎉 所有测试通过!")
            else:
                print(f"\n❌ 有 {total['failed']} 个测试失败")
            exit_code = 0 if total['failed'] == 0 else 1
        else:
            if result.get('failed', 0) == 0:
                print("\n🎉 所有测试通过!")
            else:
                print(f"\n❌ 有 {result.get('failed', 0)} 个测试失败")
            exit_code = 0 if result.get('failed', 0) == 0 else 1
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
