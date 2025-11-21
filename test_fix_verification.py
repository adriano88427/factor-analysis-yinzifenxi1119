#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
因子分析代码修复验证脚本
验证BUG修复效果，确保代码正常运行
"""

import sys
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 添加当前目录到Python路径
sys.path.append('.')

def test_import_and_basic_functionality():
    """测试导入和基础功能"""
    print("🧪 测试1: 导入和基础功能")
    print("-" * 50)
    
    try:
        # 导入主要模块
        from yinzifenxi1119 import FactorAnalysis, ParameterizedFactorAnalyzer, Logger
        print("✅ 模块导入成功")
        
        # 测试Logger类
        logger = Logger()
        print("✅ Logger类初始化成功")
        logger.close()
        
        # 测试FactorAnalysis类初始化（不加载数据）
        # 创建一个简单的测试对象
        try:
            analyzer = FactorAnalysis(data=None)
            print("✅ FactorAnalysis类初始化成功")
        except Exception as e:
            print(f"❌ FactorAnalysis初始化失败: {e}")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 基础功能测试失败: {e}")
        return False

def test_classify_factors_method():
    """测试分类方法"""
    print("\n🧪 测试2: 分类方法")
    print("-" * 50)
    
    try:
        from yinzifenxi1119 import FactorAnalysis
        import pandas as pd
        import numpy as np
        
        # 创建一个模拟的分析对象
        analyzer = FactorAnalysis(data=None)
        
        # 模拟一些分析结果
        analyzer.analysis_results = {
            '测试因子1': {
                'ic_mean': 0.05,
                'ic_std': 0.02,
                'ir': 2.5,
                'p_value': 0.01,
                'group_results': {
                    'long_short_return': 0.03
                }
            },
            '测试因子2': {
                'ic_mean': -0.03,
                'ic_std': 0.015,
                'ir': -2.0,
                'p_value': 0.05,
                'group_results': {
                    'long_short_return': -0.02
                }
            }
        }
        
        # 测试分类方法（确保不再传递参数）
        positive_factors, negative_factors = analyzer.classify_factors_by_ic()
        
        print(f"✅ 分类方法调用成功")
        print(f"   正向因子数量: {len(positive_factors)}")
        print(f"   负向因子数量: {len(negative_factors)}")
        
        # 验证分类结果
        if len(positive_factors) == 1 and len(negative_factors) == 1:
            print("✅ 分类结果正确")
        else:
            print(f"❌ 分类结果异常: 正向{len(positive_factors)}, 负向{len(negative_factors)}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 分类方法测试失败: {e}")
        return False

def test_report_generation_methods():
    """测试报告生成方法"""
    print("\n🧪 测试3: 报告生成方法")
    print("-" * 50)
    
    try:
        from yinzifenxi1119 import FactorAnalysis
        import pandas as pd
        import numpy as np
        
        # 创建一个模拟的分析对象
        analyzer = FactorAnalysis(data=None)
        
        # 模拟分析结果
        analyzer.analysis_results = {
            '测试因子1': {
                'ic_mean': 0.05,
                'ic_std': 0.02,
                'ir': 2.5,
                'p_value': 0.01,
                'group_results': {
                    'long_short_return': 0.03
                }
            }
        }
        
        # 测试各个报告生成方法
        print("   测试 generate_factor_classification_overview...")
        overview = analyzer.generate_factor_classification_overview()
        print(f"✅ 概览生成成功 (长度: {len(overview)})")
        
        print("   测试 generate_positive_factors_analysis...")
        positive_analysis = analyzer.generate_positive_factors_analysis()
        print(f"✅ 正向因子分析生成成功 (长度: {len(positive_analysis)})")
        
        print("   测试 generate_negative_factors_analysis...")
        negative_analysis = analyzer.generate_negative_factors_analysis()
        print(f"✅ 负向因子分析生成成功 (长度: {len(negative_analysis)})")
        
        print("   测试 _get_scoring_standards...")
        standards = analyzer._get_scoring_standards()
        print(f"✅ 评分标准生成成功 (长度: {len(standards)})")
        
        return True
        
    except Exception as e:
        print(f"❌ 报告生成方法测试失败: {e}")
        return False

def test_infinite_recursion_fix():
    """测试无限递归修复"""
    print("\n🧪 测试4: 无限递归修复")
    print("-" * 50)
    
    try:
        from yinzifenxi1119 import FactorAnalysis
        import pandas as pd
        import numpy as np
        
        # 创建模拟数据
        np.random.seed(42)
        n_samples = 100
        
        test_data = pd.DataFrame({
            '股票代码': [f'000{i:03d}' for i in range(n_samples)],
            '股票名称': [f'测试股票{i}' for i in range(n_samples)],
            '信号日期': pd.date_range('2024-01-01', periods=n_samples),
            '持股2日收益率': np.random.normal(0.02, 0.05, n_samples),
            '信号发出时上市天数': np.random.randint(100, 2000, n_samples),
            '日最大跌幅百分比': np.random.normal(-0.05, 0.03, n_samples),
            '信号当日收盘涨跌幅': np.random.normal(-0.02, 0.04, n_samples),
            '信号后一日开盘涨跌幅': np.random.normal(-0.01, 0.03, n_samples),
            '次日开盘后总体下跌幅度': np.random.normal(-0.03, 0.04, n_samples),
            '前10日最大涨幅': np.random.normal(0.08, 0.06, n_samples),
            '当日回调': np.random.normal(-0.02, 0.03, n_samples)
        })
        
        # 创建分析器并设置数据
        analyzer = FactorAnalysis(data=test_data)
        
        # 运行基本分析
        if analyzer.preprocess_data():
            print("✅ 数据预处理成功")
            
            # 运行因子分析
            if analyzer.run_factor_analysis():
                print("✅ 因子分析成功")
                
                # 生成汇总报告
                summary_df = analyzer.generate_summary_report()
                print("✅ 汇总报告生成成功")
                
                # 重点测试：生成详细报告（这里是之前出现无限递归的地方）
                print("   测试 generate_factor_analysis_report (关键修复点)...")
                
                try:
                    report_filename = analyzer.generate_factor_analysis_report(
                        summary_df, 
                        process_factors=True, 
                        factor_method='standardize', 
                        winsorize=True
                    )
                    
                    if report_filename and os.path.exists(report_filename):
                        # 检查文件大小，确保不是空文件
                        file_size = os.path.getsize(report_filename)
                        print(f"✅ 详细报告生成成功 (文件名: {report_filename}, 大小: {file_size}字节)")
                        
                        # 清理测试文件
                        try:
                            os.remove(report_filename)
                        except:
                            pass
                            
                        return True
                    else:
                        print("❌ 报告文件生成失败")
                        return False
                        
                except RecursionError:
                    print("❌ 仍然存在无限递归问题!")
                    return False
                except Exception as e:
                    print(f"❌ 报告生成异常: {e}")
                    return False
            else:
                print("❌ 因子分析失败")
                return False
        else:
            print("❌ 数据预处理失败")
            return False
            
    except RecursionError as e:
        print(f"❌ 检测到无限递归错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 无限递归修复测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始验证因子分析代码修复效果")
    print("=" * 60)
    
    test_results = []
    
    # 运行所有测试
    test_results.append(("导入和基础功能", test_import_and_basic_functionality()))
    test_results.append(("分类方法", test_classify_factors_method()))
    test_results.append(("报告生成方法", test_report_generation_methods()))
    test_results.append(("无限递归修复", test_infinite_recursion_fix()))
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("\n🎉 所有修复验证测试通过！")
        print("   BUG修复成功，代码可以正常运行")
        return True
    else:
        print(f"\n⚠️  有 {total-passed} 项测试失败")
        print("   请检查相关功能，可能需要进一步修复")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
