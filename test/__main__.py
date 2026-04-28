#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试模块 CLI 入口

该模块提供命令行接口来运行各种测试，支持：
- 运行所有测试
- 只运行 token 模块测试
- 只运行 lexer 模块测试
- 分析代码
- JSON 格式输出（用于自动化）

使用方法:
    python -m test              # 运行所有测试
    python -m test -m token     # 只运行 token 测试
    python -m test -m lexer     # 只运行 lexer 测试
    python -m test -c "code"    # 分析代码
    python -m test --json       # JSON 输出格式
    python test                 # 运行所有测试（如果是包）
"""

import sys
import os
import argparse
import json

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

try:
    from test_token import run_tests as run_token_tests, get_test_cases as get_token_cases
except ImportError:
    from .test_token import run_tests as run_token_tests, get_test_cases as get_token_cases

try:
    from test_lexer import run_tests as run_lexer_tests, get_test_cases as get_lexer_cases
except ImportError:
    from .test_lexer import run_tests as run_lexer_tests, get_test_cases as get_lexer_cases


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


def run_token_tests_cli() -> dict:
    """
    运行 token 模块测试

    Returns:
        dict: 测试结果字典
    """
    passed, failed, results = run_token_tests()
    
    return {
        'passed': passed,
        'failed': failed,
        'results': results,
        'total': passed + failed
    }


def run_lexer_tests_cli() -> dict:
    """
    运行 lexer 模块测试

    Returns:
        dict: 测试结果字典
    """
    passed, failed, results = run_lexer_tests()
    
    return {
        'passed': passed,
        'failed': failed,
        'results': results,
        'total': passed + failed
    }


def main():
    """
    CLI 主函数
    """
    parser = argparse.ArgumentParser(
        description='Lua 解释器测试 CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python -m test              # 运行所有测试
  python -m test -m token     # 只运行 token 测试
  python -m test -m lexer     # 只运行 lexer 测试
  python -m test -c "local x = 10"  # 分析代码
  python -m test --json       # JSON 输出格式
  python -m test -m token --json  # token 测试，JSON 输出
        """
    )
    
    parser.add_argument(
        '-m', '--module',
        type=str,
        choices=['token', 'lexer', 'all'],
        default='all',
        help='指定要测试的模块: token, lexer, 或 all（默认）'
    )
    
    parser.add_argument(
        '-c', '--code',
        type=str,
        metavar='CODE',
        help='分析指定的 Lua 代码'
    )
    
    parser.add_argument(
        '-j', '--json',
        action='store_true',
        help='以 JSON 格式输出结果（用于自动化测试）'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Lua Test CLI v1.0'
    )
    
    args = parser.parse_args()
    
    result = {}
    
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
    
    if args.module == 'token':
        result = run_token_tests_cli()
    elif args.module == 'lexer':
        result = run_lexer_tests_cli()
    else:
        result = run_all_tests()
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if 'total' in result and isinstance(result['total'], dict):
            total = result['total']
            if total['failed'] == 0:
                print("\n🎉 所有测试通过!")
            else:
                print(f"\n❌ 有 {total['failed']} 个测试失败")
            return 0 if total['failed'] == 0 else 1
        else:
            if result.get('failed', 0) == 0:
                print("\n🎉 所有测试通过!")
            else:
                print(f"\n❌ 有 {result.get('failed', 0)} 个测试失败")
            return 0 if result.get('failed', 0) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
