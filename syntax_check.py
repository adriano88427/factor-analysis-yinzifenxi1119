import ast
import sys

try:
    with open('yinzifenxi1119.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析AST
    tree = ast.parse(content)
    print("语法检查通过！")
    
except SyntaxError as e:
    print(f"语法错误：")
    print(f"行号: {e.lineno}")
    print(f"列号: {e.offset}")
    print(f"错误信息: {e.msg}")
    print(f"错误行: {e.text}")
    
except Exception as e:
    print(f"其他错误: {e}")
