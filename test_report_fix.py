#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试因子分析报告截断问题修复是否成功
"""

import os
import sys
import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_report_generation():
    """
    测试报告生成功能
    """
    try:
        # 导入因子分析模块
        from yinzifenxi1119 import FactorAnalysis
        
        print("开始测试因子分析报告生成...")
        
        # 创建因子分析器实例
        analyzer = FactorAnalysis()
        
        # 加载数据
        print("加载数据...")
        analyzer.load_data()
        
        # 运行因子分析
        print("运行因子分析...")
        analyzer.run_factor_analysis()
        
        # 生成汇总报告
        print("生成汇总报告...")
        summary_df = analyzer.generate_summary_report()
        
        # 生成详细分析报告
        print("生成详细分析报告...")
        report_filename = analyzer.generate_factor_analysis_report(summary_df)
        
        if report_filename:
            print(f"详细分析报告已生成: {report_filename}")
            
            # 检查报告文件是否存在
            if os.path.exists(report_filename):
                print("报告文件存在")
                
                # 检查报告内容
                with open(report_filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 检查是否包含负向因子详细分析部分
                if "3. 负向因子详细分析" in content:
                    print("✓ 报告包含负向因子详细分析标题")
                    
                    # 检查标题后是否有实际内容
                    title_pos = content.find("3. 负向因子详细分析")
                    if title_pos != -1:
                        # 获取标题后的内容
                        after_title = content[title_pos+len("3. 负向因子详细分析"):title_pos+len("3. 负向因子详细分析")+500]
                        
                        # 检查是否有分隔线
                        if "=" * 50 in after_title:
                            print("✓ 报告包含负向因子详细分析分隔线")
                            
                            # 检查是否有实际内容
                            if "负向因子总数" in after_title or "IC均值" in after_title or "评级分布" in after_title:
                                print("✓ 报告包含负向因子详细分析实际内容")
                                print("✓ 报告截断问题已修复")
                                return True
                            else:
                                print("✗ 报告不包含负向因子详细分析实际内容")
                                print("✗ 报告截断问题未修复")
                                return False
                        else:
                            print("✗ 报告不包含负向因子详细分析分隔线")
                            print("✗ 报告截断问题未修复")
                            return False
                    else:
                        print("✗ 无法找到负向因子详细分析标题位置")
                        print("✗ 报告截断问题未修复")
                        return False
                else:
                    print("✗ 报告不包含负向因子详细分析标题")
                    print("✗ 报告截断问题未修复")
                    return False
            else:
                print("✗ 报告文件不存在")
                return False
        else:
            print("✗ 报告生成失败")
            return False
            
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_report_generation()
    if success:
        print("\n测试成功：因子分析报告截断问题已修复")
    else:
        print("\n测试失败：因子分析报告截断问题未修复")
    
    sys.exit(0 if success else 1)