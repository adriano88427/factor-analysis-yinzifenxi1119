#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试评级分布修复的脚本
"""

import pandas as pd
import numpy as np
from yinzifenxi1119 import FactorAnalysis

def test_rating_distribution():
    """测试评级分布是否正确显示"""
    print("测试评级分布修复...")
    
    # 创建分析器实例
    analyzer = FactorAnalysis()
    
    # 加载数据（使用默认文件路径）
    analyzer.load_data()
    
    # 运行因子分析
    analyzer.run_full_analysis()
    
    # 生成正向因子分析报告
    positive_analysis = analyzer.generate_positive_factors_analysis()
    
    # 检查评级分布部分
    lines = positive_analysis.split('\n')
    rating_start = -1
    rating_end = -1
    
    for i, line in enumerate(lines):
        if "评级分布:" in line:
            rating_start = i
        elif rating_start != -1 and line.strip() == "" and i > rating_start + 1:
            rating_end = i
            break
    
    if rating_start == -1:
        print("错误: 未找到评级分布部分")
        return False
    
    if rating_end == -1:
        rating_section = lines[rating_start:]
    else:
        rating_section = lines[rating_start:rating_end]
    
    print("\n评级分布部分内容:")
    for line in rating_section:
        print(line)
    
    # 检查是否有评级数据
    has_rating_data = any("级:" in line for line in rating_section)
    
    if has_rating_data:
        print("\n✓ 评级分布修复成功，包含评级数据")
        return True
    else:
        print("\n✗ 评级分布修复失败，没有评级数据")
        return False

if __name__ == "__main__":
    success = test_rating_distribution()
    if success:
        print("\n评级分布修复验证成功！")
    else:
        print("\n评级分布修复验证失败！")