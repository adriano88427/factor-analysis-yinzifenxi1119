#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 精确分析重复函数和问题定位

def analyze_code_issues():
    file_path = "yinzifenxi1119.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print("=== 代码问题分析 ===")
        print(f"总行数: {len(lines)}")
        
        # 查找重复函数定义
        function_positions = []
        for i, line in enumerate(lines):
            if line.strip().startswith('def calculate_ic('):
                function_positions.append({
                    'line_number': i + 1,
                    'content': line.strip(),
                    'indent': len(line) - len(line.lstrip())
                })
        
        print(f"\n找到 {len(function_positions)} 个 calculate_ic 函数定义:")
        for i, pos in enumerate(function_positions):
            print(f"  {i+1}. 第{pos['line_number']}行: {pos['content']}")
        
        # 检查每个函数定义的完整性
        print("\n函数完整性分析:")
        for i, pos in enumerate(function_positions):
            start_line = pos['line_number'] - 1
            function_lines = []
            indent_level = pos['indent']
            
            # 收集函数内容
            for j in range(start_line + 1, min(start_line + 50, len(lines))):  # 检查前50行
                line = lines[j]
                current_indent = len(line) - len(line.lstrip())
                
                # 如果遇到新的函数定义或缩进减少，停止
                if line.strip().startswith('def ') and j > start_line + 1:
                    break
                if line.strip() and current_indent <= indent_level and j > start_line + 5:
                    break
                
                function_lines.append(line)
            
            print(f"\n函数 {i+1} (第{pos['line_number']}行):")
            print(f"  收集的代码行数: {len(function_lines)}")
            print(f"  前5行内容:")
            for line in function_lines[:5]:
                print(f"    {line.rstrip()}")
            if len(function_lines) > 5:
                print(f"  后3行内容:")
                for line in function_lines[-3:]:
                    print(f"    {line.rstrip()}")
            
            # 检查是否完整
            has_return = any('return' in line for line in function_lines)
            has_end = any(line.strip() == '' or line.strip().startswith('#') for line in function_lines[-5:])
            
            print(f"  是否有return语句: {has_return}")
            print(f"  是否完整: {'是' if has_return and len(function_lines) > 10 else '否'}")
        
        # 查找其他潜在问题
        print("\n=== 其他潜在问题检查 ===")
        
        # 查找空return语句
        empty_returns = []
        for i, line in enumerate(lines):
            if 'return' in line and line.strip() == 'return':
                empty_returns.append(i + 1)
        
        if empty_returns:
            print(f"发现 {len(empty_returns)} 个空return语句:")
            for line_num in empty_returns[:5]:  # 只显示前5个
                print(f"  第{line_num}行: {lines[line_num-1].strip()}")
        
        # 查找可能的不完整定义
        incomplete_defs = []
        for i, line in enumerate(lines):
            if line.strip().startswith('def ') and not line.strip().endswith(':'):
                incomplete_defs.append(i + 1)
        
        if incomplete_defs:
            print(f"\n发现 {len(incomplete_defs)} 个可能不完整的函数定义:")
            for line_num in incomplete_defs[:5]:  # 只显示前5个
                print(f"  第{line_num}行: {lines[line_num-1].strip()}")
        
        # 查找重复变量定义
        print("\n查找重复变量定义:")
        variable_lines = {}
        duplicates = []
        
        for i, line in enumerate(lines):
            if line.strip().startswith(('daily_ics', 'daily_ic', 'ic_mean', 'ic_std')):
                var_name = line.strip().split('=')[0].strip()
                if var_name in variable_lines:
                    duplicates.append((variable_lines[var_name], i + 1, line.strip()))
                else:
                    variable_lines[var_name] = i + 1
        
        if duplicates:
            print(f"发现 {len(duplicates)} 个重复变量定义:")
            for first_line, second_line, content in duplicates:
                print(f"  第一次: 第{first_line}行")
                print(f"  第二次: 第{second_line}行 - {content}")
        else:
            print("未发现明显的重复变量定义")
        
        # 统计总结
        print(f"\n=== 修复建议总结 ===")
        print(f"1. calculate_ic函数: {'需要合并' if len(function_positions) > 1 else '正常'}")
        print(f"2. 空return语句: {len(empty_returns)}个需要修复")
        print(f"3. 不完整函数定义: {len(incomplete_defs)}个需要检查")
        print(f"4. 重复变量定义: {len(duplicates)}个需要处理")
        
        return {
            'calculate_ic_positions': function_positions,
            'empty_returns': empty_returns,
            'incomplete_defs': incomplete_defs,
            'variable_duplicates': duplicates
        }
        
    except Exception as e:
        print(f"分析过程中出错: {e}")
        return None

if __name__ == "__main__":
    results = analyze_code_issues()
    if results:
        print(f"\n分析完成！发现的主要问题:")
        print(f"- calculate_ic函数定义: {len(results['calculate_ic_positions'])}个")
        print(f"- 空return语句: {len(results['empty_returns'])}个")
        print(f"- 不完整定义: {len(results['incomplete_defs'])}个")
        print(f"- 重复变量: {len(results['variable_duplicates'])}个")
