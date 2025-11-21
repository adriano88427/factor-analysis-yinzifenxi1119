#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调试递归调用问题
"""

import re
import sys

def find_recursive_calls(filename):
    """查找文件中的递归调用"""
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有函数定义
    function_pattern = r'def\s+(\w+)\s*\('
    functions = re.findall(function_pattern, content)
    
    print(f"发现的所有函数: {functions}")
    
    # 查找递归调用模式
    for func_name in functions:
        # 查找函数内部是否有对自身的调用
        pattern = rf'class\s+.*?[\s\S]*?def\s+{func_name}\s*\([^)]*\):.*?(?=\n    def|\nclass|\Z)'
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        
        if match:
            func_body = match.group(0)
            # 查找是否调用了自己
            if f'self.{func_name}()' in func_body or f'{func_name}(' in func_body:
                print(f"\n发现可能的递归调用函数: {func_name}")
                
                # 提取函数的前几行来显示上下文
                lines = func_body.split('\n')
                for i, line in enumerate(lines[:10]):
                    if line.strip():
                        print(f"  {i+1}: {line}")
    
    # 特别查找 generate_factor_analysis_report 方法
    print("\n=== 查找 generate_factor_analysis_report 方法 ===")
    pattern = r'class\s+.*?[\s\S]*?def\s+generate_factor_analysis_report\s*\([^)]*\):.*?(?=\n    def|\nclass|\Z)'
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    
    if match:
        func_body = match.group(0)
        print("generate_factor_analysis_report 方法体:")
        lines = func_body.split('\n')
        for i, line in enumerate(lines[:30]):  # 显示前30行
            print(f"  {i+1}: {line}")
    else:
        print("未找到 generate_factor_analysis_report 方法")
    
    # 查找 generate_negative_factors_analysis 方法
    print("\n=== 查找 generate_negative_factors_analysis 方法 ===")
    pattern = r'class\s+.*?[\s\S]*?def\s+generate_negative_factors_analysis\s*\([^)]*\):.*?(?=\n    def|\nclass|\Z)'
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    
    if match:
        func_body = match.group(0)
        print("generate_negative_factors_analysis 方法体:")
        lines = func_body.split('\n')
        for i, line in enumerate(lines[:30]):  # 显示前30行
            print(f"  {i+1}: {line}")
    else:
        print("未找到 generate_negative_factors_analysis 方法")
    
    # 查找方法调用
    print("\n=== 查找方法调用 ===")
    calls = re.findall(r'self\.(generate_\w+)\(\)', content)
    for call in set(calls):
        print(f"调用: self.{call}()")
    
    return content

if __name__ == "__main__":
    content = find_recursive_calls("yinzifenxi1119.py")
