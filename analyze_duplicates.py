#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 分析yinzifenxi1119.py中的calculate_ic函数重复问题

def analyze_calculate_ic_duplicates():
    file_path = "yinzifenxi1119.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        calculate_ic_functions = []
        
        for i, line in enumerate(lines):
            if line.strip().startswith('def calculate_ic('):
                # 找到函数开始行
                function_start = i + 1
                function_code = [line]
                
                # 收集函数内容直到遇到下一个def或缩进减少
                j = i + 1
                indent_level = len(line) - len(line.lstrip())
                
                while j < len(lines):
                    current_line = lines[j]
                    current_indent = len(current_line) - len(current_line.lstrip())
                    
                    # 如果遇到新的函数定义或缩进减少（但不是空行或注释），则认为函数结束
                    if current_line.strip().startswith('def ') and j > i + 1:
                        break
                    elif current_line.strip() and current_indent <= indent_level and j > i + 1:
                        break
                    
                    function_code.append(current_line)
                    j += 1
                
                # 存储函数信息
                function_info = {
                    'line_number': i + 1,
                    'function_signature': line.strip(),
                    'function_code': function_code,
                    'function_end_line': j
                }
                calculate_ic_functions.append(function_info)
                
                # 跳过已处理的行
                i = j - 1
        
        print(f"找到 {len(calculate_ic_functions)} 个 calculate_ic 函数定义：")
        print("=" * 60)
        
        for idx, func in enumerate(calculate_ic_functions):
            print(f"\n函数 {idx + 1}:")
            print(f"位置: 第 {func['line_number']} 行")
            print(f"签名: {func['function_signature']}")
            print(f"代码行数: {len(func['function_code'])}")
            
            # 显示函数的前几行和后几行
            print("函数开头:")
            for line in func['function_code'][:5]:
                print(f"  {line.rstrip()}")
            print("  ...")
            
            if len(func['function_code']) > 5:
                print("函数结尾:")
                for line in func['function_code'][-3:]:
                    print(f"  {line.rstrip()}")
        
        # 比较函数内容
        if len(calculate_ic_functions) > 1:
            print("\n" + "=" * 60)
            print("函数内容比较:")
            print("=" * 60)
            
            func1 = calculate_ic_functions[0]
            func2 = calculate_ic_functions[1]
            
            print(f"函数1行数: {len(func1['function_code'])}")
            print(f"函数2行数: {len(func2['function_code'])}")
            
            # 找出差异
            if len(func1['function_code']) != len(func2['function_code']):
                print("❌ 函数长度不同，存在重复定义")
                print("需要删除较短的版本，保留较长的完整版本")
            else:
                print("⚠️ 函数长度相同，需要详细比较内容")
        
    except Exception as e:
        print(f"分析过程中出错: {e}")

if __name__ == "__main__":
    analyze_calculate_ic_duplicates()
