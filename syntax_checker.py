#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python语法检查和修复工具
专门用于检查yinzifenxi1119.py文件中的语法错误
"""

import ast
import re
import sys
from typing import List, Dict, Tuple, Optional

class PythonSyntaxChecker:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.file_lines = []
        
    def load_file(self, filepath: str) -> bool:
        """加载文件内容"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.file_lines = f.readlines()
            print(f"✓ 成功加载文件: {filepath}")
            return True
        except Exception as e:
            print(f"✗ 加载文件失败: {e}")
            return False
    
    def check_syntax_with_ast(self) -> List[Dict]:
        """使用AST检查语法错误"""
        try:
            with open('yinzifenxi1119.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            ast.parse(content)
            print("✓ AST语法检查通过")
            return []
        except SyntaxError as e:
            error_info = {
                'type': 'syntax_error',
                'line': e.lineno,
                'column': e.offset,
                'message': e.msg,
                'text': e.text,
                'suggested_fix': self._suggest_syntax_fix(e)
            }
            print(f"✗ 语法错误发现: 行 {e.lineno}: {e.msg}")
            return [error_info]
        except Exception as e:
            print(f"✗ 检查过程出错: {e}")
            return []
    
    def _suggest_syntax_fix(self, error) -> str:
        """为语法错误提供修复建议"""
        line_num = error.lineno
        if line_num > len(self.file_lines):
            return "未知错误位置"
            
        problematic_line = self.file_lines[line_num - 1].strip()
        
        # 常见的语法错误和修复建议
        if "invalid syntax" in error.msg:
            if "return" in problematic_line and problematic_line.strip().startswith("return"):
                return "检查return语句是否有返回值"
            elif ":" in problematic_line:
                return "检查缩进或语法结构"
            else:
                return "检查语句格式和语法"
        
        if "unexpected indent" in error.msg:
            return "检查缩进是否正确"
        
        if "expected indent" in error.msg:
            return "增加适当的缩进"
        
        return f"修复建议: {error.msg}"
    
    def check_return_statements(self) -> List[Dict]:
        """检查return语句的完整性"""
        return_issues = []
        
        for i, line in enumerate(self.file_lines, 1):
            line_stripped = line.strip()
            
            # 检查return语句是否完整
            if line_stripped.startswith("return"):
                if line_stripped == "return":
                    return_issues.append({
                        'type': 'incomplete_return',
                        'line': i,
                        'issue': 'return语句缺少返回值',
                        'original_line': line.rstrip(),
                        'suggested_fix': f"return None  # 添加返回值"
                    })
                elif line_stripped.endswith("return"):
                    return_issues.append({
                        'type': 'incomplete_return',
                        'line': i,
                        'issue': 'return语句可能缺少返回值',
                        'original_line': line.rstrip(),
                        'suggested_fix': '检查return语句是否完整'
                    })
        
        return return_issues
    
    def check_function_definitions(self) -> List[Dict]:
        """检查函数定义的完整性"""
        function_issues = []
        
        for i, line in enumerate(self.file_lines, 1):
            line_stripped = line.strip()
            
            # 检查函数定义
            if line_stripped.startswith("def "):
                if not line_stripped.endswith(":"):
                    function_issues.append({
                        'type': 'incomplete_function_def',
                        'line': i,
                        'issue': '函数定义缺少冒号',
                        'original_line': line.rstrip(),
                        'suggested_fix': line_stripped + ':'
                    })
                elif line_stripped.count("(") != line_stripped.count(")"):
                    function_issues.append({
                        'type': 'unmatched_parentheses',
                        'line': i,
                        'issue': '函数定义中括号不匹配',
                        'original_line': line.rstrip(),
                        'suggested_fix': '检查括号匹配'
                    })
        
        return function_issues
    
    def check_indentation(self) -> List[Dict]:
        """检查缩进问题"""
        indentation_issues = []
        
        for i, line in enumerate(self.file_lines, 1):
            if line.strip():  # 非空行
                leading_spaces = len(line) - len(line.lstrip())
                if leading_spaces % 4 != 0 and leading_spaces % 8 != 0:
                    # 检查是否可能是函数或类内部语句
                    prev_lines = self.file_lines[max(0, i-10):i]
                    has_function_def = any(l.strip().startswith('def ') for l in prev_lines)
                    has_class_def = any(l.strip().startswith('class ') for l in prev_lines)
                    
                    if has_function_def or has_class_def:
                        indentation_issues.append({
                            'type': 'indentation_issue',
                            'line': i,
                            'issue': f'缩进不正确 (当前: {leading_spaces}个空格)',
                            'original_line': line.rstrip(),
                            'suggested_fix': f'使用4或8个空格作为缩进'
                        })
        
        return indentation_issues
    
    def check_duplicate_definitions(self) -> List[Dict]:
        """检查重复定义"""
        duplicates = []
        function_names = {}
        
        for i, line in enumerate(self.file_lines, 1):
            line_stripped = line.strip()
            
            # 查找函数定义
            if line_stripped.startswith("def "):
                match = re.match(r'def\s+(\w+)\s*\(', line_stripped)
                if match:
                    func_name = match.group(1)
                    if func_name in function_names:
                        duplicates.append({
                            'type': 'duplicate_function',
                            'line': i,
                            'function_name': func_name,
                            'issue': f'函数 {func_name} 重复定义',
                            'original_line': line.rstrip(),
                            'suggested_fix': f'重命名函数 {func_name}_{i}'
                        })
                    else:
                        function_names[func_name] = i
        
        return duplicates
    
    def generate_fix_report(self) -> str:
        """生成修复报告"""
        report = []
        report.append("Python语法检查修复报告")
        report.append("=" * 50)
        report.append("")
        
        # AST检查
        ast_errors = self.check_syntax_with_ast()
        if ast_errors:
            report.append("🚨 语法错误 (需要立即修复):")
            for error in ast_errors:
                report.append(f"  行 {error['line']}: {error['message']}")
                report.append(f"    修复建议: {error['suggested_fix']}")
                if error.get('text'):
                    report.append(f"    问题代码: {error['text'].strip()}")
                report.append("")
        
        # Return语句检查
        return_issues = self.check_return_statements()
        if return_issues:
            report.append("⚠️  Return语句问题:")
            for issue in return_issues:
                report.append(f"  行 {issue['line']}: {issue['issue']}")
                report.append(f"    原始代码: {issue['original_line']}")
                report.append(f"    修复建议: {issue['suggested_fix']}")
                report.append("")
        
        # 函数定义检查
        function_issues = self.check_function_definitions()
        if function_issues:
            report.append("⚠️  函数定义问题:")
            for issue in function_issues:
                report.append(f"  行 {issue['line']}: {issue['issue']}")
                report.append(f"    原始代码: {issue['original_line']}")
                report.append(f"    修复建议: {issue['suggested_fix']}")
                report.append("")
        
        # 缩进检查
        indentation_issues = self.check_indentation()
        if indentation_issues:
            report.append("⚠️  缩进问题:")
            for issue in indentation_issues:
                report.append(f"  行 {issue['line']}: {issue['issue']}")
                report.append(f"    修复建议: {issue['suggested_fix']}")
                report.append("")
        
        # 重复定义检查
        duplicate_issues = self.check_duplicate_definitions()
        if duplicate_issues:
            report.append("⚠️  重复定义问题:")
            for issue in duplicate_issues:
                report.append(f"  行 {issue['line']}: {issue['issue']}")
                report.append(f"    修复建议: {issue['suggested_fix']}")
                report.append("")
        
        # 总结
        total_issues = len(ast_errors) + len(return_issues) + len(function_issues) + len(indentation_issues) + len(duplicate_issues)
        
        if total_issues == 0:
            report.append("✅ 未发现语法问题")
        else:
            report.append(f"📊 总计发现 {total_issues} 个问题需要修复")
            report.append("")
            report.append("修复优先级:")
            report.append("1. 🚨 语法错误 (立即修复)")
            report.append("2. ⚠️  结构性错误 (函数定义、return语句)")
            report.append("3. ⚠️  格式问题 (缩进)")
        
        return "\n".join(report)

def main():
    """主函数"""
    print("Python语法检查工具启动")
    print("=" * 40)
    
    checker = PythonSyntaxChecker()
    
    # 加载文件
    if not checker.load_file('yinzifenxi1119.py'):
        return
    
    # 生成修复报告
    report = checker.generate_fix_report()
    
    # 保存报告
    with open('syntax_check_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n" + report)
    print(f"\n完整报告已保存到: syntax_check_report.txt")

if __name__ == "__main__":
    main()
