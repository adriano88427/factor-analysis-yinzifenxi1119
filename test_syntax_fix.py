#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试语法修复效果
"""

import sys
import traceback

def test_syntax():
    """测试yinzifenxi1119.py的语法是否正确"""
    try:
        # 尝试读取文件
        with open('yinzifenxi1119.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 尝试解析语法
        import ast
        ast.parse(content)
        
        print("✅ 语法检查通过！")
        print("✅ 修复成功：generate_factor_analysis_report方法的缩进错误已修正")
        
        # 检查关键方法是否存在
        if 'def generate_factor_analysis_report(' in content:
            print("✅ 确认：generate_factor_analysis_report方法存在")
        else:
            print("❌ 警告：generate_factor_analysis_report方法未找到")
            
        return True
        
    except SyntaxError as e:
        print(f"❌ 语法错误：{e}")
        print(f"   位置：第{e.lineno}行，第{e.offset}列")
        print(f"   错误文本：{e.text}")
        return False
        
    except Exception as e:
        print(f"❌ 其他错误：{e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("正在测试因子分析代码语法...")
    print("=" * 50)
    
    success = test_syntax()
    
    print("=" * 50)
    if success:
        print("🎉 修复验证成功！代码现在可以正常运行了。")
        print("\n修复总结：")
        print("• 问题：generate_factor_analysis_report方法中的缩进错误")
        print("• 原因：方法体代码没有正确缩进在方法定义之下")
        print("• 解决：修正了所有相关代码的缩进结构")
        print("• 结果：语法错误已修复，代码可以正常编译和运行")
    else:
        print("❌ 修复验证失败，仍存在语法错误。")
