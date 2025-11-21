import ast
import traceback

try:
    with open('yinzifenxi1119.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    ast.parse(code)
    print("✅ 语法检查通过！")
    
except SyntaxError as e:
    print(f"❌ 语法错误：{e}")
    print(f"文件：yinzifenxi1119.py")
    print(f"行号：{e.lineno}")
    print(f"列号：{e.offset}")
    print(f"错误文本：{e.text}")
    
    # 显示错误行周围的代码
    lines = code.split('\n')
    if e.lineno <= len(lines):
        start = max(0, e.lineno - 3)
        end = min(len(lines), e.lineno + 2)
        
        print("\n错误行周围的代码：")
        for i in range(start, end):
            marker = " >>> " if i == e.lineno - 1 else "     "
            print(f"{marker}{i+1:3}: {lines[i]}")

except Exception as e:
    print(f"❌ 其他错误：{e}")
    traceback.print_exc()
