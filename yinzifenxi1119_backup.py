import sys
import os
import warnings
from datetime import datetime

import pandas as pd
import numpy as np
import scipy
import matplotlib.pyplot as plt

# 日志记录类
class Logger:
    def __init__(self, log_file=None):
        """初始化日志记录器
        
        Args:
            log_file: 日志文件路径，如果为None则自动生成
        """
        if log_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = f'因子分析日志_{timestamp}.txt'
        
        self.log_file = log_file
        self.terminal = sys.stdout  # 保存原始终端输出
        
        # 创建日志文件
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"因子分析日志 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
    
    def write(self, message):
        """同时输出到终端和日志文件"""
        # 输出到终端
        self.terminal.write(message)
        
        # 输出到日志文件
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(message)
    
    def flush(self):
        """刷新输出"""
        self.terminal.flush()
        
    def close(self):
        """关闭日志记录器"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n\n日志记录结束 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n")
        
        # 恢复原始终端输出
        sys.stdout = self.terminal

# 添加类型检查函数
# 增强类型检查函数
def ensure_list(obj, obj_name="object"):
    """确保对象是列表类型，防止len() of unsized object错误"""
    if not isinstance(obj, list):
        print(f"  警告: {obj_name} 不是列表类型，当前类型: {type(obj)}，正在修复...")
        return []
    return obj

def safe_len(obj, obj_name="object"):
    """安全获取对象长度，防止len() of unsized object错误"""
    try:
        if isinstance(obj, (list, tuple, np.ndarray)):
            return len(obj)
        else:
            print(f"  警告: {obj_name} 类型 {type(obj)} 不支持len()操作，重置为0")
            return 0
    except Exception as e:
        print(f"  错误: 获取{obj_name}长度时出错: {e}，重置为0")
        return 0

def safe_ensure_list(obj, obj_name="object"):
    """安全版本确保对象是列表类型，防止len() of unsized object错误"""
    if not isinstance(obj, list):
        print(f"  警告: {obj_name} 不是列表类型，当前类型: {type(obj)}，正在修复...")
        return []
    return obj

# 默认数据文件路径设置（方便用户修改）
DEFAULT_DATA_FILE = "创业板单日下跌14%详细交易日数据（清理后）1114.xlsx"

# 读取完整因子数据文件
print(f"使用指定的数据文件: {DEFAULT_DATA_FILE}")

# 检查文件是否存在
if os.path.exists(DEFAULT_DATA_FILE):
    print(f"数据文件路径: {os.path.abspath(DEFAULT_DATA_FILE)}")
else:
    print(f"错误: 数据文件不存在，请检查文件路径")
    print(f"期望的文件: {DEFAULT_DATA_FILE}")
    sys.exit(1)

# 尝试导入scipy.stats，如果不可用则设置标志
HAS_SCIPY = False
try:
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    print("警告: scipy不可用，部分统计计算功能将被简化，但基本分析仍将继续")

# 尝试导入matplotlib和seaborn，如果不可用则设置标志
HAS_PLOT = False
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    HAS_PLOT = True
except ImportError:
    print("警告: matplotlib或seaborn不可用，可视化功能将被禁用，但核心分析仍将继续")

# 稳健性统计方法辅助函数

def kendall_tau_corr(x, y):
    """
    计算Kendall's Tau相关系数（不依赖scipy）
    
    Args:
        x: 第一个数组
        y: 第二个数组
        
    Returns:
        float: Kendall's Tau相关系数
    """
    x = np.asarray(x)
    y = np.asarray(y)
    
    if len(x) < 2 or len(y) < 2 or len(x) != len(y):
        return np.nan
    
    if np.isnan(x).any() or np.isnan(y).any():
        return np.nan
    
    n = len(x)
    concordant = 0
    discordant = 0
    
    for i in range(n - 1):
        for j in range(i + 1, n):
            if (x[i] < x[j] and y[i] < y[j]) or (x[i] > x[j] and y[i] > y[j]):
                concordant += 1
            elif (x[i] < x[j] and y[i] > y[j]) or (x[i] > x[j] and y[i] < y[j]):
                discordant += 1
    
    tau = (concordant - discordant) / (n * (n - 1) / 2)
    return tau

def robust_correlation(x, y, method='median'):
    """
    计算稳健相关系数
    
    Args:
        x: 第一个数组
        y: 第二个数组
        method: 稳健方法 ('median', 'trimmed_mean', 'winsorized')
        
    Returns:
        float: 稳健相关系数
    """
    x = np.asarray(x)
    y = np.asarray(y)
    
    if len(x) < 2 or len(y) < 2 or len(x) != len(y):
        return np.nan
    
    if np.isnan(x).any() or np.isnan(y).any():
        return np.nan
    
    if method == 'median':
        # 使用中位数绝对偏差进行稳健回归
        def median_abs_deviation(data):
            return np.median(np.abs(data - np.median(data)))
        
        # 计算基于中位数的稳健相关系数
        n = len(x)
        x_centered = x - np.median(x)
        y_centered = y - np.median(y)
        
        # 使用MAD作为权重
        x_mad = median_abs_deviation(x)
        y_mad = median_abs_deviation(y)
        
        if x_mad == 0 or y_mad == 0:
            return np.nan
        
        # 稳健相关系数
        robust_x = np.sign(x_centered) * np.minimum(np.abs(x_centered), 3 * x_mad)
        robust_y = np.sign(y_centered) * np.minimum(np.abs(y_centered), 3 * y_mad)
        
        return np.corrcoef(robust_x, robust_y)[0, 1]
    
    elif method == 'trimmed_mean':
        # 截尾均值方法
        n = len(x)
        trim_pct = 0.1  # 截尾10%
        trim_count = int(n * trim_pct)
        
        x_sorted = np.sort(x)[trim_count:-trim_count]
        y_sorted = np.sort(y)[trim_count:-trim_count]
        
        if len(x_sorted) < 2 or len(y_sorted) < 2:
            return np.corrcoef(x, y)[0, 1]
        
        return np.corrcoef(x_sorted, y_sorted)[0, 1]
    
    else:
        return np.corrcoef(x, y)[0, 1]

def mann_whitney_u_test(x, y):
    """
    进行Mann-Whitney U检验（非参数检验）
    
    Args:
        x: 第一组数据
        y: 第二组数据
        
    Returns:
        tuple: (U统计量, p值)
    """
    try:
        # 安全的数组转换和有效性检查
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        
        # 移除NaN和无穷值
        x = x[np.isfinite(x)]
        y = y[np.isfinite(y)]
        
        if len(x) < 1 or len(y) < 1:
            return np.nan, np.nan
        
        # 合并数据并排序
        combined = np.concatenate([x, y])
        ranks = np.argsort(np.argsort(combined)) + 1
        
        # 计算U统计量
        R1 = np.sum(ranks[:len(x)])
        n1, n2 = len(x), len(y)
        U1 = R1 - n1 * (n1 + 1) / 2
        U2 = n1 * n2 - U1
        U = min(U1, U2)
        
        # 计算p值（大样本近似）
        n = n1 + n2
        mean_U = n1 * n2 / 2
        var_U = n1 * n2 * (n + 1) / 12
        
        if var_U == 0:
            return U, 1.0
        
        z = (U - mean_U) / np.sqrt(var_U)
        
        # 使用scipy或自定义正态分布计算
        if HAS_SCIPY:
            p_value = 2 * (1 - scipy.stats.norm.cdf(abs(z)))
        else:
            # 自定义正态分布累积分布函数近似
            import math
            p_value = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
        
        return U, p_value
        
    except Exception as e:
        # 如果计算失败，返回安全的默认值
        return np.nan, np.nan

def bootstrap_confidence_interval(x, y, statistic='correlation', n_bootstrap=1000, confidence_level=0.95):
    """
    计算Bootstrap置信区间
    
    Args:
        x: 第一个数组
        y: 第二个数组
        statistic: 统计量 ('correlation', 'mean_diff')
        n_bootstrap: 重抽样次数
        confidence_level: 置信水平
        
    Returns:
        tuple: (下界, 上界, 自举统计量)
    """
    x = np.asarray(x)
    y = np.asarray(y)
    
    if len(x) < 2 or len(y) < 2 or len(x) != len(y):
        return np.nan, np.nan, []
    
    n = len(x)
    bootstrap_stats = []
    
    # 定义统计量函数
    def correlation_stat(data1, data2):
        return np.corrcoef(data1, data2)[0, 1]
    
    def mean_diff_stat(data1, data2):
        return np.mean(data1) - np.mean(data2)
    
    stat_func = correlation_stat if statistic == 'correlation' else mean_diff_stat
    
    for i in range(n_bootstrap):
        # 重抽样
        indices = np.random.choice(n, n, replace=True)
        boot_x = x[indices]
        boot_y = y[indices]
        
        # 计算统计量
        try:
            stat_value = stat_func(boot_x, boot_y)
            if not np.isnan(stat_value) and np.isfinite(stat_value):
                bootstrap_stats.append(stat_value)
        except:
            continue
    
    if len(bootstrap_stats) < 10:  # 至少需要10个有效样本
        return np.nan, np.nan, bootstrap_stats
    
    # 计算置信区间
    alpha = 1 - confidence_level
    lower_percentile = (alpha / 2) * 100
    upper_percentile = (1 - alpha / 2) * 100
    
    ci_lower = np.percentile(bootstrap_stats, lower_percentile)
    ci_upper = np.percentile(bootstrap_stats, upper_percentile)
    
    return ci_lower, ci_upper, bootstrap_stats

def detect_outliers(x, method='iqr'):
    """
    异常值诊断
    
    Args:
        x: 输入数据
        method: 诊断方法 ('iqr', 'zscore', 'modified_zscore')
        
    Returns:
        dict: 异常值诊断结果
    """
    x = np.asarray(x)
    
    if len(x) < 3:
        return {'outlier_mask': np.zeros(len(x), dtype=bool), 'method': method, 'threshold': np.nan}
    
    result = {'method': method, 'threshold': np.nan}
    
    if method == 'iqr':
        Q1 = np.percentile(x, 25)
        Q3 = np.percentile(x, 75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        result['threshold'] = (lower_bound, upper_bound)
        result['outlier_mask'] = (x < lower_bound) | (x > upper_bound)
        result['mild_outlier_mask'] = (x < lower_bound) | (x > upper_bound)
        
        # 极端异常值
        extreme_lower = Q1 - 3 * IQR
        extreme_upper = Q3 + 3 * IQR
        result['extreme_outlier_mask'] = (x < extreme_lower) | (x > extreme_upper)
    
    elif method == 'zscore':
        z_scores = np.abs((x - np.mean(x)) / np.std(x))
        threshold = 3
        result['threshold'] = threshold
        result['outlier_mask'] = z_scores > threshold
    
    elif method == 'modified_zscore':
        median = np.median(x)
        mad = np.median(np.abs(x - median))
        modified_z_scores = 0.6745 * (x - median) / mad
        threshold = 3.5
        result['threshold'] = threshold
        result['outlier_mask'] = np.abs(modified_z_scores) > threshold
    
    return result

def sensitivity_analysis(x, y, outlier_methods=['iqr', 'zscore'], include_outliers=True):
    """
    敏感性分析：包含vs剔除异常值的对比
    
    Args:
        x: 因子数据
        y: 收益率数据
        outlier_methods: 异常值检测方法列表
        include_outliers: 是否包含异常值分析
        
    Returns:
        dict: 敏感性分析结果
    """
    if len(x) != len(y) or len(x) < 3:
        return {'error': '数据长度不足或不一致'}
    
    results = {}
    
    # 原始数据相关性
    original_corr = np.corrcoef(x, y)[0, 1]
    results['original'] = {
        'correlation': original_corr,
        'sample_size': len(x)
    }
    
    # 不同方法异常值检测结果
    for method in outlier_methods:
        outlier_info = detect_outliers(x, method)
        outlier_mask = outlier_info['outlier_mask']
        
        if include_outliers:
            # 包含异常值的结果
            x_with_outliers = x[outlier_mask]
            y_with_outliers = y[outlier_mask]
            if len(x_with_outliers) >= 2:
                corr_with_outliers = np.corrcoef(x_with_outliers, y_with_outliers)[0, 1]
                results[f'{method}_with_outliers'] = {
                    'correlation': corr_with_outliers,
                    'sample_size': len(x_with_outliers)
                }
        
        # 剔除异常值的结果
        clean_x = x[~outlier_mask]
        clean_y = y[~outlier_mask]
        if len(clean_x) >= 2:
            corr_without_outliers = np.corrcoef(clean_x, clean_y)[0, 1]
            results[f'{method}_without_outliers'] = {
                'correlation': corr_without_outliers,
                'sample_size': len(clean_x),
                'outliers_removed': np.sum(outlier_mask)
            }
    
    # 计算敏感性指标
    clean_results = {k: v for k, v in results.items() if 'without_outliers' in k}
    if clean_results:
        correlations = [v['correlation'] for v in clean_results.values() 
                       if not np.isnan(v['correlation'])]
        if correlations:
            results['sensitivity'] = {
                'correlation_std': np.std(correlations),
                'correlation_range': np.max(correlations) - np.min(correlations),
                'max_difference_from_original': max(abs(corr - original_corr) for corr in correlations)
            }
    
    return results

def false_discovery_control(p_values, method='bh', alpha=0.05):
    """
    多重检验校正（False Discovery Rate控制）
    
    Args:
        p_values: p值列表
        method: 校正方法 ('bh' for Benjamini-Hochberg, 'by' for Benjamini-Yekutieli)
        alpha: 显著性水平
        
    Returns:
        tuple: (校正后的p值, 是否拒绝原假设, 发现的显著结果数量)
    """
    p_values = np.asarray(p_values)
    
    if len(p_values) == 0:
        return np.array([]), np.array([]), 0
    
    # 移除NaN值
    valid_mask = ~np.isnan(p_values)
    if not np.any(valid_mask):
        return p_values, np.zeros(len(p_values), dtype=bool), 0
    
    valid_p = p_values[valid_mask]
    
    if method == 'bh':
        # Benjamini-Hochberg方法
        sorted_indices = np.argsort(valid_p)
        sorted_p = valid_p[sorted_indices]
        m = len(valid_p)
        
        # 计算校正阈值
        thresholds = (np.arange(1, m + 1) / m) * alpha
        
        # 找到最后一个显著的结果
        significant_indices = np.where(sorted_p <= thresholds)[0]
        
        if len(significant_indices) > 0:
            last_significant = significant_indices[-1]
            # 将阈值应用到所有结果
            corrected_p = np.copy(valid_p)
            for i in range(last_significant + 1):
                corrected_p[sorted_indices[i]] = sorted_p[i] * m / (i + 1)
        else:
            corrected_p = valid_p.copy()
    
    elif method == 'by':
        # Benjamini-Yekutieli方法（更保守）
        sorted_indices = np.argsort(valid_p)
        sorted_p = valid_p[sorted_indices]
        m = len(valid_p)
        
        # 计算调和数
        c_m = np.sum(1.0 / np.arange(1, m + 1))
        
        # 计算校正阈值
        thresholds = (np.arange(1, m + 1) / (m * c_m)) * alpha
        
        # 找到最后一个显著的结果
        significant_indices = np.where(sorted_p <= thresholds)[0]
        
        if len(significant_indices) > 0:
            last_significant = significant_indices[-1]
            # 将阈值应用到所有结果
            corrected_p = np.copy(valid_p)
            for i in range(last_significant + 1):
                corrected_p[sorted_indices[i]] = sorted_p[i] * c_m * m / (i + 1)
        else:
            corrected_p = valid_p.copy()
    
    else:
        # 不进行校正
        corrected_p = valid_p.copy()
    
    # 创建完整的结果数组
    full_corrected_p = np.full(len(p_values), np.nan)
    full_corrected_p[valid_mask] = corrected_p
    
    # 判断是否拒绝原假设
    reject_null = (full_corrected_p <= alpha) & ~np.isnan(full_corrected_p)
    
    # 计算显著结果数量
    n_significant = np.sum(reject_null)
    
    return full_corrected_p, reject_null, n_significant

def rolling_window_analysis(df, factor_col, return_col, window_sizes=[30, 60], 
                          compute_ic_decay=True, save_plots=False):
    """
    滚动窗口分析：优化滚动窗口机制
    
    Args:
        df: 数据框
        factor_col: 因子列名
        return_col: 收益率列名
        window_sizes: 窗口大小列表（交易日数）
        compute_ic_decay: 是否计算IC衰减分析
        save_plots: 是否保存图表
        
    Returns:
        dict: 滚动窗口分析结果
    """
    results = {
        'window_sizes': window_sizes,
        'rolling_ic': {},
        'ic_decay': {},
        'stability_metrics': {}
    }
    
    df = df.sort_values('信号日期')
    unique_dates = sorted(df['信号日期'].unique())
    
    for window_size in window_sizes:
        print(f"\n分析窗口大小: {window_size} 个交易日")
        
        rolling_ics = []
        rolling_dates = []
        
        # 计算滚动IC值
        for i in range(len(unique_dates) - window_size + 1):
            window_dates = unique_dates[i:i + window_size]
            window_data = df[df['信号日期'].isin(window_dates)]
            
            # 确保有足够的数据点
            if len(window_data) >= window_size * 2:  # 至少每个交易日2个样本
                valid_data = window_data.dropna(subset=[factor_col, return_col])
                
                if len(valid_data) >= window_size:
                    try:
                        # 计算Spearman相关系数
                        ic = custom_spearman_corr(valid_data[factor_col], valid_data[return_col])
                        if not np.isnan(ic) and np.isfinite(ic):
                            rolling_ics.append(ic)
                            rolling_dates.append(window_dates[-1])  # 使用窗口结束日期
                    except:
                        continue
        
        results['rolling_ic'][window_size] = {
            'dates': rolling_dates,
            'ic_values': rolling_ics,
            'mean_ic': np.mean(rolling_ics) if rolling_ics else np.nan,
            'ic_std': np.std(rolling_ics) if rolling_ics else np.nan
        }
        
        print(f"  有效窗口数: {len(rolling_ics)}")
        if rolling_ics:
            print(f"  平均IC值: {np.mean(rolling_ics):.4f}")
            print(f"  IC标准差: {np.std(rolling_ics):.4f}")
    
    # 计算IC衰减分析
    if compute_ic_decay:
        print(f"\n计算IC衰减分析...")
        
        for window_size in window_sizes:
            if window_size in results['rolling_ic'] and results['rolling_ic'][window_size]['ic_values']:
                ic_series = results['rolling_ic'][window_size]['ic_values']
                
                # 计算IC的半衰期（IC绝对值衰减到一半所需的时间）
                abs_ics = np.abs(ic_series)
                initial_ic = abs_ics[0] if len(abs_ics) > 0 else 0
                
                if initial_ic > 0:
                    half_life = None
                    for i, ic_val in enumerate(abs_ics):
                        if ic_val <= initial_ic / 2:
                            half_life = i + 1
                            break
                    
                    results['ic_decay'][window_size] = {
                        'half_life': half_life,
                        'initial_ic': initial_ic,
                        'final_ic': abs_ics[-1] if len(abs_ics) > 0 else np.nan,
                'decay_rate': (initial_ic - (abs_ics[-1] if len(abs_ics) > 0 else 0)) / len(abs_ics) 
                              if len(abs_ics) > 0 else np.nan
                    }
        
        # 计算稳定性指标
        for window_size in window_sizes:
            if window_size in results['rolling_ic']:
                ic_values = results['rolling_ic'][window_size]['ic_values']
                if ic_values:
                    results['stability_metrics'][window_size] = {
                        'coefficient_of_variation': np.std(ic_values) / abs(np.mean(ic_values)) if np.mean(ic_values) != 0 else np.inf,
                        'persistence': np.corrcoef(range(len(ic_values)), ic_values)[0, 1] if len(ic_values) > 1 else np.nan,
                        'mean_abs_ic': np.mean(np.abs(ic_values))
                    }
    
    return results

def temporal_stability_analysis(factor_results):
    """
    结果稳健性检验：时序稳定性
    
    Args:
        factor_results: 因子分析结果字典
        
    Returns:
        dict: 时序稳定性分析结果
    """
    stability_results = {
        'ic_stability': {},
        'rank_stability': {},
        'temporal_trends': {}
    }
    
    # 分析IC值的时序稳定性
    if 'ic_values' in factor_results:
        ic_values = factor_results['ic_values']
        if len(ic_values) > 2:
            # 计算IC序列的自相关性
            ic_series = np.array(ic_values)
            
            # 一阶自相关
            lag1_corr = np.corrcoef(ic_series[:-1], ic_series[1:])[0, 1] if len(ic_series) > 2 else np.nan
            
            # IC值的趋势分析
            x = np.arange(len(ic_series))
            trend_corr = np.corrcoef(x, ic_series)[0, 1]
            
            stability_results['ic_stability'] = {
                'autocorr_lag1': lag1_corr,
                'trend_correlation': trend_corr,
                'is_stationary': abs(trend_corr) < 0.3,  # 趋势相关性小于0.3认为相对稳定
                'ic_volatility': np.std(ic_series) / abs(np.mean(ic_series)) if np.mean(ic_series) != 0 else np.inf
            }
            
            # 时间序列分解（简单版本）
            trend = np.polyfit(x, ic_series, 1)[0]  # 线性趋势
            stability_results['temporal_trends'] = {
                'linear_trend': trend,
                'trend_pvalue': np.nan,  # 需要更复杂的计算
                'sign_changes': np.sum(np.diff(np.sign(ic_series)) != 0),
                'mean_reversion_strength': 1 - abs(lag1_corr) if not np.isnan(lag1_corr) else np.nan
            }
    
    # 分析因子排名稳定性
    if 'factor_rankings' in factor_results:
        rankings = factor_results['factor_rankings']
        if len(rankings) > 1:
            # 计算排名变化的稳定性
            ranking_changes = []
            for i in range(1, len(rankings)):
                # 计算排名变化的平均绝对偏差
                change = np.mean(np.abs(np.array(rankings[i]) - np.array(rankings[i-1])))
                ranking_changes.append(change)
            
            stability_results['rank_stability'] = {
                'mean_ranking_change': np.mean(ranking_changes) if ranking_changes else np.nan,
                'ranking_volatility': np.std(ranking_changes) if ranking_changes else np.nan,
                'ranking_consistency': 1 - (np.std(ranking_changes) / np.mean(ranking_changes) if ranking_changes and np.mean(ranking_changes) > 0 else np.inf)
            }
    
    return stability_results

def sample_sensitivity_analysis(df, factor_col, return_col, 
                               sample_sizes=[0.8, 0.9, 1.0], n_iterations=100):
    """
    结果稳健性检验：样本敏感性分析
    
    Args:
        df: 数据框
        factor_col: 因子列名
        return_col: 收益率列名
        sample_sizes: 样本大小比例列表
        n_iterations: 每个样本大小下的迭代次数
        
    Returns:
        dict: 样本敏感性分析结果
    """
    sensitivity_results = {
        'sample_size_effects': {},
        'robustness_metrics': {}
    }
    
    valid_data = df.dropna(subset=[factor_col, return_col])
    total_samples = len(valid_data)
    
    print(f"\n开始样本敏感性分析（总样本数: {total_samples}）")
    
    for sample_size in sample_sizes:
        print(f"  分析样本大小: {sample_size*100:.0f}%")
        
        sample_ics = []
        
        for iteration in range(n_iterations):
            # 随机抽样
            n_samples = int(total_samples * sample_size)
            sampled_data = valid_data.sample(n=n_samples, random_state=iteration)
            
            # 计算IC值
            try:
                ic = custom_spearman_corr(sampled_data[factor_col], sampled_data[return_col])
                if not np.isnan(ic) and np.isfinite(ic):
                    sample_ics.append(ic)
            except:
                continue
        
        if sample_ics:
            sensitivity_results['sample_size_effects'][sample_size] = {
                'ic_mean': np.mean(sample_ics),
                'ic_std': np.std(sample_ics),
                'ic_median': np.median(sample_ics),
                'ic_q25': np.percentile(sample_ics, 25),
                'ic_q75': np.percentile(sample_ics, 75),
                'n_successful_iterations': len(sample_ics),
                'success_rate': len(sample_ics) / n_iterations
            }
            
            print(f"    成功迭代: {len(sample_ics)}/{n_iterations}")
            print(f"    平均IC: {np.mean(sample_ics):.4f} ± {np.std(sample_ics):.4f}")
    
    # 计算稳健性指标
    if len(sensitivity_results['sample_size_effects']) > 1:
        ic_means = [stats['ic_mean'] for stats in sensitivity_results['sample_size_effects'].values()]
        ic_stds = [stats['ic_std'] for stats in sensitivity_results['sample_size_effects'].values()]
        
        sensitivity_results['robustness_metrics'] = {
            'ic_stability_across_samples': np.std(ic_means) / abs(np.mean(ic_means)) if np.mean(ic_means) != 0 else np.inf,
            'mean_variance_across_samples': np.mean(ic_stds),
            'best_sample_size': max(sensitivity_results['sample_size_effects'].keys(), 
                                  key=lambda x: abs(sensitivity_results['sample_size_effects'][x]['ic_mean'])),
            'most_stable_sample_size': min(sensitivity_results['sample_size_effects'].keys(),
                                         key=lambda x: sensitivity_results['sample_size_effects'][x]['ic_std'])
        }
    
    return sensitivity_results

# 自定义Spearman相关系数计算函数，不依赖scipy
def custom_spearman_corr(x, y):
    """
    计算Spearman相关系数，确保数学上的准确性，不添加任何人为限制或修正
    
    Args:
        x: 第一个数组
        y: 第二个数组
        
    Returns:
        float: Spearman相关系数
    """
    # 转换为numpy数组
    x = np.asarray(x)
    y = np.asarray(y)
    
    # 检查是否有足够的数据点和数据长度是否匹配
    if len(x) < 2 or len(y) < 2 or len(x) != len(y):
        return np.nan
    
    # 检查是否有NaN值或无穷值
    if np.isnan(x).any() or np.isnan(y).any() or np.isinf(x).any() or np.isinf(y).any():
        return np.nan
    
    # 计算秩，正确处理重复值
    def rank_with_ties(data):
        # 转换为numpy数组
        arr = np.asarray(data)
        
        # 获取排序后的索引
        sorted_indices = np.argsort(arr)
        
        # 创建排名数组
        ranks = np.zeros_like(sorted_indices, dtype=float)
        
        # 初始化
        i = 0
        n = len(arr)
        
        while i < n:
            # 查找相同值的范围
            current_value = arr[sorted_indices[i]]
            j = i
            
            # 找到所有相等值的位置
            while j < n and arr[sorted_indices[j]] == current_value:
                j += 1
            
            # 计算平均排名 - 使用标准的平均排名公式
            # 排名从1开始，所以起始位置是i+1，结束位置是j
            rank = (i + 1 + j) / 2
            
            # 为相同值的元素分配平均排名
            for k in range(i, j):
                ranks[sorted_indices[k]] = rank
            
            # 移动到下一组不同的值
            i = j
        
        return ranks
    
    # 计算x和y的秩（处理重复值）
    rank_x = rank_with_ties(x)
    rank_y = rank_with_ties(y)
    
    # 直接使用标准皮尔逊相关系数公式计算，确保数学准确性
    n = len(rank_x)
    sum_xy = np.sum(rank_x * rank_y)
    sum_x = np.sum(rank_x)
    sum_y = np.sum(rank_y)
    sum_x2 = np.sum(rank_x**2)
    sum_y2 = np.sum(rank_y**2)
    
    # 应用皮尔逊相关系数公式计算Spearman相关系数
    numerator = n * sum_xy - sum_x * sum_y
    denominator = np.sqrt((n * sum_x2 - sum_x**2) * (n * sum_y2 - sum_y**2))
    
    # 处理分母为0的情况
    if denominator == 0:
        # 如果秩方差为0，Spearman相关系数没有定义
        return np.nan
    
    # 直接计算相关系数，不添加任何人为限制或修正
    corr = numerator / denominator
    
    # 由于浮点精度问题，可能会出现略微超出范围的情况，进行轻微的截断
    # 这是必要的数学处理，而不是人为修改结果
    corr = min(max(corr, -1.0), 1.0)
    
    return corr

def calculate_standard_annual_return(total_return_rate, observation_years, method='standard_compound'):
    """
    标准复利年化收益率计算 - 优化版本
    
    Args:
        total_return_rate: 总收益率（例如：0.2058表示20.58%的总收益）
        observation_years: 观测期年数（例如：5.18年）
        method: 计算方法，'standard_compound'（标准复利）或'log_based'（对数方法）
        
    Returns:
        tuple: (年化收益率, 计算详情字典)
    
    数学公式:
    标准复利年化: (1 + 总收益率)^(1/年数) - 1
    对数方法: exp(ln(1+总收益率)/年数) - 1（数值稳定性更好）
    
    示例验证:
    如果日收益率5.8%，交易85天，总收益约为120.58%
    观测期5.18年，则年化收益率 = (1.2058)^(1/5.18) - 1 ≈ 160.77%
    """
    try:
        # 输入参数验证
        if total_return_rate is None or observation_years is None:
            return np.nan, {'error': '输入参数包含None值'}
        
        if not np.isfinite(total_return_rate) or not np.isfinite(observation_years):
            return np.nan, {'error': '输入参数包含无穷大或NaN值'}
        
        if total_return_rate <= -1:
            return np.nan, {'error': f'总收益率不能小于-100%，实际值: {total_return_rate}'}
        
        if observation_years <= 0:
            return np.nan, {'error': f'观测期年数必须大于0，实际值: {observation_years}'}
        
        if observation_years > 100:
            return np.nan, {'error': f'观测期年数过大，可能导致数值不稳定: {observation_years}'}
        
        # 转换为最终价值倍数
        final_value = total_return_rate + 1
        
        # 检查最终价值是否合理
        if final_value <= 0:
            return np.nan, {'error': f'最终价值倍数必须为正数，实际值: {final_value}'}
        
        # 根据方法选择计算方式
        if method == 'log_based':
            # 对数方法：数值稳定性更好
            log_final_value = np.log(final_value)
            if not np.isfinite(log_final_value):
                return np.nan, {'error': '对数计算溢出，数值不稳定'}
            
            annual_log_return = log_final_value / observation_years
            annual_return_rate = np.exp(annual_log_return) - 1
            
            calculation_details = {
                'method': 'log_based',
                'final_value': final_value,
                'log_final_value': log_final_value,
                'annual_log_return': annual_log_return,
                'observation_years': observation_years
            }
            
        else:
            # 标准复利方法：直接幂运算
            annual_return_rate = final_value ** (1/observation_years) - 1
            
            calculation_details = {
                'method': 'standard_compound',
                'final_value': final_value,
                'observation_years': observation_years,
                'calculation': f'{final_value}^(1/{observation_years}) - 1'
            }
        
        # 数值稳定性检查
        if not np.isfinite(annual_return_rate):
            return np.nan, {'error': '年化收益率计算结果数值不稳定'}
        
        # 合理性检查：年化收益率不应该过于极端
        if abs(annual_return_rate) > 10:  # 年化收益率超过1000%
            return np.nan, {'error': f'年化收益率过于极端: {annual_return_rate:.2%}'}
        
        # 添加计算质量评估
        calculation_details.update({
            'annual_return_rate': annual_return_rate,
            'annual_return_percent': annual_return_rate * 100,
            'quality_assessment': {
                'numerical_stability': 'stable' if abs(annual_return_rate) < 5 else ('moderate' if abs(annual_return_rate) < 10 else 'unstable'),
                'return_magnitude': 'extreme_high' if annual_return_rate > 1 else ('high' if annual_return_rate > 0.5 else ('positive' if annual_return_rate > 0 else 'negative')),
                'calculation_reliable': abs(annual_return_rate) < 5  # 超过500%的年化收益率需要额外验证
            }
        })
        
        # 反向验证计算结果（可选验证）
        reconstructed_total_return = (1 + annual_return_rate) ** observation_years - 1
        verification_error = abs(reconstructed_total_return - total_return_rate)
        calculation_details['verification'] = {
            'reconstructed_total_return': reconstructed_total_return,
            'original_total_return': total_return_rate,
            'verification_error': verification_error,
            'verification_passed': verification_error < 1e-6
        }
        
        return annual_return_rate, calculation_details
        
    except Exception as e:
        return np.nan, {
            'error': f'标准复利年化计算错误: {str(e)}',
            'total_return_rate': total_return_rate,
            'observation_years': observation_years
        }

def safe_calculate_annual_return(total_return, years, method='standard_compound'):
    """
    修复4: 安全版本的年化计算函数，确保输入类型正确
    防止类型转换错误，提高代码健壮性
    
    Args:
        total_return: 总收益率（任意数值类型）
        years: 观测年数（任意数值类型）
        method: 计算方法
        
    Returns:
        tuple: (年化收益率, 计算详情字典)
    """
    try:
        # 类型转换与验证
        if not isinstance(total_return, (int, float, np.number)):
            print(f"  警告: 总收益率类型 {type(total_return)} 不兼容，尝试转换...")
            if isinstance(total_return, str):
                total_return = float(total_return)
            else:
                total_return = 0.0  # 使用默认值
                
        if not isinstance(years, (int, float, np.number)):
            print(f"  警告: 观测年数类型 {type(years)} 不兼容，尝试转换...")
            if isinstance(years, str):
                years = float(years)
            else:
                years = 1.0  # 使用默认值
        
        # 调用原始计算函数
        return calculate_standard_annual_return(total_return, years, method)
    except Exception as e:
        print(f"  年化计算出错: {str(e)}")
        return np.nan, {'error': f'年化计算失败: {str(e)}'}

def validate_annual_return_calculation(annual_return, observation_years, original_total_return, tolerance=0.01):
    """
    验证年化收益率计算的正确性（反向验证）- 优化版本
    
    Args:
        annual_return: 年化收益率
        observation_years: 观测期年数
        original_total_return: 原始总收益率
        tolerance: 相对误差容忍度，默认为1%
        
    Returns:
        dict: 验证结果，包含详细分析信息
    """
    try:
        # 输入参数验证
        if annual_return is None or observation_years is None or original_total_return is None:
            return {'valid': False, 'error': '输入参数包含None值'}

        # 修复3: 添加类型检查确保输入是数值类型，防止numpy.isnan类型错误
        try:
            annual_return = float(annual_return)
            observation_years = float(observation_years)
            original_total_return = float(original_total_return)
        except (TypeError, ValueError):
            return {'valid': False, 'error': '输入参数无法转换为数值类型'}

        # 现在可以安全地使用isnan
        if np.isnan(annual_return) or np.isnan(observation_years) or np.isnan(original_total_return):
            return {'valid': False, 'error': '输入参数包含NaN值'}

        if observation_years <= 0:
            return {'valid': False, 'error': f'观测期年数必须大于0，实际值: {observation_years}'}

        if annual_return <= -1:
            return {'valid': False, 'error': f'年化收益率不能小于-100%，实际值: {annual_return}'}
        
        # 使用年化收益率重新计算总收益率
        reconstructed_total_return = (1 + annual_return) ** observation_years - 1
        
        # 计算误差分析
        error = abs(reconstructed_total_return - original_total_return)
        relative_error = error / abs(original_total_return) if abs(original_total_return) > 1e-10 else np.inf
        
        # 数值稳定性检查
        if not np.isfinite(reconstructed_total_return):
            return {'valid': False, 'error': '反向计算结果数值不稳定'}
        
        # 判断是否在容忍范围内
        is_valid = relative_error < tolerance
        
        # 计算额外的验证指标
        original_final_value = original_total_return + 1
        reconstructed_final_value = reconstructed_total_return + 1
        
        # 对数差异（对极端值更敏感）
        if original_final_value > 0 and reconstructed_final_value > 0:
            log_error = abs(np.log(original_final_value) - np.log(reconstructed_final_value))
        else:
            log_error = np.inf
        
        # 收益率差异（百分比形式）
        return_rate_diff = abs(reconstructed_total_return - original_total_return) * 100
        
        # 构建详细验证结果
        validation_result = {
            'valid': is_valid,
            'original_total_return': original_total_return,
            'reconstructed_total_return': reconstructed_total_return,
            'original_final_value': original_final_value,
            'reconstructed_final_value': reconstructed_final_value,
            'absolute_error': error,
            'relative_error': relative_error,
            'log_error': log_error,
            'return_rate_diff_percent': return_rate_diff,
            'tolerance': tolerance,
            'observation_years': observation_years,
            'annual_return': annual_return,
            'validation_passed': is_valid,
            'error_analysis': {
                'absolute_error_level': 'high' if error > 0.1 else ('medium' if error > 0.01 else 'low'),
                'relative_error_level': 'high' if relative_error > 0.1 else ('medium' if relative_error > tolerance else 'low'),
                'numerical_stability': 'unstable' if log_error > 0.1 else ('stable' if log_error < 0.01 else 'moderate')
            }
        }
        
        # 添加详细验证信息
        if is_valid:
            validation_result['validation_summary'] = '验证通过：反向计算结果与原始结果一致'
        else:
            validation_result['validation_summary'] = f'验证失败：相对误差{relative_error:.4f}超过容忍度{tolerance}'
        
        return validation_result
        
    except Exception as e:
        return {
            'valid': False,
            'error': f'验证过程出错: {str(e)}',
            'original_total_return': original_total_return,
            'annual_return': annual_return,
            'observation_years': observation_years
        }

class FactorAnalysis:
    def __init__(self, file_path=None, data=None):
        """
        初始化因子分析类
        
        Args:
            file_path: 数据文件路径（Excel或CSV）
            data: 直接传入的DataFrame数据
        """
        # 使用传入的文件路径，如果没有则使用默认文件
        self.file_path = file_path or DEFAULT_DATA_FILE
        self.data = data
        self.factors = [
             '信号发出时上市天数',
             '日最大跌幅百分比',
             '信号当日收盘涨跌幅',
             '信号后一日开盘涨跌幅',
             '次日开盘后总体下跌幅度',
              '前10日最大涨幅',
               '当日回调'
         ]
        self.return_col = '持股2日收益率'
        self.analysis_results = {}
        
        # 初始化异常统计数据
        self.anomaly_stats = {
            'factor_processing': {},
            'missing_values': {},
            'outliers': {},
            'unique_value_check': {},
            'duplicate_rows': {},
            'data_cleaning': {},
            'ic_calculation': {}
        }
        
        # 如果没有直接传入数据且有文件路径，则加载数据
        if self.data is None and self.file_path:
            self.load_data()
    
    def _calculate_adaptive_annual_returns(self, avg_returns, characteristics, method_info):
        """
        执行自适应年化计算 - 优化版本
        
        核心改进：
        1. 使用标准复利年化方法作为主要计算方式
        2. 保留CAGR方法作为对比方法
        3. 删除线性年化方法（忽视复利效应）
        4. 增强数据特征分析和验证机制
        
        Args:
            avg_returns: 平均收益数据，包含分组收益信息
            characteristics: 数据特征分析结果
            method_info: 选择的年化方法
            
        Returns:
            dict: 年化计算结果，包含标准复利年化、CAGR对比和验证信息
        """
        try:
            print(f"    [处理] 开始自适应年化计算优化...")
            
            # 持股周期和数据特征
            holding_period = characteristics['holding_period_days']
            observation_years = characteristics['observation_period_years']
            total_trades = characteristics['total_trades']
            
            # 步骤1: 计算持股周期总收益率
            # 使用分组平均收益作为持股周期收益率
            period_total_returns = avg_returns['平均收益']
            
            # 步骤2: 应用标准复利年化方法（主要方法）
            print(f"    [统计] 应用标准复利年化方法...")
            standard_annual_returns = []
            validation_results = []
            
            for i, total_return in enumerate(period_total_returns):
                # 修复4: 使用安全版本的年化计算函数，防止类型错误
                annual_return, _ = safe_calculate_annual_return(total_return, observation_years)
                standard_annual_returns.append(annual_return)
                
                # 验证计算结果的正确性
                validation = validate_annual_return_calculation(annual_return, observation_years, total_return)
                validation_results.append(validation)
                
                # 输出验证结果（前3组详细显示）
                if i < 3 and validation['valid']:
                    print(f"      组{i+1}: 总收益{total_return:.4f} -> 年化{annual_return:.4f} ({annual_return*100:.2f}%)")
                elif i < 3:
                    print(f"      组{i+1}: 验证失败 - {validation.get('error', '未知错误')}")
            
            # 转换为numpy数组
            standard_annual_returns = np.array(standard_annual_returns)
            
            # 步骤3: 计算CAGR复合年化（对比方法）
            print(f"    [上升] 计算CAGR复合年化（对比方法）...")
            cagr_annual_returns = []
            
            for total_return in period_total_returns:
                # 修复4: 使用安全版本的年化计算函数，防止类型错误
                # CAGR计算：(1 + 总收益率)^(1/年数) - 1
                # 这与标准复利年化是相同的数学公式
                cagr_return, _ = safe_calculate_annual_return(total_return, observation_years)
                cagr_annual_returns.append(cagr_return)
            
            cagr_annual_returns = np.array(cagr_annual_returns)
            
            # 步骤4: 移除线性年化方法（方法A/B）
            # 不再计算传统的线性年化收益率
            
            # 步骤5: 计算年化风险指标
            print(f"    [下降] 计算年化风险指标...")
            daily_std_returns = avg_returns['收益标准差'] / holding_period
            
            # 使用标准复利年化收益率计算风险指标
            # 年化标准差：考虑复利效应的波动率调整
            annual_std = daily_std_returns * np.sqrt(observation_years * 252 / holding_period)

            # 修复2: 数组形状兼容性检查，防止broadcast错误
            # 确保annual_std是1D数组
            if annual_std.ndim > 1:
                annual_std = annual_std.flatten()
            # 确保standard_annual_returns是1D数组
            if standard_annual_returns.ndim > 1:
                standard_annual_returns = standard_annual_returns.flatten()

            # 年化夏普比率（基于标准复利年化收益率）
            annual_sharpe = np.where(annual_std > 0,
                                    standard_annual_returns / annual_std,
                                    0.0)

            # 年化索提诺比率（简化处理，下行风险使用标准差代替）
            annual_sortino = np.where(annual_std > 0,
                                     standard_annual_returns / annual_std,
                                     0.0)
            
            # 步骤6: 数据质量评估和验证统计
            print(f"    [OK] 数据质量评估...")
            valid_annual_returns = standard_annual_returns[np.isfinite(standard_annual_returns)]
            
            quality_stats = {
                'total_groups': len(standard_annual_returns),
                'valid_groups': len(valid_annual_returns),
                'validation_success_rate': sum(v['valid'] for v in validation_results) / len(validation_results) if validation_results else 0,
                'mean_annual_return': np.mean(valid_annual_returns) if len(valid_annual_returns) > 0 else np.nan,
                'std_annual_return': np.std(valid_annual_returns) if len(valid_annual_returns) > 0 else np.nan,
                'min_annual_return': np.min(valid_annual_returns) if len(valid_annual_returns) > 0 else np.nan,
                'max_annual_return': np.max(valid_annual_returns) if len(valid_annual_returns) > 0 else np.nan
            }
            
            print(f"      有效年化计算: {quality_stats['valid_groups']}/{quality_stats['total_groups']}")
            print(f"      验证成功率: {quality_stats['validation_success_rate']:.1%}")
            print(f"      平均年化收益率: {quality_stats['mean_annual_return']*100:.2f}%" if not np.isnan(quality_stats['mean_annual_return']) else "      平均年化收益率: N/A")
            
            # 步骤7: 构建结果字典
            results = {
                # 主要结果（标准复利年化）
                'standard_compound_annual_return': standard_annual_returns,
                'main_annual_return': standard_annual_returns,  # 保持兼容性
                
                # 对比方法（CAGR）
                'cagr_annual_return': cagr_annual_returns,
                
                # 移除线性年化方法
                'traditional_annual_return': np.full_like(standard_annual_returns, np.nan),  # 返回NaN表示已移除
                
                # 风险指标
                'annual_std': annual_std,
                'annual_sharpe': annual_sharpe,
                'annual_sortino': annual_sortino,
                
                # 基础数据
                'daily_avg_returns': period_total_returns / holding_period,
                'base_frequency': method_info['frequency_base'],
                'daily_std_returns': daily_std_returns,
                
                # 新增：数据质量信息
                'quality_stats': quality_stats,
                'validation_results': validation_results,
                'observation_years': observation_years,
                
                # 计算方法标识
                'calculation_method': 'standard_compound',
                'comparison_method': 'cagr_based',
                'deprecated_methods': ['linear_annual_return_a', 'linear_annual_return_b']
            }
            
            print(f"    [OK] 自适应年化计算完成")
            return results
            
        except Exception as e:
            print(f"    [ERROR] 年化计算出错: {str(e)}")
            # 返回安全的默认值
            n_groups = len(avg_returns)
            return {
                'standard_compound_annual_return': np.full(n_groups, np.nan),
                'main_annual_return': np.full(n_groups, np.nan),
                'cagr_annual_return': np.full(n_groups, np.nan),
                'traditional_annual_return': np.full(n_groups, np.nan),
                'annual_std': np.full(n_groups, np.nan),
                'annual_sharpe': np.full(n_groups, np.nan),
                'annual_sortino': np.full(n_groups, np.nan),
                'daily_avg_returns': np.full(n_groups, np.nan),
                'base_frequency': np.nan,
                'daily_std_returns': np.full(n_groups, np.nan),
                'quality_stats': {'error': str(e)},
                'validation_results': [],
                'observation_years': np.nan,
                'calculation_method': 'error_fallback',
                'comparison_method': 'error_fallback',
                'deprecated_methods': []
            }
    
    def load_data(self):
        """从文件加载数据"""
        try:
            if self.file_path.endswith('.csv'):
                self.data = pd.read_csv(self.file_path, encoding='utf-8-sig')
            elif self.file_path.endswith('.xlsx') or self.file_path.endswith('.xls'):
                self.data = pd.read_excel(self.file_path)
            else:
                raise ValueError("仅支持CSV和Excel文件格式")
            
            return True
        except Exception as e:
            print(f"数据加载失败: {e}")  # 保留错误提示
            return False
    
    def apply_factor_processing(self, df, factor_col, method='standardize', winsorize=True, winsorize_limits=(0.01, 0.99)):
        """
        对因子数据进行处理（标准化和缩尾处理）
        
        Args:
            df: 数据框
            factor_col: 因子列名
            method: 处理方法，'standardize'（标准化）或 'normalize'（归一化）
            winsorize: 是否进行缩尾处理
            winsorize_limits: 缩尾处理的分位数范围
            
        Returns:
            处理后的数据框
        """
        # 复制数据以避免修改原始数据
        processed_df = df.copy()
        
        # 记录处理前的统计信息
        original_stats = {
            'mean': processed_df[factor_col].mean(),
            'std': processed_df[factor_col].std(),
            'min': processed_df[factor_col].min(),
            'max': processed_df[factor_col].max(),
            'q1': processed_df[factor_col].quantile(0.25),
            'q3': processed_df[factor_col].quantile(0.75)
        }
        
        # 缩尾处理
        if winsorize:
            lower_limit = processed_df[factor_col].quantile(winsorize_limits[0])
            upper_limit = processed_df[factor_col].quantile(winsorize_limits[1])
            processed_df[factor_col] = processed_df[factor_col].clip(lower=lower_limit, upper=upper_limit)
            
            # 记录缩尾处理信息（安全检查确保键存在）
            if factor_col not in self.anomaly_stats['factor_processing']:
                self.anomaly_stats['factor_processing'][factor_col] = {}
            winsorized_count = ((df[factor_col] < lower_limit) | (df[factor_col] > upper_limit)).sum()
            self.anomaly_stats['factor_processing'][factor_col]['winsorized_count'] = winsorized_count
            self.anomaly_stats['factor_processing'][factor_col]['winsorize_limits'] = winsorize_limits
        
        # 标准化或归一化处理
        if method == 'standardize':
            # 标准化：(x - mean) / std
            mean_val = processed_df[factor_col].mean()
            std_val = processed_df[factor_col].std()
            if std_val > 0:
                processed_df[factor_col] = (processed_df[factor_col] - mean_val) / std_val
                if factor_col not in self.anomaly_stats['factor_processing']:
                    self.anomaly_stats['factor_processing'][factor_col] = {}
                self.anomaly_stats['factor_processing'][factor_col]['method'] = 'standardize'
                self.anomaly_stats['factor_processing'][factor_col]['params'] = {'mean': mean_val, 'std': std_val}
            else:
                print(f"警告：因子 {factor_col} 标准差为0，无法标准化")
                if factor_col not in self.anomaly_stats['factor_processing']:
                    self.anomaly_stats['factor_processing'][factor_col] = {}
                self.anomaly_stats['factor_processing'][factor_col]['method'] = 'none'
                self.anomaly_stats['factor_processing'][factor_col]['params'] = {'reason': 'std=0'}
                
        elif method == 'normalize':
            # 归一化：(x - min) / (max - min)
            min_val = processed_df[factor_col].min()
            max_val = processed_df[factor_col].max()
            if max_val > min_val:
                processed_df[factor_col] = (processed_df[factor_col] - min_val) / (max_val - min_val)
                if factor_col not in self.anomaly_stats['factor_processing']:
                    self.anomaly_stats['factor_processing'][factor_col] = {}
                self.anomaly_stats['factor_processing'][factor_col]['method'] = 'normalize'
                self.anomaly_stats['factor_processing'][factor_col]['params'] = {'min': min_val, 'max': max_val}
            else:
                print(f"警告：因子 {factor_col} 最大值等于最小值，无法归一化")
                if factor_col not in self.anomaly_stats['factor_processing']:
                    self.anomaly_stats['factor_processing'][factor_col] = {}
                self.anomaly_stats['factor_processing'][factor_col]['method'] = 'none'
                self.anomaly_stats['factor_processing'][factor_col]['params'] = {'reason': 'max=min'}
        
        # 记录处理后的统计信息
        processed_stats = {
            'mean': processed_df[factor_col].mean(),
            'std': processed_df[factor_col].std(),
            'min': processed_df[factor_col].min(),
            'max': processed_df[factor_col].max(),
            'q1': processed_df[factor_col].quantile(0.25),
            'q3': processed_df[factor_col].quantile(0.75)
        }
        
        # 记录处理后的统计信息
        if factor_col not in self.anomaly_stats['factor_processing']:
            self.anomaly_stats['factor_processing'][factor_col] = {}
        if factor_col not in self.anomaly_stats['factor_processing']:
            self.anomaly_stats['factor_processing'][factor_col] = {}
        self.anomaly_stats['factor_processing'][factor_col]['original_stats'] = original_stats
        self.anomaly_stats['factor_processing'][factor_col]['processed_stats'] = processed_stats
        
        return processed_df
    
    def preprocess_data(self, process_factors=False, factor_method='standardize', winsorize=True, winsorize_limits=(0.01, 0.99)):
        """
        数据预处理方法 - 处理百分比字符串和数值转换
        
        Args:
            process_factors: 是否处理因子数据，默认为False
            factor_method: 因子处理方法 ('standardize', 'normalize', 'rank'), 默认为'standardize'
            winsorize: 是否进行缩尾处理，默认为True
            winsorize_limits: 缩尾处理的上下限分位数，默认为(0.01, 0.99)
            
        Returns:
            bool: 预处理是否成功
        """
        if self.data is None or self.data.empty:
            print("错误: 没有数据可处理")
            return False
        
        try:
            # 复制数据
            df = self.data.copy()
            
            # 初始化异常数据统计信息字典
            self.anomaly_stats = {
                'missing_values': {},
                'outliers': {},
                'unique_value_check': {},
                'duplicate_rows': {},
                'factor_processing': {}
            }
            
            # 检查必要的列是否存在
            required_cols = ['股票代码', '股票名称', '信号日期', self.return_col]
            for factor in self.factors:
                required_cols.append(factor)
            
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                print(f"错误：缺少必要的列: {missing_cols}")
                return False
            
            # 处理百分比字符串列（转换百分比）
            percentage_columns = [
                '日最大跌幅百分比', '信号当日收盘涨跌幅', '信号后一日开盘涨跌幅', 
                '次日开盘后总体下跌幅度', '前10日最大涨幅', '当日回调', '持股2日收益率'
            ]
            
            # 处理包含百分比符号的数值列
            for col in percentage_columns:
                if col in df.columns:
                    # 如果列是字符串类型且包含%
                    if df[col].dtype == 'object':
                        try:
                            # 转换百分比字符串为数值（去除%并除以100）
                            df[col] = pd.to_numeric(df[col].astype(str).str.replace('%', ''), errors='coerce') / 100
                            print(f"已转换列 '{col}' 从百分比字符串到数值")
                        except Exception as e:
                            print(f"转换列 '{col}' 时出错: {e}")
                    # 注释掉以下代码，不再对已经是数值型的百分比列进行除以100操作
                    # else:
                    #     # 如果已经是数值但可能在0-1范围外，标准化到合理范围
                    #     try:
                    #         if df[col].abs().max() > 1.0:
                    #             df[col] = df[col] / 100
                    #             print(f"已转换列 '{col}' 从百分比数值到小数")
                    #     except Exception as e:
                    #         print(f"标准化列 '{col}' 时出错: {e}")
            
            # 确保日期列正确处理
            if '信号日期' in df.columns:
                try:
                    df['信号日期'] = pd.to_datetime(df['信号日期'], errors='coerce')
                except:
                    print("警告：无法转换信号日期列")
            
            # 处理数值型因子并记录异常信息
            for factor in self.factors:
                print(f"处理因子: {factor}")
                # 初始化因子处理统计信息
                self.anomaly_stats['factor_processing'][factor] = {
                    'processed': process_factors,
                    'method': factor_method,
                    'params': {'winsorize': winsorize, 'winsorize_limits': winsorize_limits}
                }
                
                # 尝试转换为数值型
                if not pd.api.types.is_numeric_dtype(df[factor]):
                    try:
                        original_dtype = str(df[factor].dtype)
                        df[factor] = pd.to_numeric(df[factor], errors='coerce')
                        print(f"  因子 {factor} 从 {original_dtype} 转换为数值型")
                    except:
                        print(f"警告：无法将因子 {factor} 转换为数值型")
                
                # 记录缺失值信息
                missing_count = df[factor].isna().sum()
                self.anomaly_stats['missing_values'][factor] = missing_count
                if missing_count > 0:
                    print(f"  因子 {factor} 有 {missing_count} 个缺失值 ({missing_count/len(df):.2%})")
                
                # 3倍标准差检测异常值（仅记录不删除）
                valid_data = df[factor].dropna()
                if len(valid_data) > 0:
                    mean_val = valid_data.mean()
                    std_val = valid_data.std()
                    lower_bound_std = mean_val - 3 * std_val
                    upper_bound_std = mean_val + 3 * std_val
                    outlier_count_std = len(valid_data[(valid_data < lower_bound_std) | (valid_data > upper_bound_std)])
                    
                    self.anomaly_stats['outliers'][factor] = {
                        'count': outlier_count_std,
                        'percentage': outlier_count_std/len(df) if len(df) > 0 else 0,
                        'bounds': {'lower': lower_bound_std, 'upper': upper_bound_std}
                    }
                    
                    if outlier_count_std > 0:
                        print(f"  因子 {factor}: 检测到 {outlier_count_std} 个3倍标准差异常值 ({outlier_count_std/len(df):.2%})")
                
                # 唯一值比例检查（低唯一值比例可能表示数据问题）
                if df[factor].nunique() < len(df) * 0.05 and len(df) > 0:
                    unique_pct = df[factor].nunique() / len(df)
                    self.anomaly_stats['unique_value_check'][factor] = unique_pct
                    print(f"  警告：因子 {factor} 唯一值比例过低 ({unique_pct:.2%})，可能存在数据质量问题")
                
                # 如果需要对因子进行处理
                if process_factors:
                    print(f"  对因子 {factor} 进行 {factor_method} 处理")
                    df = self.apply_factor_processing(df, factor, factor_method, winsorize, winsorize_limits)
            
            # 处理收益率列
            if not pd.api.types.is_numeric_dtype(df[self.return_col]):
                try:
                    # 如果是百分比字符串，先去除百分号再转换
                    if df[self.return_col].dtype == 'object':
                        df[self.return_col] = df[self.return_col].str.replace('%', '')
                    df[self.return_col] = pd.to_numeric(df[self.return_col], errors='coerce')
                    print(f"收益率列 {self.return_col} 转换为数值型")
                except:
                    print(f"警告：无法将 {self.return_col} 转换为数值型")
            
            # 记录收益率列的缺失值和异常值
            missing_return_count = df[self.return_col].isna().sum()
            self.anomaly_stats['missing_values'][self.return_col] = missing_return_count
            if missing_return_count > 0:
                print(f"收益率列 {self.return_col} 有 {missing_return_count} 个缺失值")
            
            # 记录重复行信息
            duplicate_rows = df.duplicated().sum()
            self.anomaly_stats['duplicate_rows']['count'] = duplicate_rows
            if duplicate_rows > 0:
                print(f"检测到 {duplicate_rows} 行重复数据")
            
            # 注意：根据用户要求，我们不删除任何数据，只记录异常信息
            # 仅删除收益率和因子列的缺失值行，以确保分析有意义的数据
            original_len = len(df)
            df = df.dropna(subset=[self.return_col] + self.factors)
            self.anomaly_stats['missing_values']['total_removed'] = original_len - len(df)
            
            if len(df) < original_len:
                print(f"数据清理：删除 {original_len - len(df)} 行缺失值")
            
            # 记录原始数据统计信息
            self.anomaly_stats['original_data_count'] = original_len
            self.anomaly_stats['analyzed_data_count'] = len(df)
            
            # 简化样本筛选信息输出
            final_count = len(df)
            removed_count = original_len - final_count
            if removed_count > 0:
                print(f"数据预处理完成：保留 {final_count}/{original_len} 行有效数据")
            
            self.processed_data = df

            self.processed_data = df
            return True
            
        except Exception as e:
            print(f"数据预处理失败: {e}")
            return False
    
    def calculate_ic(self, factor_col, use_pearson=False, use_robust_corr=False, use_kendall=False, 
                     use_nonparam_test=False, compute_bootstrap_ci=False, n_bootstrap=1000):
        """
        计算因子IC值，支持多种稳健性统计方法
        
        Args:
            factor_col: 因子列名
            use_pearson: 是否使用Pearson相关系数，默认为False（使用Spearman）
            use_robust_corr: 是否使用稳健相关系数（Spearman + Kendall组合），默认为False
            use_kendall: 是否使用Kendall's Tau相关系数，默认为False
            use_nonparam_test: 是否进行非参数检验，默认为False
            compute_bootstrap_ci: 是否计算Bootstrap置信区间，默认为False
            n_bootstrap: Bootstrap重抽样次数，默认1000次
            
        Returns:
            tuple: (IC均值, IC标准差, t统计量, p值, 额外统计结果字典)
        """
        # 使用预处理后的数据，确保因子处理生效
        df = self.processed_data if hasattr(self, 'processed_data') and self.processed_data is not None else self.data.copy()
        
        # 确保数据有效
        if df.empty or factor_col not in df.columns or self.return_col not in df.columns:
            print(f"警告: 数据为空或列名不存在")
            return (np.nan, np.nan, np.nan, np.nan, {})
        
        corr_type = "Pearson" if use_pearson else "Spearman"
        print(f"计算因子 {factor_col} 的 {corr_type} IC值")
        
        # 计算平均每日样本数量并应用动态筛选策略
        daily_sample_counts = []
        for date, group in df.groupby('信号日期'):
            valid_data = group.dropna(subset=[factor_col, self.return_col])
            daily_sample_counts.append(len(valid_data))
        
        avg_daily_samples = np.mean(daily_sample_counts) if daily_sample_counts else 0
        
        # 根据平均每日样本数量选择不同的样本筛选方式
        if avg_daily_samples >= 5:
            min_samples_per_day = 5
            mode = "高样本量模式"
        elif avg_daily_samples >= 3:
            min_samples_per_day = 3
            mode = "中样本量模式"
        else:
            min_samples_per_day = 2
            mode = "低样本量模式"
        
        # 尝试按日期分组计算每日IC值
        daily_ics = []
        skipped_dates = 0
        
        # 初始化异常统计
        if not hasattr(self, 'anomaly_stats'):
            self.anomaly_stats = {}
        
        if 'ic_calculation' not in self.anomaly_stats:
            self.anomaly_stats['ic_calculation'] = {}
        
        self.anomaly_stats['ic_calculation'][factor_col] = {
            'total_dates': len(df['信号日期'].unique()),
            'processed_dates': 0,
            'skipped_dates': 0,
            'skipped_reasons': [],
            'avg_daily_samples': avg_daily_samples,
            'screening_mode': mode,
            'min_samples_per_day': min_samples_per_day
        }
        
        try:
            # 按日期分组
            for date, group in df.groupby('信号日期'):
                # 确保daily_ics始终是列表类型，防止"len() of unsized object"错误
                daily_ics = ensure_list(daily_ics, "daily_ics")
                
                # 确保每组有足够的数据点
                valid_data = group.dropna(subset=[factor_col, self.return_col])
                
                # 重要：保持原始数据不变，只进行缺失值处理
                # 不进行任何异常值修改或数据清洗，确保结果的真实性
                
                if len(valid_data) >= min_samples_per_day:
                    # 检查因子值变异性
                    factor_values = valid_data[factor_col]
                    return_values = valid_data[self.return_col]
                    factor_variability = factor_values.nunique()
                    return_variability = return_values.nunique()
                    
                    # 增加变异性检查，避免除零错误
                    factor_std = factor_values.std()
                    return_std = return_values.std()
                    
                    # 根据动态策略调整变异性要求
                    # 首先检查标准差是否为零
                    if factor_std <= 0 or return_std <= 0:
                        # 如果因子值或收益率值无变异性，尝试使用整体数据计算
                        try:
                            # 获取该日期的所有有效数据（不仅仅是当前日期的数据）
                            all_valid_data = df.dropna(subset=[factor_col, self.return_col])
                            
                            if len(all_valid_data) >= 3:  # 至少需要3个样本点
                                # 使用整体数据计算IC，而不是按日期计算
                                overall_ic = np.corrcoef(all_valid_data[factor_col], all_valid_data[self.return_col])[0, 1]
                                if not np.isnan(overall_ic) and np.isfinite(overall_ic):
                                    # 在append之前确保daily_ics是列表类型
                                    daily_ics = ensure_list(daily_ics, "daily_ics")
                                    daily_ics.append(overall_ic)
                                    self.anomaly_stats['ic_calculation'][factor_col]['processed_dates'] += 1
                                    reason = f"日期 {date}: 使用整体数据计算IC (因子std: {factor_std:.6f}, 收益率std: {return_std:.6f})"
                                    print(f"  {reason}")
                                    continue
                        except Exception as e:
                            print(f"  日期 {date}: 使用整体数据计算IC时出错 - {str(e)}")
                        
                        # 如果无法使用整体数据计算，记录原因并跳过
                        if factor_std <= 0:
                            reason = f"日期 {date}: 因子值标准差为零 (无变异性)"
                        else:
                            reason = f"日期 {date}: 收益率值标准差为零 (无变异性)"
                            
                        self.anomaly_stats['ic_calculation'][factor_col]['skipped_reasons'].append(reason)
                        print(f"  {reason}")
                        skipped_dates += 1
                        continue
                    
                    # 根据平均每日样本数量动态设置变异性要求
                    if avg_daily_samples >= 5:
                        min_factor_variability = 5
                        min_return_variability = 5
                    elif avg_daily_samples >= 3:
                        min_factor_variability = 3
                        min_return_variability = 3
                    else:
                        min_factor_variability = 2
                        min_return_variability = 2
                    
                    # 然后检查变异性要求
                    if (factor_variability >= min_factor_variability and
                        return_variability >= min_return_variability):
                        try:
                            # 根据参数选择相关系数计算方法
                            if use_pearson:
                                # 使用Pearson相关系数，增加类型安全检查
                                factor_values_clean = np.asarray(factor_values, dtype=float)
                                return_values_clean = np.asarray(return_values, dtype=float)
                                # 移除NaN值
                                mask = ~(np.isnan(factor_values_clean) | np.isnan(return_values_clean))
                                factor_values_clean = factor_values_clean[mask]
                                return_values_clean = return_values_clean[mask]
                                
                                if len(factor_values_clean) >= 2:
                                    daily_ic = np.corrcoef(factor_values_clean, return_values_clean)[0, 1]
                                else:
                                    daily_ic = np.nan
                            else:
                                # 使用自定义的Spearman相关系数计算函数，确保数学准确性
                                daily_ic = custom_spearman_corr(factor_values, return_values)
                            
                            if not np.isnan(daily_ic) and np.isfinite(daily_ic):
                                # 添加调试信息：检查daily_ic的类型和形状
                                print(f"    调试: daily_ic类型={type(daily_ic)}, 值={daily_ic}, 形状={getattr(daily_ic, 'shape', 'N/A')}")
                                
                                # 确保daily_ic是标量值
                                if hasattr(daily_ic, 'shape') and daily_ic.shape:
                                    # 如果是数组，取第一个元素
                                    daily_ic = daily_ic.item() if daily_ic.size > 0 else np.nan
                                    print(f"    调试: 转换为标量后daily_ic={daily_ic}")
                                
                                # 在append之前确保daily_ics是列表类型
                                daily_ics = ensure_list(daily_ics, "daily_ics")
                                daily_ics.append(daily_ic)
                                self.anomaly_stats['ic_calculation'][factor_col]['processed_dates'] += 1
                            else:
                                # 记录计算结果为NaN或无穷大的情况
                                reason = f"日期 {date}: 计算结果为NaN或无穷大 (因子std: {factor_std:.6f}, 收益率std: {return_std:.6f})"
                                self.anomaly_stats['ic_calculation'][factor_col]['skipped_reasons'].append(reason)
                                skipped_dates += 1
                                print(f"  {reason}")
                        except Exception as e:
                            error_msg = f"日期 {date}: 计算错误 - {str(e)}"
                            self.anomaly_stats['ic_calculation'][factor_col]['skipped_reasons'].append(error_msg)
                            print(f"  {error_msg}")
                            skipped_dates += 1
                            continue
                    else:
                        # 记录跳过的日期及原因
                        if factor_variability < min_factor_variability:
                            reason = f"日期 {date}: 因子值变异性不足 (唯一值: {factor_variability}, 要求: {min_factor_variability})"
                            self.anomaly_stats['ic_calculation'][factor_col]['skipped_reasons'].append(reason)
                            print(f"  {reason}")
                        elif return_variability < min_return_variability:
                            reason = f"日期 {date}: 收益率值变异性不足 (唯一值: {return_variability}, 要求: {min_return_variability})"
                            self.anomaly_stats['ic_calculation'][factor_col]['skipped_reasons'].append(reason)
                            print(f"  {reason}")
                        skipped_dates += 1
                else:
                    reason = f"日期 {date}: 有效数据点不足 (需要≥{min_samples_per_day}，实际: {len(valid_data)})"
                    self.anomaly_stats['ic_calculation'][factor_col]['skipped_reasons'].append(reason)
                    skipped_dates += 1
        
            # 如果成功计算了每日IC值
            daily_ics = ensure_list(daily_ics, "daily_ics")
            if daily_ics and isinstance(daily_ics, list):
                ic_mean = np.mean(daily_ics)
                ic_std = np.std(daily_ics, ddof=1)  # 使用样本标准差（无偏估计）
                
                # 统计有效日期和样本信息
                total_dates = len(df['信号日期'].unique())
                # 确保daily_ics是列表类型
                daily_ics = ensure_list(daily_ics, "daily_ics")
                valid_dates = len(daily_ics)
                valid_pct = valid_dates / total_dates if total_dates > 0 else 0
                
                print(f"IC计算完成：{valid_dates}/{total_dates} 个有效交易日")
                
                # 构建额外的统计结果字典
                extra_stats = {}
                
                # 如果启用稳健性统计方法，计算额外的IC值
                if use_kendall or use_robust_corr:
                    # 计算所有有效IC值的Kendall's Tau
                    daily_ics = ensure_list(daily_ics, "daily_ics")
                    if HAS_SCIPY and daily_ics and len(daily_ics) > 0:
                        from scipy.stats import kendalltau
                        kt, _ = kendalltau(range(len(daily_ics)), daily_ics)
                        extra_stats['kendall_tau'] = kt
                
                if use_robust_corr:
                    daily_ics = ensure_list(daily_ics, "daily_ics")
                    if daily_ics and len(daily_ics) > 0:
                        # 计算稳健相关系数（基于每日IC值）
                        extra_stats['robust_corr'] = robust_correlation(range(len(daily_ics)), daily_ics)
                
                if use_nonparam_test:
                    daily_ics = ensure_list(daily_ics, "daily_ics")
                    if daily_ics and len(daily_ics) > 0:
                        # 对IC值序列进行非参数检验（检验是否显著不同于0）
                        extra_stats['wilcoxon_test'] = mann_whitney_u_test(daily_ics, [0.0] * len(daily_ics))
                
                if compute_bootstrap_ci:
                    daily_ics = ensure_list(daily_ics, "daily_ics")
                    if daily_ics and len(daily_ics) > 0:
                        # 对IC均值计算Bootstrap置信区间
                        bootstrap_results = bootstrap_confidence_interval(daily_ics, None, n_bootstrap=n_bootstrap)
                        extra_stats['bootstrap_ci'] = bootstrap_results
                
                print(f"IC计算完成：{valid_dates}/{total_dates} 个有效交易日")
                
        except Exception as e:
            print(f"  按日期分组计算IC时出错: {str(e)}")
        
        # 计算t统计量和p值
        # 加强daily_ics类型检查和修复
        daily_ics = ensure_list(daily_ics, "daily_ics")
        # 进一步检查daily_ics是否为空或包含非数值元素
        try:
            # 尝试过滤出数值元素
            valid_ics = []
            for ic in daily_ics:
                if isinstance(ic, (int, float, np.number)) and not np.isnan(ic) and np.isfinite(ic):
                    valid_ics.append(float(ic))
            daily_ics = valid_ics
            print(f"  修复后daily_ics包含 {len(daily_ics)} 个有效IC值")
        except Exception as e:
            print(f"  daily_ics修复失败: {e}，重置为空列表")
        # 修复1: 确保daily_ics是列表类型，防止"len() of unsized object"错误

        daily_ics = ensure_list(daily_ics, "daily_ics")
        if daily_ics:
            n = len(daily_ics)
            ic_mean = np.mean(daily_ics)
            ic_std = np.std(daily_ics, ddof=1)
            
            if n >= 5 and ic_std > 0:
                t_stat = ic_mean / (ic_std / np.sqrt(n))
                dof = n - 1

                # 计算p值
                if HAS_SCIPY:
                    from scipy.stats import t
                    p_value = 2 * (1 - t.cdf(abs(t_stat), dof))
                else:
                    import math
                    t_abs = abs(t_stat)
                    p_value = 2 * (1 - 0.5 * (1 + math.erf(t_abs / math.sqrt(2))))

                return (ic_mean, ic_std, t_stat, p_value, extra_stats)
            else:


                print(f"  警告: 有效IC值数量不足或标准差为0，无法计算t统计量")
                return (ic_mean, ic_std, np.nan, np.nan, extra_stats if 'extra_stats' in locals() else {})
        else:
            print(f"  警告: 没有成功计算任何每日IC值，尝试整体计算")
            return (np.nan, np.nan, np.nan, np.nan, {})
            daily_ics = []
        
        # 修复1: 确保daily_ics是列表类型，防止"len() of unsized object"错误
        daily_ics = ensure_list(daily_ics, "daily_ics")
        
        n = len(daily_ics)
        if n >= 5 and ic_std > 0:
            t_stat = ic_mean / (ic_std / np.sqrt(n))
            dof = n - 1

            # 计算p值
            if HAS_SCIPY:
                from scipy.stats import t
                p_value = 2 * (1 - t.cdf(abs(t_stat), dof))
            else:
                import math
                t_abs = abs(t_stat)
                p_value = 2 * (1 - 0.5 * (1 + math.erf(t_abs / math.sqrt(2))))

            return (ic_mean, ic_std, t_stat, p_value, extra_stats)
        else:
            print(f"  警告: 有效IC值数量不足或标准差为0，无法计算t统计量")
            return (ic_mean, ic_std, np.nan, np.nan, extra_stats if 'extra_stats' in locals() else {})
        
        print(f"  警告: 没有成功计算任何每日IC值，尝试整体计算")
    
        # 如果按日期分组计算失败，尝试整体计算IC值
        try:
            valid_data = df.dropna(subset=[factor_col, self.return_col])
            
            # 确保数据安全性：转换为numpy数组并进行类型检查
            factor_data = np.asarray(valid_data[factor_col], dtype=float)
            return_data = np.asarray(valid_data[self.return_col], dtype=float)
            
            # 移除NaN值和无穷值
            valid_mask = np.isfinite(factor_data) & np.isfinite(return_data)
            factor_data = factor_data[valid_mask]
            return_data = return_data[valid_mask]
            
            # 根据平均每日样本数量调整整体计算的样本量要求
            if avg_daily_samples >= 5:
                min_overall_samples = 25
                min_factor_variability = 5
                min_return_variability = 5
            elif avg_daily_samples >= 3:
                min_overall_samples = 15
                min_factor_variability = 3
                min_return_variability = 3
            else:
                min_overall_samples = 10
                min_factor_variability = 2
                min_return_variability = 2
            
            # 增加更严格的数据质量检查
            if len(factor_data) >= min_overall_samples:
                # 检查因子值和收益率值的变异性
                factor_variability = len(np.unique(factor_data))
                return_variability = len(np.unique(return_data))
                
                if factor_variability >= min_factor_variability and return_variability >= min_return_variability:
                    if use_pearson:
                        # 使用增强的Pearson相关系数计算
                        if len(factor_data) >= 2:
                            overall_ic = np.corrcoef(factor_data, return_data)[0, 1]
                        else:
                            overall_ic = np.nan
                    elif HAS_SCIPY:
                        # 使用scipy计算整体Spearman相关系数，增加类型安全
                        if len(factor_data) >= 2:
                            from scipy.stats import spearmanr
                            overall_ic, _ = spearmanr(factor_data, return_data)
                        else:
                            overall_ic = np.nan
                    else:
                        # 手动计算Spearman相关系数，增加类型检查
                        if len(factor_data) >= 2:
                            try:
                                factor_rank = pd.Series(factor_data).rank().values
                                return_rank = pd.Series(return_data).rank().values
                                overall_ic = np.corrcoef(factor_rank, return_rank)[0, 1]
                            except:
                                overall_ic = np.nan
                        else:
                            overall_ic = np.nan
                    
                    if not np.isnan(overall_ic) and np.isfinite(overall_ic):
                        print(f"  成功计算整体IC值: {overall_ic:.6f}")
                        print(f"  数据量: {len(factor_data)}, 因子唯一值: {factor_variability}, 收益率唯一值: {return_variability}")
                        
                        # 估算IC标准差（使用抽样分布的理论标准差）
                        n = len(factor_data)
                        # Spearman相关系数的理论标准差近似
                        if n > 2:
                            ic_std = np.sqrt((1 - overall_ic**2) / (n - 2))
                        else:
                            ic_std = np.nan
                        
                        # 计算t统计量和p值
                        if n >= min_overall_samples:
                            # 避免除以零的情况
                            if abs(overall_ic) < 1.0:  # 确保分母不为零
                                # Spearman相关系数的t统计量计算
                                t_stat = overall_ic * np.sqrt((n - 2) / (1 - overall_ic**2))
                                dof = n - 2
                                
                                # 计算p值
                                if HAS_SCIPY:
                                    from scipy.stats import t
                                    p_value = 2 * (1 - t.cdf(abs(t_stat), dof))
                                else:
                                    import math
                                    t_abs = abs(t_stat)
                                    p_value = 2 * (1 - 0.5 * (1 + math.erf(t_abs / math.sqrt(2))))
                                
                                # 构建额外的统计结果字典
                                extra_stats = {}
                                
                                # 如果启用稳健性统计方法，添加更多统计量
                                if use_kendall or use_robust_corr:
                                    extra_stats['kendall_tau'] = kendall_tau_corr(factor_data, return_data)
                                
                                if use_robust_corr:
                                    extra_stats['robust_corr'] = robust_correlation(factor_data, return_data)
                                
                                if use_nonparam_test:
                                    extra_stats['mann_whitney_u'] = mann_whitney_u_test(factor_data, return_data)
                                
                                if compute_bootstrap_ci:
                                    bootstrap_results = bootstrap_confidence_interval(factor_data, return_data, n_bootstrap=n_bootstrap)
                                    extra_stats['bootstrap_ci'] = bootstrap_results
                                
                                return (overall_ic, ic_std, t_stat, p_value, extra_stats)
                            else:
                                print(f"  警告: 相关系数为±1，无法计算t统计量")
                                return (overall_ic, ic_std, np.nan, np.nan, {})
                        else:
                            return (overall_ic, ic_std, np.nan, np.nan, {})
                    else:
                        print(f"  警告: 整体数据变异性不足 - 因子唯一值: {factor_variability}, 收益率唯一值: {return_variability}")
            else:
                print(f"  警告: 整体数据量不足，无法计算有效的整体IC值")
                
        except Exception as e:
            print(f"  计算整体IC值时出错: {e}")
        
        # 如果所有计算方法都失败
        print("  无法计算IC值")
        return (np.nan, np.nan, np.nan, np.nan, {})
    
    def calculate_group_returns(self, factor_col, n_groups=5):
        """
        计算分组收益 - 使用简单的等分分组方式：直接对完整因子数据排序后平均分配，不按日期分组处理
        
        Args:
            factor_col: 因子列名
            n_groups: 分组数量
            
        Returns:
            dict: 包含分组收益和多空收益的字典
        """
        # 使用预处理后的数据，确保因子处理生效
        df = self.processed_data if hasattr(self, 'processed_data') and self.processed_data is not None else self.data.copy()
        
        # 确保数据有效
        if df.empty or factor_col not in df.columns or self.return_col not in df.columns:
            print(f"警告: 数据为空或列名不存在")
            return None
        
        print(f"使用预处理后的数据进行分组，总样本数: {len(df)}")
        
        # 统计分组收益计算的样本筛选情况
        total_samples = len(df)
        df_clean = df[df[factor_col].notna()].copy()
        valid_samples = len(df_clean)
        removed_samples = total_samples - valid_samples
        
        if len(df_clean) == 0:
            print(f"警告: 去除因子值为空的行后没有剩余数据")
            return None
        
        # 使用简单的等分分组方式
        # 1. 将因子数据从小到大排列
        # 2. 平均分成n_groups份
        df_clean = df_clean.sort_values(by=factor_col)
        
        # 计算每个样本应该属于哪个分组
        total_samples = len(df_clean)
        group_size = total_samples // n_groups
        remainder = total_samples % n_groups
        
        # 创建分组标签
        groups = []
        for i in range(n_groups):
            # 前remainder个分组每个多分配1个样本
            group_count = group_size + (1 if i < remainder else 0)
            groups.extend([i+1] * group_count)
        
        # 分配分组标签
        df_clean['分组'] = groups[:total_samples]  # 确保长度匹配
        
        # 验证分组样本数量分布
        group_counts = df_clean['分组'].value_counts().sort_index()
        if len(group_counts) > 0:
            min_count = group_counts.min()
            max_count = group_counts.max()
            # 如果样本数量差异超过10%，发出警告
            if max_count > min_count * 1.1:
                print(f"警告: 分组样本数量分布不均，最小: {min_count}, 最大: {max_count}")
        
        # 计算每组的平均收益、标准差和样本数量
        # 同时计算每组因子值的最小值和最大值
        group_stats = df_clean.groupby('分组').agg({
            self.return_col: ['mean', 'std', 'count'],
            factor_col: ['min', 'max']
        }).reset_index()
        
        # 重命名列
        group_stats.columns = ['分组', '平均收益', '收益标准差', '样本数量', '因子最小值', '因子最大值']
        
        # 创建参数区间列
        # 使用更统一的格式化方法，避免显示不一致
        # 注释掉对百分比因子的特殊处理，统一使用原始数据
        # percentage_columns = [
        #     '日最大跌幅百分比', '信号当日收盘涨跌幅', '信号后一日开盘涨跌幅', 
        #     '次日开盘后总体下跌幅度', '前10日最大涨幅', '当日回调', '持股2日收益率'
        # ]
        
        # 注释掉对百分比因子的特殊处理，统一使用原始数据
        # if factor_col in percentage_columns:
        #     # 对于百分比因子，将值乘以100恢复为原始百分比形式
        #     group_stats['参数区间'] = group_stats.apply(lambda x: f"{x['因子最小值']*100:.4f}-{x['因子最大值']*100:.4f}", axis=1)
        # else:
        #     # 对于非百分比因子，保持原样
        #     group_stats['参数区间'] = group_stats.apply(lambda x: f"{x['因子最小值']:.4f}-{x['因子最大值']:.4f}", axis=1)
            
        # 使用原始数据，不进行任何转换，修改为使用"到"分隔符避免Excel解析错误
        group_stats['参数区间'] = group_stats.apply(lambda x: f"{x['因子最小值']:.4f}到{x['因子最大值']:.4f}", axis=1)
        
        # 检测并警告异常大的区间跨度
        for idx, row in group_stats.iterrows():
            span = row['因子最大值'] - row['因子最小值']
            # 计算所有组的平均跨度
            avg_span = group_stats['因子最大值'].mean() - group_stats['因子最小值'].mean()
            # 如果某组跨度超过平均跨度的3倍，发出警告
            if span > 3 * avg_span and span > 0:
                print(f"警告: 第{int(row['分组'])}组的参数区间跨度异常大: {span:.4f}")
        
        # 保留需要的列
        avg_returns = group_stats[['分组', '平均收益', '收益标准差', '样本数量', '参数区间']]
        
        # 简化的分组完成提示
        total_samples = avg_returns['样本数量'].sum()
        print(f"分组完成，共 {n_groups} 组，总样本数: {total_samples}")
        
        # 确保分组从1到n_groups连续
        expected_groups = list(range(1, n_groups + 1))
        for g in expected_groups:
            if g not in avg_returns['分组'].values:
                print(f"警告: 未找到分组 {g}，创建默认记录")
                new_row = pd.DataFrame({
                    '分组': [g],
                    '平均收益': [0.0],
                    '收益标准差': [0.0],
                    '样本数量': [0]
                })
                avg_returns = pd.concat([avg_returns, new_row], ignore_index=True)
        
        # 按分组排序
        avg_returns = avg_returns.sort_values('分组').reset_index(drop=True)
        
        # 计算t统计量和p值
        t_stats = []
        p_values = []
        
        for _, row in avg_returns.iterrows():
            group_num = row['分组']
            # 从原始数据中获取该分组的数据
            group_data = df_clean[df_clean['分组'] == group_num][self.return_col]
            
            if len(group_data) > 1:
                # 计算样本标准差
                std = group_data.std(ddof=1)
                if std > 0:
                    # 计算t统计量
                    t_stat = row['平均收益'] / (std / np.sqrt(len(group_data)))
                    
                    # 计算p值
                    if HAS_SCIPY:
                        from scipy.stats import t
                        p_value = 2 * (1 - t.cdf(abs(t_stat), len(group_data) - 1))
                        # 为非常小的p值设置最小值，避免显示为0
                        p_value = max(p_value, 1e-10)
                    else:
                        # 不使用scipy时，使用数学公式计算
                        import math
                        dof = len(group_data) - 1
                        
                        # 对于大自由度，可以使用正态近似
                        if dof > 30:
                            z_score = t_stat
                            p_value = 2 * (1 - 0.5 * (1 + math.erf(z_score / math.sqrt(2))))
                        else:
                            # 对于小自由度，使用更简单的近似
                            p_value = 2 * math.exp(-t_stat**2 / 2)
                        # 为非常小的p值设置最小值
                        p_value = max(p_value, 1e-10)
                else:
                    t_stat = np.nan
                    p_value = np.nan
            else:
                t_stat = np.nan
                p_value = np.nan
            
            t_stats.append(t_stat)
            p_values.append(p_value)
        
        avg_returns['T统计量'] = t_stats
        avg_returns['P值'] = p_values
        
        # 计算每个分组的胜率、最大回撤、夏普率和索提诺比率
        win_rates = []
        max_drawdowns = []
        sharpe_ratios = []
        sortino_ratios = []
        
        for _, row in avg_returns.iterrows():
            group_num = row['分组']
            # 从原始数据中获取该分组的数据
            group_data = df_clean[df_clean['分组'] == group_num][self.return_col]
            
            if len(group_data) > 0:
                # 计算胜率：收益为正的样本占比
                positive_count = (group_data > 0).sum()
                win_rate = positive_count / len(group_data) if len(group_data) > 0 else 0
                win_rates.append(win_rate)
                
                # 计算最大回撤
                if len(group_data) > 1:
                    cumulative_returns = (1 + group_data).cumprod()
                    running_max = cumulative_returns.expanding().max()
                    drawdown = (cumulative_returns - running_max) / running_max
                    max_drawdown = abs(drawdown.min())
                    max_drawdowns.append(max_drawdown)
                else:
                    max_drawdowns.append(0.0)
                
                # 计算单期夏普率（用于年化转换）
                if row['收益标准差'] > 0:
                    single_period_sharpe = row['平均收益'] / row['收益标准差']
                    sharpe_ratios.append(single_period_sharpe)
                else:
                    sharpe_ratios.append(0.0)
                
                # 计算单期索提诺比率（用于年化转换）
                downside_returns = group_data[group_data < 0]
                if len(downside_returns) > 0 and len(downside_returns) > 1:
                    downside_std = downside_returns.std(ddof=1)
                    if downside_std > 0:
                        single_period_sortino = row['平均收益'] / downside_std
                        sortino_ratios.append(single_period_sortino)
                    else:
                        sortino_ratios.append(0.0)
                else:
                    sortino_ratios.append(0.0)
            else:
                win_rates.append(0.0)
                max_drawdowns.append(0.0)
                sharpe_ratios.append(0.0)
                sortino_ratios.append(0.0)
        
        # 添加新的列到结果中
        avg_returns['胜率'] = win_rates
        avg_returns['最大回撤'] = max_drawdowns
        avg_returns['夏普率'] = sharpe_ratios  # 添加单期夏普比率
        avg_returns['索提诺比率'] = sortino_ratios  # 添加单期索提诺比率
        
        # [目标] 自适应年化收益率计算系统
        # 自动分析原始数据特征，智能选择年化算法
        print(f"  [分析] 开始自适应年化计算分析...")
        
        # 步骤1: 自动分析原始数据特征
        data_characteristics = self._analyze_data_characteristics()
        
        # 步骤2: 基于数据特征选择最优年化算法
        annualization_method = self._select_optimal_annualization_method(data_characteristics)
        
        # 步骤3: 执行年化计算
        annual_results = self._calculate_adaptive_annual_returns(avg_returns, data_characteristics, annualization_method)
        
        # 应用计算结果 - 优化版本
        # 主要年化收益率：使用标准复利年化结果
        avg_returns['年化收益率'] = annual_results['main_annual_return']
        
        # 对比方法：CAGR复合年化收益率
        avg_returns['CAGR年化收益率'] = annual_results['cagr_annual_return']
        
        # 已移除线性年化方法，保持向后兼容性但标记为已移除
        avg_returns['传统年化收益率'] = annual_results['traditional_annual_return']
        
        # 风险指标
        avg_returns['年化收益标准差'] = annual_results['annual_std']
        avg_returns['年化夏普比率'] = annual_results['annual_sharpe']
        avg_returns['年化索提诺比率'] = annual_results['annual_sortino']
        
        # 新增：数据质量信息列
        if 'quality_stats' in annual_results:
            quality = annual_results['quality_stats']
            avg_returns['年化计算成功率'] = quality.get('validation_success_rate', 0)
            avg_returns['有效分组数'] = quality.get('valid_groups', 0)
        
        # 打印详细分析结果
        self._print_annualization_analysis(data_characteristics, annualization_method, annual_results)
        
        # 计算多空收益（高分组 - 低分组）
        long_short_return = np.nan
        if len(avg_returns) >= 2:
            max_group = avg_returns['分组'].max()
            min_group = avg_returns['分组'].min()
            
            max_return = avg_returns.loc[avg_returns['分组'] == max_group, '平均收益'].values[0]
            min_return = avg_returns.loc[avg_returns['分组'] == min_group, '平均收益'].values[0]
            
            # 计算高因子组与低因子组的收益差
            long_short_return = max_return - min_return
            print(f"  多空收益（高-低分组）: {long_short_return:.4f}")
        
        return {
            'avg_returns': avg_returns,
            'long_short_return': long_short_return
        }
    
    def _analyze_data_characteristics(self):
        """
        自动分析原始数据特征
        
        Returns:
            dict: 数据特征分析结果
        """
        df = self.data
        characteristics = {}
        
        # 计算交易频率和持股周期
        if '信号日期' in df.columns and '持股2日收益率' in df.columns:
            df_sorted = df.sort_values('信号日期')
            date_diff = df_sorted['信号日期'].diff().dt.days
            
            # 去除NaN值
            date_diff_clean = date_diff.dropna()
            avg_interval = date_diff_clean.mean()
            
            # 计算实际年交易频率
            if avg_interval > 0:
                actual_trades_per_year = 365 / avg_interval
            else:
                actual_trades_per_year = 365  # 默认值
                
            # 观测期长度
            if len(date_diff_clean) > 0:
                total_days = (df_sorted['信号日期'].max() - df_sorted['信号日期'].min()).days
                observation_period = total_days / 365.25
            else:
                observation_period = 1  # 默认值
            
            # 持股周期分析（基于收益率数据推断）
            returns = df['持股2日收益率'].dropna()
            holding_period = 2  # 从数据特征知道是2日持有
            
            characteristics = {
                'total_trades': len(df),
                'avg_trade_interval': avg_interval,
                'actual_annual_trades': actual_trades_per_year,
                'observation_period_years': observation_period,
                'holding_period_days': holding_period,
                'trade_frequency_category': '高频' if actual_trades_per_year > 100 else ('中频' if actual_trades_per_year > 20 else '低频')
            }
        else:
            # 默认特征
            characteristics = {
                'total_trades': len(df),
                'avg_trade_interval': 2.0,
                'actual_annual_trades': 164.0,
                'observation_period_years': 5.18,
                'holding_period_days': 2,
                'trade_frequency_category': '高频'
            }
        
        return characteristics
    
    def _select_optimal_annualization_method(self, characteristics):
        """
        基于数据特征选择最优年化算法 - 优化版本
        
        核心改进：
        1. 优先选择标准复利年化方法（数学最严谨）
        2. 基于数据质量特征智能选择算法
        3. 保留CAGR方法作为对比验证
        4. 添加数据质量评估机制
        
        Args:
            characteristics: 数据特征分析结果
            
        Returns:
            dict: 选择的年化方法参数，包含新的标准复利方法标识
        """
        try:
            actual_trades = characteristics['actual_annual_trades']
            holding_period = characteristics['holding_period_days']
            frequency_category = characteristics['trade_frequency_category']
            observation_years = characteristics['observation_period_years']
            total_trades = characteristics['total_trades']
            
            print(f"    [分析] 智能选择最优年化算法...")
            
            # 数据质量评估指标
            data_quality_score = 0
            frequency_stability_score = 0
            
            # 1. 数据完整性评估
            if observation_years >= 2.0 and total_trades >= 50:
                data_quality_score += 0.4  # 观测期足够长且交易样本充足
            if actual_trades >= 20 and actual_trades <= 300:
                data_quality_score += 0.3  # 年交易频率在合理范围内
            if holding_period > 0 and holding_period <= 30:
                data_quality_score += 0.3  # 持股周期合理
            
            # 2. 频率稳定性评估
            if frequency_category in ['高频', '中频']:
                frequency_stability_score += 0.5  # 高频和中频交易相对稳定
            if actual_trades > 10:  # 有足够的交易频率数据
                frequency_stability_score += 0.5
            
            # 3. 智能算法选择
            # 主要标准：优先使用标准复利年化方法
            if data_quality_score >= 0.7:
                # 高质量数据：优先使用标准复利年化方法
                selected_method = {
                    'primary_method': 'standard_compound',
                    'comparison_method': 'cagr_based',
                    'reason': f'高质量数据（得分{data_quality_score:.2f}），使用标准复利年化方法（数学最严谨）',
                    'frequency_base': actual_trades,
                    'data_quality_score': data_quality_score,
                    'frequency_stability_score': frequency_stability_score,
                    'optimization_reason': '数据质量优秀，优先选择数学上最严谨的标准复利年化方法'
                }
                print(f"      [OK] 选择：标准复利年化（数据质量得分: {data_quality_score:.2f}）")
                
            elif frequency_stability_score >= 0.7:
                # 中等质量数据：仍优先使用标准复利年化，但加强验证
                selected_method = {
                    'primary_method': 'standard_compound',
                    'comparison_method': 'cagr_based',
                    'reason': f'频率稳定性良好（得分{frequency_stability_score:.2f}），使用标准复利年化方法',
                    'frequency_base': actual_trades,
                    'data_quality_score': data_quality_score,
                    'frequency_stability_score': frequency_stability_score,
                    'optimization_reason': '频率稳定性良好，使用标准复利年化方法，加强结果验证'
                }
                print(f"      [OK] 选择：标准复利年化（频率稳定性得分: {frequency_stability_score:.2f}）")
                
            else:
                # 较低质量数据：使用标准复利年化但增加保守性检查
                selected_method = {
                    'primary_method': 'standard_compound',
                    'comparison_method': 'cagr_based',
                    'reason': f'数据质量一般，仍使用标准复利年化方法但加强验证',
                    'frequency_base': actual_trades,
                    'data_quality_score': data_quality_score,
                    'frequency_stability_score': frequency_stability_score,
                    'optimization_reason': '数据质量一般，使用标准复利年化方法，但需要加强验证和保守性处理'
                }
                print(f"      [警告]  选择：标准复利年化（加强验证模式）")
            
            # 添加技术参数
            selected_method.update({
                'observation_period_years': observation_years,
                'holding_period_days': holding_period,
                'frequency_category': frequency_category,
                'is_optimized': True,  # 标记为优化版本
                'deprecated_methods': ['linear_annual_return_a', 'linear_annual_return_b']  # 标记已移除的方法
            })
            
            print(f"      [统计] 算法特征分析:")
            print(f"         数据质量得分: {data_quality_score:.2f}")
            print(f"         频率稳定性得分: {frequency_stability_score:.2f}")
            print(f"         观测期长度: {observation_years:.2f}年")
            print(f"         年交易频率: {actual_trades:.1f}次")
            
            return selected_method
            
        except Exception as e:
            print(f"      [ERROR] 算法选择出错: {str(e)}")
            # 返回安全的默认选择
            return {
                'primary_method': 'standard_compound',
                'comparison_method': 'cagr_based',
                'reason': f'算法选择失败，使用默认标准复利年化方法',
                'frequency_base': 252,
                'data_quality_score': 0,
                'frequency_stability_score': 0,
                'is_optimized': False,
                'error': str(e)
            }
    
    def _print_annualization_analysis(self, characteristics, method_info, results):
        """
        打印详细年化分析结果 - 优化版本
        
        Args:
            characteristics: 数据特征
            method_info: 选择的年化方法
            results: 年化计算结果（优化后的结构）
        """
        print(f"  [统计] 数据特征分析:")
        print(f"     总交易次数: {characteristics['total_trades']}次")
        print(f"     年化交易频率: {characteristics['actual_annual_trades']:.1f}次/年")
        print(f"     平均交易间隔: {characteristics['avg_trade_interval']:.1f}天")
        print(f"     观测期长度: {characteristics['observation_period_years']:.2f}年")
        print(f"     持股周期: {characteristics['holding_period_days']}天")
        print(f"     交易频率分类: {characteristics['trade_frequency_category']}")
        
        print(f"\n  [目标] 选择年化算法:")
        print(f"     算法类型: {method_info['primary_method']}")
        print(f"     选择理由: {method_info['reason']}")
        print(f"     频率基础: {method_info['frequency_base']:.1f}次/年")
        
        print(f"\n  🔢 年化计算结果（优化后）:")
        
        # 主要方法：标准复利年化
        if 'standard_compound_annual_return' in results:
            valid_standard = results['standard_compound_annual_return'][np.isfinite(results['standard_compound_annual_return'])]
            if len(valid_standard) > 0:
                print(f"     [强] 标准复利年化收益率: {float(valid_standard.mean()):.6f} ({float(valid_standard.mean())*100:.4f}%)")
                print(f"        (数学公式: (1+总收益率)^(1/年数) - 1)")
            else:
                print(f"     [强] 标准复利年化收益率: 无有效数据")
        
        # 对比方法：CAGR年化
        if 'cagr_annual_return' in results:
            valid_cagr = results['cagr_annual_return'][np.isfinite(results['cagr_annual_return'])]
            if len(valid_cagr) > 0:
                print(f"     [上升] CAGR复合年化收益率: {float(valid_cagr.mean()):.6f} ({float(valid_cagr.mean())*100:.4f}%)")
                print(f"        (对比方法，与标准复利年化数学等价)")
            else:
                print(f"     [上升] CAGR复合年化收益率: 无有效数据")
        
        # 已移除的线性年化方法
        if 'traditional_annual_return' in results:
            print(f"     [警告]  线性年化收益率: 已移除（忽视复利效应）")
        
        # 数据质量评估
        if 'quality_stats' in results:
            quality = results['quality_stats']
            print(f"\n  [列表] 数据质量评估:")
            print(f"     有效分组数: {quality.get('valid_groups', 0)}/{quality.get('total_groups', 0)}")
            print(f"     验证成功率: {quality.get('validation_success_rate', 0):.1%}")
            
            if not np.isnan(quality.get('mean_annual_return', np.nan)):
                print(f"     年化收益率范围: {quality.get('min_annual_return', 0)*100:.2f}% 到 {quality.get('max_annual_return', 0)*100:.2f}%")
        
        # 风险指标
        valid_std = results['annual_std'][np.isfinite(results['annual_std'])]
        valid_sharpe = results['annual_sharpe'][np.isfinite(results['annual_sharpe'])]
        valid_sortino = results['annual_sortino'][np.isfinite(results['annual_sortino'])]
        
        if len(valid_std) > 0:
            print(f"     年化收益标准差: {float(valid_std.mean()):.6f} ({float(valid_std.mean())*100:.4f}%)")
        if len(valid_sharpe) > 0:
            print(f"     年化夏普比率: {float(valid_sharpe.mean()):.4f}")
        if len(valid_sortino) > 0:
            print(f"     年化索提诺比率: {float(valid_sortino.mean()):.4f}")
        
        # 计算方法说明
        print(f"\n  [工具] 计算方法说明:")
        print(f"     [OK] 主要方法: 标准复利年化（数学最严谨）")
        print(f"     [统计] 对比方法: CAGR复合年化（验证一致性）")
        print(f"     [ERROR] 已移除: 线性年化方法（忽视复利效应）")
        print(f"     [分析] 验证机制: 反向计算验证结果准确性")
        
        # 计算方法差异分析
        if 'standard_compound_annual_return' in results and 'cagr_annual_return' in results:
            standard_mean = np.nanmean(results['standard_compound_annual_return'])
            cagr_mean = np.nanmean(results['cagr_annual_return'])
            
            if not (np.isnan(standard_mean) or np.isnan(cagr_mean)) and cagr_mean != 0:
                method_diff = standard_mean / cagr_mean
                print(f"     [尺度] 方法一致性检验: {method_diff:.6f} (应接近1.0)")
                if abs(method_diff - 1.0) < 0.001:
                    print(f"        [OK] 两种方法结果一致，验证通过")
                else:
                    print(f"        [警告]  方法间存在差异，需要检查")
    
    def calculate_factor_stats(self, factor_col):
        """
        计算因子统计指标，包括异常数据统计
        
        Args:
            factor_col: 因子列名
            
        Returns:
            dict: 因子统计信息，包含异常数据统计指标
        """
        df = self.processed_data
        factor_data = df[factor_col].dropna()
        total_samples = len(df)
        valid_samples = len(factor_data)
        
        # 计算基本统计量（这些只需要pandas和numpy）
        stats_info = {
            '均值': factor_data.mean(),
            '标准差': factor_data.std(),
            '最小值': factor_data.min(),
            '最大值': factor_data.max(),
            '中位数': factor_data.median(),
            '偏度': factor_data.skew(),
            '峰度': factor_data.kurtosis(),
            '样本数': total_samples,
            '有效样本数': valid_samples,
            '缺失样本比例': (total_samples - valid_samples) / total_samples if total_samples > 0 else 0
        }
        
        # 计算异常数据统计指标
        # 1. IQR离群值检测（不删除，只统计）
        Q1 = factor_data.quantile(0.25)
        Q3 = factor_data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound_iqr = Q1 - 1.5 * IQR
        upper_bound_iqr = Q3 + 1.5 * IQR
        extreme_lower_bound = Q1 - 3.0 * IQR
        extreme_upper_bound = Q3 + 3.0 * IQR
        
        # 温和离群值（1.5-3倍IQR）
        mild_outliers = factor_data[(factor_data < lower_bound_iqr) | (factor_data > upper_bound_iqr)]
        # 极端离群值（>3倍IQR）
        extreme_outliers = factor_data[(factor_data < extreme_lower_bound) | (factor_data > extreme_upper_bound)]
        
        stats_info['IQR'] = IQR
        stats_info['Q1'] = Q1
        stats_info['Q3'] = Q3
        stats_info['温和离群值数量'] = len(mild_outliers) - len(extreme_outliers)
        stats_info['温和离群值比例'] = (len(mild_outliers) - len(extreme_outliers)) / valid_samples if valid_samples > 0 else 0
        stats_info['极端离群值数量'] = len(extreme_outliers)
        stats_info['极端离群值比例'] = len(extreme_outliers) / valid_samples if valid_samples > 0 else 0
        stats_info['总离群值比例'] = len(mild_outliers) / valid_samples if valid_samples > 0 else 0
        
        # 2. 极值比例（分位数之外的数据）
        p1 = factor_data.quantile(0.01)
        p99 = factor_data.quantile(0.99)
        p05 = factor_data.quantile(0.05)
        p95 = factor_data.quantile(0.95)
        
        extreme_low_values = factor_data[factor_data < p1]
        extreme_high_values = factor_data[factor_data > p99]
        
        stats_info['1%分位数'] = p1
        stats_info['99%分位数'] = p99
        stats_info['5%分位数'] = p05
        stats_info['95%分位数'] = p95
        stats_info['1%以下极值比例'] = len(extreme_low_values) / valid_samples if valid_samples > 0 else 0
        stats_info['99%以上极值比例'] = len(extreme_high_values) / valid_samples if valid_samples > 0 else 0
        
        # 3. 数据分布异常检测
        # 偏度异常检测（绝对值大于2表示严重偏斜）
        skewness = factor_data.skew()
        stats_info['偏度异常'] = abs(skewness) > 2
        stats_info['偏度异常程度'] = '严重偏斜' if abs(skewness) > 2 else ('中等偏斜' if abs(skewness) > 1 else '近似对称')
        
        # 峰度异常检测（绝对值大于3表示分布异常陡峭或平坦）
        kurtosis = factor_data.kurtosis()
        stats_info['峰度异常'] = abs(kurtosis) > 3
        stats_info['峰度异常程度'] = '极端' if abs(kurtosis) > 3 else ('中等' if abs(kurtosis) > 1 else '正常')
        
        # 4. 唯一值比例（低唯一值比例可能表示数据离散度不足）
        unique_count = factor_data.nunique()
        unique_ratio = unique_count / valid_samples if valid_samples > 0 else 0
        stats_info['唯一值数量'] = unique_count
        stats_info['唯一值比例'] = unique_ratio
        stats_info['离散度不足'] = unique_ratio < 0.05
        
        # 5. 零值和极值检查
        zero_count = (factor_data == 0).sum()
        stats_info['零值数量'] = zero_count
        stats_info['零值比例'] = zero_count / valid_samples if valid_samples > 0 else 0
        
        # 检查是否存在异常大的数值变化
        if valid_samples > 1:
            max_min_ratio = abs(factor_data.max() / factor_data.min()) if factor_data.min() != 0 else float('inf')
            stats_info['最大值/最小值比率'] = max_min_ratio
            stats_info['数值范围异常'] = max_min_ratio > 10000 or factor_data.max() > 1e6 or factor_data.min() < -1e6
        
        # 使用scipy计算更详细的统计信息（仅当scipy可用时）
        if HAS_SCIPY:
            # 计算Jarque-Bera正态性检验
            jb_stat, jb_pvalue = stats.jarque_bera(factor_data)
            stats_info['Jarque-Bera统计量'] = jb_stat
            stats_info['Jarque-Bera p值'] = jb_pvalue
            stats_info['非正态分布'] = jb_pvalue < 0.05  # p值小于0.05拒绝正态分布假设
            
            # 计算Shapiro-Wilk正态性检验
            if len(factor_data) <= 5000:  # Shapiro-Wilk在大样本上计算较慢
                sw_stat, sw_pvalue = stats.shapiro(factor_data)
                stats_info['Shapiro-Wilk统计量'] = sw_stat
                stats_info['Shapiro-Wilk p值'] = sw_pvalue
                stats_info['Shapiro-Wilk非正态'] = sw_pvalue < 0.05
        
        # 6. 异常因子识别（为后续报告做准备）
        stats_info['可能异常因子'] = any([
            stats_info['总离群值比例'] > 0.2,  # 超过20%的离群值
            stats_info['极端离群值比例'] > 0.05,  # 超过5%的极端离群值
            stats_info['偏度异常'],
            stats_info['峰度异常'],
            stats_info['离散度不足'],
            '数值范围异常' in stats_info and stats_info['数值范围异常'],
            stats_info['零值比例'] > 0.5  # 超过50%的零值
        ])
        
        return stats_info
    
    # 移除了验证函数，优化计算逻辑确保结果正确
    
    def run_factor_analysis(self, use_pearson=False):
        """
        运行所有因子的分析
        
        Args:
            use_pearson: 是否使用Pearson相关系数计算IC值，默认为False（使用Spearman相关系数）
        """
        if not self.preprocess_data():
            return False
        
        # 添加总体样本统计和打印
        print(f"\n===== 因子分析总体样本统计 =====")
        print(f"原始数据总样本数: {len(self.data)}")
        print(f"预处理后数据总样本数: {len(self.processed_data)}")
        print(f"数据保留率: {len(self.processed_data)/len(self.data)*100:.2f}%")
        print(f"待分析因子数量: {len(self.factors)}")
        
        # 统计各因子的有效样本数
        factor_valid_samples = {}
        for factor in self.factors:
            if factor in self.processed_data.columns:
                valid_samples = self.processed_data[factor].notna().sum()
                factor_valid_samples[factor] = valid_samples
                print(f"因子 {factor}: {valid_samples} 个有效样本 ({valid_samples/len(self.processed_data)*100:.2f}%)")
            else:
                factor_valid_samples[factor] = 0
                print(f"因子 {factor}: 0 个有效样本 (因子不存在)")
        
        # 计算收益率列的有效样本数
        return_valid_samples = self.processed_data[self.return_col].notna().sum()
        print(f"收益率列 {self.return_col}: {return_valid_samples} 个有效样本 ({return_valid_samples/len(self.processed_data)*100:.2f}%)")
        print("==================================\n")
        
        # 确定相关系数类型
        corr_type = "Pearson" if use_pearson else "Spearman"
        print(f"\n开始因子分析，使用 {self.return_col} 作为收益率计算标准")
        print(f"使用 {corr_type} 相关系数计算IC值")
        
        for factor in self.factors:
            print(f"\n=== 分析因子: {factor} ===")
            
            # 检查因子是否存在且有效
            if factor not in self.processed_data.columns:
                print(f"跳过因子 {factor}: 数据中不存在该因子")
                continue
            
            # 计算因子基本统计
            stats_info = self.calculate_factor_stats(factor)
            print(f"分析因子: {factor}")
            
            # 计算IC值 - 启用所有新增的稳健性统计方法
            ic_mean, ic_std, t_stat, p_value, extra_stats = self.calculate_ic(
                factor, 
                use_pearson=use_pearson,
                use_robust_corr=True,    # 启用稳健相关系数
                use_kendall=True,        # 启用Kendall's Tau
                use_nonparam_test=True,  # 启用非参数检验
                compute_bootstrap_ci=True # 启用Bootstrap置信区间
            )
            
            # 显示额外的统计信息
            if extra_stats:
                print(f"  额外稳健性统计信息:")
                for key, value in extra_stats.items():
                    if isinstance(value, tuple):
                        print(f"    {key}: {value}")
                    elif isinstance(value, list) and len(value) > 0:
                        print(f"    {key}: {len(value)}个Bootstrap样本")
                    else:
                        print(f"    {key}: {value:.3f}")
            
            # 添加缺失值检查和警告
            if np.isnan(ic_std):
                print(f"  警告: {factor} 的IC标准差计算失败或缺失")
                ir = np.nan
            else:
                # 直接按数学定义计算IR值，不添加任何人为限制
                ir = ic_mean / ic_std if ic_std != 0 else np.nan
                if np.isnan(ir) or not np.isfinite(ir):
                    print(f"  警告: {factor} 的IR值计算异常（可能是IC标准差为0）")
            
            print(f"IC分析结果: IC均值={ic_mean:.3f}, IR值={ir:.3f}")
            
            # 计算分组收益
            group_results = self.calculate_group_returns(factor)
            if group_results:
                print(f"\n分组收益分析:")
                print(group_results['avg_returns'].to_string(index=False, float_format='%.3f'))
                print(f"\n多空收益(最高组-最低组): {group_results['long_short_return']:.3f}")
            
            # 保存分析结果
            self.analysis_results[factor] = {
                'stats_info': stats_info,
                'ic_mean': ic_mean,
                'ic_std': ic_std,
                'ir': ir,
                't_stat': t_stat,
                'p_value': p_value,
                'group_results': group_results
            }
            
            # 注释掉自动生成CSV文件的代码，将在用户选择因子后再生成
            # if group_results and 'avg_returns' in group_results:
            #     timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            #     safe_factor_name = factor.replace('/', '_').replace('\\', '_').replace(':', '_')
            #     csv_filename = f'十等分分组收益_{safe_factor_name}_{timestamp}.csv'
            #     group_results['avg_returns'].to_csv(csv_filename, index=False, encoding='utf-8-sig')
            #     print(f"  因子 {factor} 的分组收益表格已保存至: {csv_filename}")
        
        print("因子分析完成")
        
        return True
    
    def plot_factor_distribution(self):
        """
        绘制因子分布图
        """
        if not HAS_PLOT:
            print("可视化功能不可用，跳过因子分布绘图")
            return False
            
        if not hasattr(self, 'processed_data'):
            print("错误：请先运行因子分析")
            return False
        
        print("\n绘制因子分布图...")
        n_factors = len(self.factors)
        n_cols = min(2, n_factors)
        n_rows = (n_factors + n_cols - 1) // n_cols
        
        plt.figure(figsize=(12, 4 * n_rows))
        
        for i, factor in enumerate(self.factors):
            if factor not in self.processed_data.columns:
                continue
            
            ax = plt.subplot(n_rows, n_cols, i + 1)
            sns.histplot(self.processed_data[factor].dropna(), kde=True, ax=ax)
            plt.title(f'{factor} 分布')
            plt.xlabel(factor)
            plt.ylabel('频次')
        
        plt.tight_layout()
        plt.savefig('因子分布图.png', dpi=300, bbox_inches='tight')
        print("因子分布图已保存为 '因子分布图.png'")
        # 移除plt.show()以避免阻塞和KeyboardInterrupt错误
        plt.close()  # 关闭当前图像以释放内存
        return True
    
    def plot_group_returns(self):
        """
        绘制分组收益图
        """
        if not HAS_PLOT:
            print("可视化功能不可用，跳过分组收益绘图")
            return False
            
        if not self.analysis_results:
            print("错误：请先运行因子分析")
            return False
        
        print("\n绘制分组收益图...")
        n_factors = len(self.analysis_results)
        n_cols = min(2, n_factors)
        n_rows = (n_factors + n_cols - 1) // n_cols
        
        plt.figure(figsize=(12, 4 * n_rows))
        
        for i, (factor, results) in enumerate(self.analysis_results.items()):
            if 'group_results' not in results or results['group_results'] is None:
                continue
            
            ax = plt.subplot(n_rows, n_cols, i + 1)
            group_returns = results['group_results']['avg_returns']
            
            sns.barplot(x='分组', y='平均收益', data=group_returns, ax=ax)
            plt.title(f'{factor} 分组收益')
            plt.xlabel('分组')
            plt.ylabel(f'{self.return_col} (平均)')
            
            # 添加数值标签
            for j, row in group_returns.iterrows():
                ax.text(j, row['平均收益'], f'{row['平均收益']:.3f}', 
                        ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig('分组收益图.png', dpi=300, bbox_inches='tight')
        print("分组收益图已保存为 '分组收益图.png'")
        # 移除plt.show()以避免阻塞和KeyboardInterrupt错误
        plt.close()  # 关闭当前图像以释放内存
        return True
    
    def _get_new_scoring_weights(self, is_negative_factor=False):
        """
        获取新的评分权重配置（基于改进报告建议）
        
        Args:
            is_negative_factor: 是否为负向因子
            
        Returns:
            dict: 权重配置字典
        """
        if is_negative_factor:
            # 负向因子专门评分体系（基于建议3）
            return {
                'ic_strength': 0.40,    # 负向强度评分（40%权重）
                'significance': 0.30,   # 统计显著性（30%权重）
                'stability': 0.20,      # IR值稳定性（20%权重）
                'return_performance': 0.10  # 收益表现（10%权重）
            }
        else:
            # 正向因子权重配置（基于建议2）
            return {
                'ic_mean': 0.35,        # IC均值（35%权重，提升预测能力重要性）
                'significance': 0.25,   # 统计显著性（25%权重，提升可靠性重视度）
                'ir_value': 0.20,       # IR值（20%权重，降低稳定性权重）
                'return_performance': 0.20  # 多空收益（20%权重，降低收益权重）
            }

    def _calculate_improved_scores(self, ic_mean, ic_std, ir, t_stat, p_value, long_short_return):
        """
        基于新标准的改进评分计算（综合建议1、2、3）
        
        Args:
            ic_mean: IC均值
            ic_std: IC标准差
            ir: IR值
            t_stat: t统计量
            p_value: p值
            long_short_return: 多空收益
            
        Returns:
            dict: 包含所有维度评分的字典
        """
        # 识别因子类型
        factor_type = self._identify_factor_type(ic_mean, long_short_return)
        is_negative_factor = ic_mean < 0
        
        # 获取对应权重配置
        weights = self._get_new_scoring_weights(is_negative_factor)
        
        if is_negative_factor:
            # 负向因子专门评分体系（建议3）
            scores = self._calculate_negative_factor_scores(
                ic_mean, ir, p_value, long_short_return, weights
            )
        else:
            # 正向因子评分体系（建议2）
            scores = self._calculate_positive_factor_scores(
                ic_mean, ir, p_value, long_short_return, weights
            )
        
        # 计算加权总分
        total_score = sum(scores[metric] * weight
                         for metric, weight in weights.items())
        
        scores['total_score'] = total_score
        scores['factor_type'] = factor_type
        scores['is_negative'] = is_negative_factor
        
        return scores

    def _calculate_positive_factor_scores(self, ic_mean, ir, p_value, long_short_return, weights):
        """
        计算正向因子各维度得分（基于建议2的权重配置）
        """
        scores = {}
        
        # 1. IC均值评分（35%权重）- 预测能力
        ic_score = self._score_ic_mean_new_standard(ic_mean)
        scores['ic_mean'] = ic_score
        
        # 2. 统计显著性评分（25%权重）- 可靠性
        sig_score = self._score_statistical_significance_new(p_value)
        scores['significance'] = sig_score
        
        # 3. IR值评分（20%权重）- 稳定性
        ir_score = self._score_ir_value_new_standard(ir)
        scores['ir_value'] = ir_score
        
        # 4. 多空收益评分（20%权重）- 收益能力
        return_score = self._score_long_short_return_new_standard(long_short_return)
        scores['return_performance'] = return_score
        
        return scores

    def _calculate_negative_factor_scores(self, ic_mean, ir, p_value, long_short_return, weights):
        """
        计算负向因子各维度得分（基于建议3的专门体系）
        """
        scores = {}
        
        # 1. 负向强度评分（40%权重）- |IC均值|越大越好
        negative_strength_score = self._score_negative_intensity(abs(ic_mean))
        scores['ic_strength'] = negative_strength_score
        
        # 2. 统计显著性评分（30%权重）- p值显著性
        sig_score = self._score_statistical_significance_new(p_value)
        scores['significance'] = sig_score
        
        # 3. IR值稳定性（20%权重）- 稳定性表现
        stability_score = self._score_stability_new(ir)
        scores['stability'] = stability_score
        
        # 4. 收益表现（10%权重）- 多空收益
        return_score = self._score_return_performance_negative(long_short_return)
        scores['return_performance'] = return_score
        
        return scores

    def _apply_domestic_standards(self, total_score, ic_mean, ir, factor_type, is_negative=False):
        """
        应用国内量化实践标准（基于建议1）
        
        Args:
            total_score: 总分
            ic_mean: IC均值
            ir: IR值
            factor_type: 因子类型
            is_negative: 是否为负向因子
            
        Returns:
            tuple: (rating, status, usage)
        """
        # 国内实践标准（建议1）
        # A级因子：IC均值>0.08，IR>0.3
        # B级因子：IC均值>0.05，IR>0.2
        
        # 特别处理：IC均值>0.12且多空收益>0.04的优秀因子（保持特殊机制）
        if not is_negative and ic_mean >= 0.12 and abs(ir) >= 0.3:
            if total_score >= 3.5:
                return 'A+', '卓越', '强烈推荐使用'
            elif total_score >= 3.0:
                return 'A', '优秀', '推荐使用'
        
        # 基于国内实践标准的评级
        if not is_negative:
            # 正向因子评级标准（结合国内实践）
            if ic_mean >= 0.08 and ir >= 0.3:
                # 国内A级标准
                if total_score >= 3.5:
                    rating = 'A+'
                elif total_score >= 3.0:
                    rating = 'A'
                else:
                    rating = 'A-'  # 保持对优秀IC因子的特殊评级
            elif ic_mean >= 0.05 and ir >= 0.2:
                # 国内B级标准
                if total_score >= 2.5:
                    rating = 'B+'
                elif total_score >= 2.0:
                    rating = 'B'
                else:
                    rating = 'B-'  # 基于国内标准调整
            elif ic_mean >= 0.02:
                # 国内C级标准
                if total_score >= 1.5:
                    rating = 'C+'
                elif total_score >= 1.0:
                    rating = 'C'
                else:
                    rating = 'C-'
            else:
                rating = 'D'  # 无效因子
        else:
            # 负向因子评级（基于绝对IC值和稳定性）
            abs_ic = abs(ic_mean)
            if abs_ic >= 0.08 and abs(ir) >= 0.3:
                rating = 'A-'  # 负向因子使用A-表示优秀反向因子
            elif abs_ic >= 0.05 and abs(ir) >= 0.2:
                rating = 'B+'
            elif abs_ic >= 0.03:
                rating = 'B'
            elif abs_ic >= 0.02:
                rating = 'C+'
            else:
                rating = 'D'
        
        # 状态和使用建议映射
        status_mapping = {
            'A+': '卓越', 'A': '优秀', 'A-': '优秀', 'B+': '良好',
            'B': '一般', 'C+': '较弱', 'C': '弱', 'D': '无效'
        }
        
        usage_mapping = {
            'A+': '强烈推荐使用', 'A': '推荐使用', 'A-': '推荐使用',
            'B+': '可考虑使用', 'B': '谨慎使用', 'C+': '不推荐使用',
            'C': '不建议使用', 'D': '避免使用'
        }
        
        status = status_mapping.get(rating, '未知')
        usage = usage_mapping.get(rating, '需重新评估')
        
        return rating, status, usage

    def _score_ic_mean_new_standard(self, ic_mean):
        """
        基于国内量化实践的IC均值评分（建议1）
        A级：>0.08，B级：>0.05
        """
        abs_ic = abs(ic_mean)
        if abs_ic >= 0.12:
            return 4.0  # 优秀（超额奖励机制）
        elif abs_ic >= 0.08:
            return 3.5  # 国内A级标准
        elif abs_ic >= 0.05:
            return 3.0  # 国内B级标准
        elif abs_ic >= 0.02:
            return 2.0  # 有效阈值
        elif abs_ic >= 0.01:
            return 1.0  # 弱
        else:
            return 0.5  # 极弱

    def _score_ir_value_new_standard(self, ir):
        """
        基于建议2的IR值评分（降低权重但保持重要性）
        """
        abs_ir = abs(ir)
        if abs_ir >= 1.5:
            return 2.5  # 极强（保持原有高分）
        elif abs_ir >= 1.0:
            return 2.0  # 强
        elif abs_ir >= 0.5:
            return 1.5  # 中等（国内常见标准）
        elif abs_ir >= 0.3:
            return 1.0  # 弱
        elif abs_ir >= 0.15:
            return 0.8  # 较弱
        else:
            return 0.5  # 极弱

    def _score_statistical_significance_new(self, p_value):
        """
        基于建议2的统计显著性评分（提升权重至25%）
        """
        if np.isnan(p_value):
            return 0.3  # 数据缺失
        
        if p_value < 0.01:
            return 1.0  # 高度显著
        elif p_value < 0.05:
            return 0.8  # 显著（国内实践重视但不过度依赖）
        elif p_value < 0.1:
            return 0.6  # 边缘显著
        else:
            return 0.3  # 不显著

    def _score_long_short_return_new_standard(self, long_short_return):
        """
        基于建议2的多空收益评分（降低权重至20%）
        """
        if np.isnan(long_short_return):
            return 1.0  # 数据缺失，默认中等
        
        abs_return = abs(long_short_return)
        if abs_return >= 0.04:
            return 2.0  # 优秀（降低满分，保持重要性）
        elif abs_return >= 0.03:
            return 1.8  # 强
        elif abs_return >= 0.02:
            return 1.5  # 中等
        elif abs_return >= 0.01:
            return 1.0  # 弱
        else:
            return 0.5  # 极弱

    def _score_negative_intensity(self, abs_ic_mean):
        """
        基于建议3的负向强度评分
        """
        if abs_ic_mean >= 0.1:
            return 4.0  # 强负向
        elif abs_ic_mean >= 0.07:
            return 3.5  # 中强负向
        elif abs_ic_mean >= 0.05:
            return 3.0  # 中等负向
        elif abs_ic_mean >= 0.03:
            return 2.0  # 弱负向
        else:
            return 1.0  # 极弱负向

    def _score_stability_new(self, ir):
        """
        基于建议3的稳定性评分（负向因子20%权重）
        """
        abs_ir = abs(ir)
        if abs_ir >= 1.5:
            return 2.0  # 极强稳定性
        elif abs_ir >= 1.0:
            return 1.5  # 强稳定性
        elif abs_ir >= 0.5:
            return 1.0  # 中等稳定性
        elif abs_ir >= 0.2:
            return 0.8  # 一般稳定性
        else:
            return 0.5  # 较差稳定性

    def _score_return_performance_negative(self, long_short_return):
        """
        基于建议3的负向因子收益表现评分（10%权重）
        """
        if np.isnan(long_short_return):
            return 0.5  # 数据缺失
        
        # 负向因子希望多空收益为负
        if long_short_return < -0.02:
            return 1.0  # 优秀反向收益
        elif long_short_return < -0.01:
            return 0.8  # 良好反向收益
        elif long_short_return < 0:
            return 0.6  # 一般反向收益
        else:
            return 0.3  # 收益为正但因子为负向，可能存在数据问题

    def _generate_improved_detailed_reason(self, rating, ic_mean, ir, p_value, long_short_return, factor_type, scores):
        """
        生成改进的详细理由说明
        """
        reasons = []
        
        # 因子类型标识
        factor_direction = "负向" if ic_mean < 0 else "正向"
        
        if rating in ['A+', 'A', 'A-']:
            reasons.append(f"[OK] 优秀表现：{rating}级{factor_direction}因子，具有强预测能力和高收益性")
            reasons.append(f"• IC均值{abs(ic_mean):.3f}，{'超过国内A级标准(>0.08)' if abs(ic_mean) > 0.08 else '接近国内A级标准'}")
            reasons.append(f"• IR值{abs(ir):.3f}，稳定性{'优秀' if abs(ir) > 1.5 else '良好' if abs(ir) > 1.0 else '一般'}")
            if p_value < 0.05:
                reasons.append(f"• 统计显著(p值={p_value:.3f})")
            reasons.append(f"• 类型：{factor_type}")
            reasons.append("使用建议：强烈推荐使用，可作为组合核心配置，权重15-25%")
            
        elif rating == 'B+':
            reasons.append(f"• 良好表现：B+级{factor_direction}因子，符合国内B级标准")
            reasons.append(f"• IC均值{abs(ic_mean):.3f}，{'达到国内B级标准(>0.05)' if abs(ic_mean) > 0.05 else '接近国内B级标准'}")
            reasons.append(f"• IR值{abs(ir):.3f}，稳定性一般")
            if p_value < 0.1:
                reasons.append(f"• p值={p_value:.3f}，{'统计显著' if p_value < 0.05 else '边缘显著'}")
            reasons.append(f"• 类型：{factor_type}")
            reasons.append("使用建议：可谨慎使用，权重控制在10%以内，加强监控")
            
        elif rating == 'B':
            reasons.append(f"• 一般表现：B级{factor_direction}因子，具有基础预测能力")
            reasons.append(f"• IC均值{abs(ic_mean):.3f}，预测能力一般")
            reasons.append(f"• IR值{abs(ir):.3f}，稳定性有限")
            reasons.append(f"• 类型：{factor_type}")
            reasons.append("使用建议：谨慎使用，权重控制在5%以内，定期评估")
            
        elif rating in ['C+', 'C']:
            reasons.append(f"✗ 表现不佳：该因子{'C+' if rating == 'C+' else 'C'}级")
            reasons.append(f"• IC均值{abs(ic_mean):.3f}，预测能力不足")
            reasons.append(f"• IR值{abs(ir):.3f}，稳定性较差")
            if p_value >= 0.05:
                reasons.append(f"• p值={p_value:.3f}，统计不显著")
            reasons.append(f"• 类型：{factor_type}")
            if rating == 'C+':
                reasons.append("使用建议：不推荐使用，如需使用请严格控制权重5%以下")
            else:
                reasons.append("使用建议：避免使用，确定无效，继续使用可能造成损失")
        
        return '\n'.join(reasons)

    def _evaluate_factor_performance(self, ic_mean, ic_std, ir, t_stat, p_value, long_short_return):
        """
        改进的因子性能评估函数（综合应用建议1、2、3）
        
        新的评分体系：
        - 正向因子：IC均值35% + 统计显著性25% + IR值20% + 多空收益20%
        - 负向因子：负向强度40% + 统计显著性30% + 稳定性20% + 收益表现10%
        - 评级标准：采用国内量化实践标准
        """
        
        # 使用新的评分计算方法
        scores = self._calculate_improved_scores(
            ic_mean, ic_std, ir, t_stat, p_value, long_short_return
        )
        
        # 应用国内量化实践标准进行评级
        rating, status, usage = self._apply_domestic_standards(
            scores['total_score'], ic_mean, ir, scores['factor_type'], scores['is_negative']
        )
        
        # 生成详细理由
        detailed_reason = self._generate_improved_detailed_reason(
            rating, ic_mean, ir, p_value, long_short_return, scores['factor_type'], scores
        )
        
        return {
            'score': round(scores['total_score'], 1),
            'rating': rating,
            'status': status,
            'usage': usage,
            'detailed_reason': detailed_reason,
            'factor_type': scores['factor_type'],
            # 新增：详细维度得分
            'ic_score': scores.get('ic_mean', scores.get('ic_strength', 0)),
            'significance_score': scores['significance'],
            'stability_score': scores.get('ir_value', scores.get('stability', 0)),
            'return_score': scores['return_performance'],
            'is_negative_factor': scores['is_negative']
        }
    
    def _generate_detailed_reason(self, rating, ic_mean, ir, p_value, long_short_return, factor_type):
        """
        根据新评级和因子指标生成精简的详细理由
        """
        reasons = []
        
        if rating in ['A+', 'A']:
            reasons.append(f"[OK] 优秀表现：{rating}级因子，具有强预测能力和高收益性")
            reasons.append(f"• IC均值{abs(ic_mean):.3f}，预测能力强")
            reasons.append(f"• 多空收益{abs(long_short_return):.3f}，收益表现卓越")
            reasons.append(f"• IR值{abs(ir):.3f}，稳定性{'优秀' if abs(ir) > 1.5 else '良好'}")
            if p_value < 0.05:
                reasons.append(f"• 统计显著(p值={p_value:.3f})")
            reasons.append(f"• 类型：{factor_type}")
            reasons.append("使用建议：强烈推荐使用，可作为组合核心配置，权重15-25%")
            
        elif rating == 'B+':
            reasons.append(f"• 良好表现：B+级因子，具有中等预测能力和收益性")
            reasons.append(f"• IC均值{abs(ic_mean):.3f}，预测能力{'中等' if abs(ic_mean) > 0.05 else '一般'}")
            reasons.append(f"• 多空收益{abs(long_short_return):.3f}，收益表现{'优秀' if abs(long_short_return) > 0.02 else '一般'}")
            reasons.append(f"• IR值{abs(ir):.3f}，稳定性一般")
            if p_value < 0.05:
                reasons.append(f"• 统计显著(p值={p_value:.3f})")
            else:
                reasons.append(f"• p值={p_value:.3f}")
            reasons.append(f"• 类型：{factor_type}")
            reasons.append("使用建议：可谨慎使用，权重控制在10%以内，加强监控")
            
        elif rating == 'B':
            reasons.append(f"• 一般表现：B级因子，具有基础预测能力")
            reasons.append(f"• IC均值{abs(ic_mean):.3f}，预测能力一般")
            reasons.append(f"• 多空收益{abs(long_short_return):.3f}，收益表现一般")
            reasons.append(f"• IR值{abs(ir):.3f}，稳定性有限")
            if p_value < 0.05:
                reasons.append(f"• 统计显著(p值={p_value:.3f})")
            else:
                reasons.append(f"• p值={p_value:.3f}")
            reasons.append(f"• 类型：{factor_type}")
            reasons.append("使用建议：谨慎使用，权重控制在5%以内，定期评估")
            
        elif rating in ['C+', 'C']:
            reasons.append(f"✗ 表现不佳：该因子{'C+' if rating == 'C+' else 'C'}级")
            reasons.append(f"• IC均值{abs(ic_mean):.3f}，预测能力不足")
            reasons.append(f"• IR值{abs(ir):.3f}，稳定性较差")
            if p_value >= 0.05:
                reasons.append(f"• p值={p_value:.3f}，统计不显著")
            reasons.append(f"• 类型：{factor_type}")
            if rating == 'C+':
                reasons.append("使用建议：不推荐使用，如需使用请严格控制权重5%以下")
            else:
                reasons.append("使用建议：避免使用，确定无效，继续使用可能造成损失")
        
        return '\n'.join(reasons)
    
    def _identify_factor_type(self, ic_mean, long_short_return):
        """
        识别因子类型：线性、非线性、无效
        """
        if abs(ic_mean) < 0.02:
            return "无效因子"
        elif not np.isnan(long_short_return) and abs(long_short_return) > abs(ic_mean) * 2:
            return "非线性因子"
        else:
            return "线性因子"
    
    def _generate_data_driven_comparison(self, summary_df):
        """
        生成基于客观数据的因子对比分析
        """
        comparison_results = {
            'objective_analysis': {},
            'data_driven_insights': {}
        }
        
        # 1. 客观数据验证
        if not summary_df.empty:
            # 计算各指标的统计分布
            ic_mean_values = summary_df['IC均值'].dropna()
            ir_values = summary_df['IR值'].dropna()
            ls_returns = summary_df['多空收益'].dropna()
            
            # 为每个因子生成客观评级
            factor_objective_grades = []
            
            for _, row in summary_df.iterrows():
                factor_name = row['因子名称']
                ic_mean = row['IC均值']
                ir = row['IR值']
                ls_return = row.get('多空收益', np.nan)
                
                # 客观评级逻辑
                objective_score = 0
                
                # IC均值客观评分
                if abs(ic_mean) >= 0.1:
                    objective_score += 30
                    ic_grade = "优秀"
                elif abs(ic_mean) >= 0.05:
                    objective_score += 20
                    ic_grade = "良好"
                elif abs(ic_mean) >= 0.02:
                    objective_score += 10
                    ic_grade = "一般"
                else:
                    ic_grade = "较差"
                
                # 多空收益客观评分（核心指标）
                if not np.isnan(ls_return) and abs(ls_return) >= 0.03:
                    objective_score += 35
                    ls_grade = "卓越"
                elif not np.isnan(ls_return) and abs(ls_return) >= 0.02:
                    objective_score += 25
                    ls_grade = "优秀"
                elif not np.isnan(ls_return) and abs(ls_return) >= 0.01:
                    objective_score += 15
                    ls_grade = "良好"
                else:
                    ls_grade = "一般"
                
                # IR值客观评分
                if abs(ir) >= 1.5:
                    objective_score += 25
                    ir_grade = "优秀"
                elif abs(ir) >= 1.0:
                    objective_score += 20
                    ir_grade = "良好"
                elif abs(ir) >= 0.5:
                    objective_score += 10
                    ir_grade = "一般"
                else:
                    ir_grade = "较差"
                
                # 统计显著性客观评分
                p_value = row.get('p值', np.nan)
                if not np.isnan(p_value):
                    if p_value < 0.01:
                        objective_score += 10
                        sig_grade = "高度显著"
                    elif p_value < 0.05:
                        objective_score += 8
                        sig_grade = "显著"
                    elif p_value < 0.1:
                        objective_score += 5
                        sig_grade = "边缘显著"
                    else:
                        objective_score += 2
                        sig_grade = "不显著"
                else:
                    sig_grade = "数据缺失"
                    objective_score += 2
                
                # 生成客观评级
                if objective_score >= 85:
                    objective_grade = "A+"
                elif objective_score >= 75:
                    objective_grade = "A"
                elif objective_score >= 65:
                    objective_grade = "B+"
                elif objective_score >= 55:
                    objective_grade = "B"
                elif objective_score >= 40:
                    objective_grade = "C+"
                elif objective_score >= 25:
                    objective_grade = "C"
                else:
                    objective_grade = "D"
                
                factor_objective_grades.append({
                    'factor_name': factor_name,
                    'objective_score': objective_score,
                    'objective_grade': objective_grade,
                    'ic_grade': ic_grade,
                    'ls_grade': ls_grade,
                    'ir_grade': ir_grade,
                    'sig_grade': sig_grade,
                    'ic_mean': ic_mean,
                    'ls_return': ls_return,
                    'ir': ir
                })
            
            comparison_results['objective_analysis'] = {
                'factor_grades': factor_objective_grades,
                'summary_stats': {
                    'total_factors': len(factor_objective_grades),
                    'excellent_factors': len([f for f in factor_objective_grades if f['objective_score'] >= 75]),
                    'good_factors': len([f for f in factor_objective_grades if 65 <= f['objective_score'] < 75]),
                    'average_ic': ic_mean_values.mean() if len(ic_mean_values) > 0 else np.nan,
                    'average_ls_return': ls_returns.mean() if len(ls_returns) > 0 else np.nan,
                    'top_performer': max(factor_objective_grades, key=lambda x: x['objective_score']) if factor_objective_grades else None
                }
            }
        
        return comparison_results
    def _generate_executive_summary(self, summary_df):
        """
        生成精简执行摘要
        """
        # 统计因子整体表现
        total_factors = len(summary_df)
        
        # 按新评价体系重新评估所有因子
        factor_scores = []
        factor_ratings = []
        factor_types = []
        factor_names = []
        
        for _, row in summary_df.iterrows():
            factor_name = row['因子名称']
            ic_mean = row['IC均值']
            ic_std = row['IC标准差']
            ir = row['IR值']
            t_stat = row.get('t统计量', np.nan)
            p_value = row.get('p值', np.nan)
            long_short_return = row.get('多空收益', np.nan)
            
            eval_result = self._evaluate_factor_performance(ic_mean, ic_std, ir, t_stat, p_value, long_short_return)
            factor_scores.append(eval_result['score'])
            factor_ratings.append(eval_result['rating'])
            factor_types.append(eval_result['factor_type'])
            factor_names.append(factor_name)
        
        # 转换为DataFrame进行分析
        analysis_df = pd.DataFrame({
            '因子名称': factor_names,
            '综合得分': factor_scores,
            '评级': factor_ratings,
            '因子类型': factor_types
        })
        
        # 最佳因子
        if not analysis_df.empty and '综合得分' in analysis_df.columns and not analysis_df['综合得分'].isna().all():
            best_factor_idx = analysis_df['综合得分'].idxmax()
            best_factor = analysis_df.iloc[best_factor_idx]
        else:
            # 处理异常情况
            best_factor = None
            print("警告: 无法确定最佳因子（可能是因为数据为空或缺少'综合得分'列）")
        
        # 因子分布统计
        rating_counts = analysis_df['评级'].value_counts()
        type_counts = analysis_df['因子类型'].value_counts()
        
        # 优秀因子数量 (A+和A级)
        excellent_count = rating_counts.get('A+', 0) + rating_counts.get('A', 0)
        good_count = rating_counts.get('B+', 0) + rating_counts.get('B', 0)
        poor_count = rating_counts.get('C+', 0) + rating_counts.get('C', 0) + rating_counts.get('D', 0)
        
        # 生成精简摘要内容
        summary_lines = []
        
        # 核心摘要
        summary_lines.append(f"本次分析共评估 {total_factors} 个因子，整体表现{'良好' if excellent_count >= 3 else '一般' if good_count >= 2 else '较差'}。")
        
        # 核心发现
        if excellent_count > 0 and best_factor is not None:
            summary_lines.append(f"• 发现 {excellent_count} 个优秀因子(A+和A级)，其中 {best_factor['因子名称']} 表现最佳(评级:{best_factor['评级']})。")
        elif excellent_count > 0:
            summary_lines.append(f"• 发现 {excellent_count} 个优秀因子(A+和A级)，但无法确定最佳因子。")
        
        # 因子类型分析
        if type_counts.get('非线性因子', 0) > 0:
            summary_lines.append(f"• 检测到 {type_counts['非线性因子']} 个非线性因子，建议采用分组选股策略。")
        
        # 投资建议
        if excellent_count >= 2:
            summary_lines.append(f"💡 投资建议：采用多因子组合策略，重点配置A级以上因子。")
        elif good_count >= 1:
            summary_lines.append(f"💡 投资建议：选择表现最佳的2-3个因子进行策略构建。")
        else:
            summary_lines.append(f"💡 投资建议：当前因子表现有限，建议重新因子开发。")
        
        # 风险提示
        if poor_count >= total_factors * 0.5:
            summary_lines.append("[警告]  风险提示：多数因子表现较差，存在模型失效风险，建议谨慎使用。")
        elif poor_count >= total_factors * 0.3:
            summary_lines.append("[警告]  风险提示：部分因子表现不佳，需结合其他指标验证。")
        
        return '\n'.join(summary_lines)
    
    def classify_factors_by_ic(self):
        """
        根据IC均值将因子分为正向和负向两类
        
        Returns:
            tuple: (positive_factors_df, negative_factors_df) 两个DataFrame，按IC均值排序
        """
        if not self.analysis_results:
            print("错误：请先运行因子分析")
            return pd.DataFrame(), pd.DataFrame()
        
        # 构建因子数据
        factors_data = []
        for factor, results in self.analysis_results.items():
            # 计算综合得分（用于排序）
            ic_mean = results.get('ic_mean', np.nan)
            ic_std = results.get('ic_std', np.nan)
            ir = results.get('ir', np.nan)
            p_value = results.get('p_value', np.nan)
            long_short_return = 0
            
            if 'group_results' in results and results['group_results'] is not None:
                long_short_return = results['group_results'].get('long_short_return', np.nan)
            
            # 计算综合得分（正向因子）
            positive_score = 0
            if not np.isnan(ic_mean):
                if ic_mean >= 0.12:
                    positive_score += 4
                elif ic_mean >= 0.08:
                    positive_score += 3.5
                elif ic_mean >= 0.05:
                    positive_score += 3
                elif ic_mean >= 0.02:
                    positive_score += 2
                elif ic_mean >= 0.01:
                    positive_score += 1
                else:
                    positive_score += 0.5
            
            if not np.isnan(p_value):
                if p_value < 0.01:
                    positive_score += 1
                elif p_value < 0.05:
                    positive_score += 0.8
                elif p_value < 0.1:
                    positive_score += 0.6
                else:
                    positive_score += 0.3
            
            if not np.isnan(ir):
                if ir >= 1.5:
                    positive_score += 2.5
                elif ir >= 1.0:
                    positive_score += 2
                elif ir >= 0.5:
                    positive_score += 1.5
                elif ir >= 0.3:
                    positive_score += 1
                elif ir >= 0.15:
                    positive_score += 0.8
                else:
                    positive_score += 0.5
            
            if not np.isnan(long_short_return):
                if long_short_return >= 4:
                    positive_score += 2
                elif long_short_return >= 3:
                    positive_score += 1.8
                elif long_short_return >= 2:
                    positive_score += 1.5
                elif long_short_return >= 1:
                    positive_score += 1
                else:
                    positive_score += 0.5
            
            # 计算综合得分（负向因子）
            negative_score = 0
            if not np.isnan(ic_mean) and ic_mean < 0:
                abs_ic = abs(ic_mean)
                if abs_ic >= 0.1:
                    negative_score += 4
                elif abs_ic >= 0.07:
                    negative_score += 3.5
                elif abs_ic >= 0.05:
                    negative_score += 3
                elif abs_ic >= 0.03:
                    negative_score += 2
                else:
                    negative_score += 1
            
            if not np.isnan(p_value):
                if p_value < 0.01:
                    negative_score += 1
                elif p_value < 0.05:
                    negative_score += 0.8
                elif p_value < 0.1:
                    negative_score += 0.6
                else:
                    negative_score += 0.3
            
            if not np.isnan(ir):
                abs_ir = abs(ir)
                if abs_ir >= 1.5:
                    negative_score += 2
                elif abs_ir >= 1.0:
                    negative_score += 1.5
                elif abs_ir >= 0.5:
                    negative_score += 1
                elif abs_ir >= 0.3:
                    negative_score += 0.8
                elif abs_ir >= 0.15:
                    negative_score += 0.5
                else:
                    negative_score += 0.5
            
            if not np.isnan(long_short_return):
                if long_short_return < -2:
                    negative_score += 1
                elif long_short_return < -1:
                    negative_score += 0.8
                elif long_short_return < 0:
                    negative_score += 0.6
                else:
                    negative_score += 0.3
            
            # 确定因子类型和评级
            factor_type = "正向因子" if ic_mean > 0 else "负向因子" if ic_mean < 0 else "中性因子"
            
            # 确定评级
            if ic_mean > 0:
                if ic_mean >= 0.08 and ir >= 0.3:
                    if positive_score >= 3.5:
                        rating = "A+级"
                    else:
                        rating = "A级"
                elif ic_mean >= 0.08:
                    rating = "A-级"
                elif ic_mean >= 0.05 and ir >= 0.2:
                    if positive_score >= 2.5:
                        rating = "B+级"
                    else:
                        rating = "B级"
                elif ic_mean >= 0.02:
                    if positive_score >= 1.5:
                        rating = "C+级"
                    else:
                        rating = "C级"
                else:
                    rating = "D级"
            else:  # 负向因子
                abs_ic = abs(ic_mean)
                if abs_ic >= 0.08 and abs(ir) >= 0.3:
                    rating = "A-级"
                elif abs_ic >= 0.05 and abs(ir) >= 0.2:
                    rating = "B+级"
                elif abs_ic >= 0.03:
                    rating = "B级"
                elif abs_ic >= 0.02:
                    rating = "C+级"
                else:
                    rating = "D级"
            
            # 添加因子数据
            factors_data.append({
                '因子名称': factor,
                'IC均值': ic_mean,
                'IC标准差': ic_std,
                'IR值': ir,
                'p值': p_value,
                '多空收益': long_short_return,
                '综合得分': positive_score if ic_mean > 0 else negative_score,
                '因子类型': factor_type,
                '评级': rating
            })
        
        # 转换为DataFrame
        factors_df = pd.DataFrame(factors_data)
        
        # 分别获取正向和负向因子
        positive_factors = factors_df[factors_df['IC均值'] > 0].sort_values('IC均值', ascending=False)
        negative_factors = factors_df[factors_df['IC均值'] < 0].sort_values('IC均值', ascending=True)
        
        return positive_factors, negative_factors
    
    def generate_factor_classification_overview(self):
        """
        生成因子分类概览
        
        Returns:
            str: 概览信息字符串
        """
        # 获取分类因子数据
        positive_factors, negative_factors = self.classify_factors_by_ic()
        
        # 构建概览信息
        overview_lines = []
        
        # 添加标题
        overview_lines.append("=" * 80)
        overview_lines.append("                     因子分类概览")
        overview_lines.append("=" * 80)
        
        # 添加基本统计信息
        total_factors = len(positive_factors) + len(negative_factors)
        overview_lines.append(f"因子总数: {total_factors}个")
        
        if len(positive_factors) > 0:
            avg_positive_ic = positive_factors['IC均值'].mean()
            best_positive_factor = positive_factors.iloc[0]
            overview_lines.append(f"正向因子: {len(positive_factors)}个，平均IC均值: {avg_positive_ic:.3f}")
            overview_lines.append(f"最佳正向因子: {best_positive_factor['因子名称']} (IC均值: {best_positive_factor['IC均值']:.3f}, 评级: {best_positive_factor['评级']})")
        else:
            overview_lines.append("正向因子: 0个")
        
        if len(negative_factors) > 0:
            avg_negative_ic = negative_factors['IC均值'].mean()
            best_negative_factor = negative_factors.iloc[0]  # 因为负向因子按IC均值升序排列，第一个是最负的
            overview_lines.append(f"负向因子: {len(negative_factors)}个，平均IC均值: {avg_negative_ic:.3f}")
            overview_lines.append(f"最佳负向因子: {best_negative_factor['因子名称']} (IC均值: {best_negative_factor['IC均值']:.3f}, 评级: {best_negative_factor['评级']})")
        else:
            overview_lines.append("负向因子: 0个")
        
        # 添加评级分布统计
        if len(positive_factors) > 0:
            overview_lines.append("\n正向因子评级分布:")
            positive_ratings = positive_factors['评级'].value_counts()
            for rating, count in positive_ratings.items():
                overview_lines.append(f"  {rating}: {count}个")
        
        if len(negative_factors) > 0:
            overview_lines.append("\n负向因子评级分布:")
            negative_ratings = negative_factors['评级'].value_counts()
            for rating, count in negative_ratings.items():
                overview_lines.append(f"  {rating}: {count}个")
        
        # 添加使用建议
        overview_lines.append("\n使用建议:")
        
        if len(positive_factors) > 0:
            top_positive = positive_factors.head(3)
            overview_lines.append("推荐正向因子:")
            for _, factor in top_positive.iterrows():
                overview_lines.append(f"  - {factor['因子名称']}: 建议权重{self._get_suggested_weight(factor['评级'], True)} (IC均值: {factor['IC均值']:.3f}, IR值: {factor['IR值']:.3f})")
        else:
            overview_lines.append("正向因子: 暂未发现有效的正向因子，建议进一步筛选或调整因子构建方法")
        
        if len(negative_factors) > 0:
            top_negative = negative_factors.head(3)
            overview_lines.append("推荐负向因子 (反向使用):")
            for _, factor in top_negative.iterrows():
                overview_lines.append(f"  - {factor['因子名称']}: 建议权重{self._get_suggested_weight(factor['评级'], False)} (IC均值: {factor['IC均值']:.3f}, IR值: {factor['IR值']:.3f})")
        else:
            overview_lines.append("负向因子: 暂未发现有效的负向因子")
        
        # 添加组合配置建议
        overview_lines.append("\n组合配置建议:")
        overview_lines.append("建议采用多因子组合策略，平衡风险收益:")
        
        if len(positive_factors) > 0 and len(negative_factors) > 0:
            overview_lines.append("1. 正向因子与负向因子结合使用，实现对冲，降低组合波动性")
            overview_lines.append("2. 正向因子配置较高权重(10%-30%)，作为核心配置")
            overview_lines.append("3. 负向因子配置较低权重(5%-15%)，作为对冲和风险控制工具")
        elif len(positive_factors) > 0:
            overview_lines.append("1. 仅使用正向因子构成组合")
            overview_lines.append("2. 选择不同评级的正向因子组合，分散风险")
        elif len(negative_factors) > 0:
            overview_lines.append("1. 仅使用负向因子反向构成组合")
            overview_lines.append("2. 选择不同评级的负向因子组合，注意风险控制")
        
        return "\n".join(overview_lines)
    
    def _get_suggested_weight(self, rating, is_positive):
        """
        根据因子评级获取建议权重
        
        Args:
            rating: 因子评级
            is_positive: 是否为正向因子
        
        Returns:
            str: 建议权重范围
        """
        if is_positive:  # 正向因子
            if "A+" in rating or "A级" in rating:
                return "15%-25%"
            elif "A-" in rating or "B+" in rating:
                return "10%-15%"
            elif "B级" in rating or "C+" in rating:
                return "5%-10%"
            elif "C级" in rating:
                return "3%-5%"
            else:
                return "0%-3%"
        else:  # 负向因子
            if "A-" in rating:
                return "-10%至-20%"
            elif "B+" in rating or "B级" in rating:
                return "-5%至-10%"
            elif "C+" in rating or "C级" in rating:
                return "-3%至-5%"
            else:
                 return "0%至-3%"
     
    def _get_scoring_standards(self):
        """
        获取因子评分标准的详细说明
        
        Returns:
            str: 评分标准说明文本
        """
        standards = []
        standards.append("因子评分标准基于国内量化实践，主要考虑以下维度：")
        standards.append("")
        standards.append("1. IC均值权重配置标准：")
        standards.append("   • 正向因子：IC均值越高，预测能力越强")
        standards.append("   • 负向因子：IC均值越负（绝对值越大），反向预测能力越强")
        standards.append("   • A级因子：|IC均值| ≥ 0.08")
        standards.append("   • B+级因子：|IC均值| ≥ 0.05")
        standards.append("   • B级因子：|IC均值| ≥ 0.03")
        standards.append("   • C+级因子：|IC均值| ≥ 0.02")
        standards.append("   • C级因子：|IC均值| ≥ 0.01")
        standards.append("")
        standards.append("2. 统计显著性评分标准：")
        standards.append("   • p值 < 0.01：高度显著，加分1.0")
        standards.append("   • 0.01 ≤ p值 < 0.05：显著，加分0.8")
        standards.append("   • 0.05 ≤ p值 < 0.1：边缘显著，加分0.6")
        standards.append("   • p值 ≥ 0.1：不显著，加分0.3")
        standards.append("")
        standards.append("3. IR值评分标准：")
        standards.append("   • |IR值| ≥ 1.5：优秀，加分2.5")
        standards.append("   • |IR值| ≥ 1.0：良好，加分2.0")
        standards.append("   • |IR值| ≥ 0.5：一般，加分1.5")
        standards.append("   • |IR值| ≥ 0.3：较弱，加分1.0")
        standards.append("   • |IR值| < 0.3：很差，加分0.5")
        standards.append("")
        standards.append("4. 多空收益评分标准：")
        standards.append("   • 多空收益 ≥ 4%：优秀，加分2.0")
        standards.append("   • 多空收益 ≥ 3%：良好，加分1.8")
        standards.append("   • 多空收益 ≥ 2%：一般，加分1.5")
        standards.append("   • 多空收益 ≥ 1%：较弱，加分1.0")
        standards.append("   • 多空收益 < 1%：很差，加分0.5")
        standards.append("")
        standards.append("5. 综合评级标准：")
        standards.append("   • A+级：总分 ≥ 8.5，预测能力强，收益表现优秀")
        standards.append("   • A级：总分 ≥ 7.5，预测能力强，收益表现良好")
        standards.append("   • A-级：总分 ≥ 6.5，预测能力较强，收益表现一般")
        standards.append("   • B+级：总分 ≥ 5.5，预测能力中等，收益表现有限")
        standards.append("   • B级：总分 ≥ 4.5，预测能力一般，收益表现较弱")
        standards.append("   • B-级：总分 ≥ 3.5，预测能力较弱")
        standards.append("   • C+级：总分 ≥ 2.5，预测能力很弱")
        standards.append("   • C级：总分 ≥ 1.5，预测能力微弱")
        standards.append("   • C-级：总分 ≥ 0.5，几乎无预测能力")
        standards.append("   • D级：总分 < 0.5，无预测能力或反向预测")
        standards.append("")
        standards.append("6. 特别评级机制：")
        standards.append("   • 优秀因子（A级以上）可获得额外加分和权重建议")
        standards.append("   • 负向因子采用特殊评分体系，注重IC绝对值和稳定性")
        standards.append("   • 非线性因子提供特殊标识和使用建议")
        standards.append("")
        standards.append("7. 使用建议：")
        standards.append("   • A+级因子：建议配置15%-25%权重")
        standards.append("   • A级因子：建议配置10%-15%权重")
        standards.append("   • B+级因子：建议配置5%-10%权重")
        standards.append("   • B级因子：建议配置3%-5%权重")
        standards.append("   • C+级及以下因子：不建议使用或仅用于组合辅助")
        standards.append("")
        standards.append("8. 国内量化实践标准：")
        standards.append("   • 严格按照国内量化行业标准进行评级")
        standards.append("   • 充分考虑A股市场特殊性")
        standards.append("   • 结合实际交易成本和滑点")
        standards.append("   • 注重因子的稳定性和可持续性")
        
        return "\n".join(standards)
    
    def generate_positive_factors_analysis(self):
        """
        生成正向因子详细分析报告
        
        Returns:
            str: 正向因子详细分析报告
        """
        # 获取分类因子数据
        positive_factors, negative_factors = self.classify_factors_by_ic()
        
        if len(positive_factors) == 0:
            return "未发现正向因子，无法生成详细分析。"
        
        # 构建正向因子分析报告
        analysis_lines = []
        
        # 添加标题
        analysis_lines.append("=" * 80)
        analysis_lines.append("                     正向因子详细分析")
        analysis_lines.append("=" * 80)
        
        # 添加总体概况
        analysis_lines.append(f"正向因子总数: {len(positive_factors)}个")
        
        # 计算整体统计指标
        avg_ic = positive_factors['IC均值'].mean()
        avg_ir = positive_factors['IR值'].mean()
        avg_long_short = positive_factors['多空收益'].mean()
        total_factors = len(positive_factors)
        
        analysis_lines.append(f"平均IC均值: {avg_ic:.4f}")
        analysis_lines.append(f"平均IR值: {avg_ir:.4f}")
        analysis_lines.append(f"平均多空收益: {avg_long_short:.4f}")
        
        # 添加评级分布统计
        analysis_lines.append("\n评级分布:")
        rating_dist = positive_factors['评级'].value_counts()
        total_rating = len(positive_factors)
        
        for rating in ['A+', 'A级', 'A-', 'B+', 'B级', 'B-', 'C+', 'C级', 'C-', 'D级']:
            if rating in rating_dist.index:
                count = rating_dist[rating]
                percentage = (count / total_rating) * 100
                analysis_lines.append(f"  {rating}: {count}个 ({percentage:.1f}%)")
        
        # 添加A级因子详细分析
        top_rated = positive_factors[positive_factors['评级'].str.contains('A\\+', na=False)]
        if len(top_rated) == 0:
            top_rated = positive_factors[positive_factors['评级'].str.contains('A级', na=False)]
        
        if len(top_rated) > 0:
            analysis_lines.append(f"\n优秀正向因子 (A级以上) 详细分析:")
            for idx, (_, factor) in enumerate(top_rated.head(5).iterrows(), 1):
                analysis_lines.append(f"\n--- 优秀因子 #{idx}: {factor['因子名称']} ---")
                analysis_lines.append(f"综合得分: {factor['综合得分']:.2f}")
                analysis_lines.append(f"评级: {factor['评级']}")
                analysis_lines.append(f"建议权重: {self._get_suggested_weight(factor['评级'], True)}")
                analysis_lines.append(f"IC均值: {factor['IC均值']:.4f}")
                analysis_lines.append(f"IC标准差: {factor['IC标准差']:.4f}")
                analysis_lines.append(f"IR值: {factor['IR值']:.4f}")
                analysis_lines.append(f"多空收益: {factor['多空收益']:.4f}")
                analysis_lines.append(f"统计显著性: p值={factor['p值']:.4f}")
                
                # 计算胜率（如果有数据）
                win_rate = "N/A"
                if 'group_results' in analyzer.analysis_results[factor['因子名称']] and \
                   analyzer.analysis_results[factor['因子名称']]['group_results'] is not None:
                    avg_returns = analyzer.analysis_results[factor['因子名称']]['group_results']['avg_returns']
                    if '胜率' in avg_returns.columns:
                        win_rate = f"{avg_returns['胜率'].mean():.2%}"
                
                analysis_lines.append(f"胜率: {win_rate}")
                
                # 分析因子表现
                performance_analysis = []
                if factor['IC均值'] > 0.02:
                    performance_analysis.append("IC均值优秀，预测能力强")
                elif factor['IC均值'] > 0.01:
                    performance_analysis.append("IC均值良好，预测能力适中")
                else:
                    performance_analysis.append("IC均值一般，预测能力有待提升")
                
                if factor['IR值'] > 0.5:
                    performance_analysis.append("风险调整后收益表现优秀")
                elif factor['IR值'] > 0.3:
                    performance_analysis.append("风险调整后收益表现良好")
                else:
                    performance_analysis.append("风险调整后收益表现一般")
                
                if factor['胜率'] > 0.6:
                    performance_analysis.append("策略胜率较高")
                elif factor['胜率'] > 0.5:
                    performance_analysis.append("策略胜率适中")
                else:
                    performance_analysis.append("策略胜率偏低，需要优化")
                
                analysis_lines.append("综合评价: " + "；".join(performance_analysis))
        
        # 添加策略建议
        analysis_lines.append("\n\n投资策略建议:")
        
        if len(positive_factors) > 0:
            # 获取前5个最佳因子
            top_5 = positive_factors.head(5)
            
            analysis_lines.append("\n1. 单因子策略:")
            for idx, (_, factor) in enumerate(top_5.iterrows(), 1):
                weight_range = self._get_suggested_weight(factor['评级'], True)
                analysis_lines.append(f"   因子{idx}: {factor['因子名称']}")
                analysis_lines.append(f"   - 建议配置权重: {weight_range}")
                analysis_lines.append(f"   - 预期年化收益: {factor['IC均值']*12:.1%} (基于IC均值估算)")
                analysis_lines.append(f"   - 风险水平: {'低' if factor['IR值'] > 0.5 else '中' if factor['IR值'] > 0.3 else '高'}")
            
            analysis_lines.append("\n2. 多因子组合策略:")
            analysis_lines.append("   - 选择3-5个不同评级的正向因子组合")
            analysis_lines.append("   - 核心配置: A级因子，占比50-70%")
            analysis_lines.append("   - 辅助配置: B级因子，占比20-40%")
            analysis_lines.append("   - 分散配置: C级因子，占比10-20%")
            
            analysis_lines.append("\n3. 风险控制措施:")
            analysis_lines.append("   - 单一因子权重不超过25%")
            analysis_lines.append("   - 设置止损点: 单因子IC连续低于-0.01时考虑剔除")
            analysis_lines.append("   - 定期重新评估: 建议每月重新计算IC值")
            analysis_lines.append("   - 市值中性: 建议对市值进行中性化处理")
        
        # 添加数据质量评估
        analysis_lines.append("\n数据质量评估:")
        valid_factors = positive_factors.dropna()
        missing_data_pct = ((len(positive_factors) - len(valid_factors)) / len(positive_factors)) * 100
        
        analysis_lines.append(f"数据完整性: {100-missing_data_pct:.1f}%")
        analysis_lines.append(f"有效因子数: {len(valid_factors)}个")
        
        if missing_data_pct > 10:
            analysis_lines.append("警告: 部分因子数据缺失较多，可能影响分析结果的可靠性")
        
        # 添加市场环境适应性
        analysis_lines.append("\n市场环境适应性:")
        if avg_ic > 0.015:
            analysis_lines.append("当前市场环境对正向因子较为有利")
        elif avg_ic > 0.01:
            analysis_lines.append("当前市场环境对正向因子较为中性")
        else:
            analysis_lines.append("当前市场环境对正向因子不利，建议调整因子选择标准")
        
        return "\n".join(analysis_lines)
    
    def generate_negative_factors_analysis(self):
        """
        生成负向因子详细分析报告
        
        Returns:
            str: 负向因子详细分析报告
        """
        # 获取分类因子数据
        positive_factors, negative_factors = self.classify_factors_by_ic()
        
        if len(negative_factors) == 0:
            return "未发现负向因子，无法生成详细分析。"
        
        # 构建负向因子分析报告
        analysis_lines = []
        
        # 添加标题
        analysis_lines.append("=" * 80)
        analysis_lines.append("                     负向因子详细分析")
        analysis_lines.append("=" * 80)
        
        # 添加总体概况
        analysis_lines.append(f"负向因子总数: {len(negative_factors)}个")
        
        # 计算整体统计指标
        avg_ic = negative_factors['IC均值'].mean()
        avg_ir = negative_factors['IR值'].mean()
        avg_long_short = negative_factors['多空收益'].mean()
        
        analysis_lines.append(f"平均IC均值: {avg_ic:.4f}")
        analysis_lines.append(f"平均IR值: {avg_ir:.4f}")
        analysis_lines.append(f"平均多空收益: {avg_long_short:.4f}")
        
        # 添加评级分布统计
        analysis_lines.append("\n评级分布:")
        rating_dist = negative_factors['评级'].value_counts()
        total_rating = len(negative_factors)
        
        for rating in ['A+', 'A级', 'A-', 'B+', 'B级', 'B-', 'C+', 'C级', 'C-', 'D级']:
            if rating in rating_dist.index:
                count = rating_dist[rating]
                percentage = (count / total_rating) * 100
                analysis_lines.append(f"  {rating}: {count}个 ({percentage:.1f}%)")
        
        # 添加最佳负向因子详细分析
        # 负向因子按IC均值升序排列，第一个是最负的
        best_negative = negative_factors.head(5)
        
        analysis_lines.append(f"\n优质负向因子 (反向使用) 详细分析:")
        for idx, (_, factor) in enumerate(best_negative.iterrows(), 1):
            analysis_lines.append(f"\n--- 优质因子 #{idx}: {factor['因子名称']} ---")
            analysis_lines.append(f"综合得分: {factor['综合得分']:.2f}")
            analysis_lines.append(f"评级: {factor['评级']}")
            analysis_lines.append(f"建议权重 (反向): {self._get_suggested_weight(factor['评级'], False)}")
            analysis_lines.append(f"IC均值: {factor['IC均值']:.4f} (原值)")
            analysis_lines.append(f"反向IC均值: {-factor['IC均值']:.4f}")
            analysis_lines.append(f"IC标准差: {factor['IC标准差']:.4f}")
            analysis_lines.append(f"IR值: {factor['IR值']:.4f}")
            analysis_lines.append(f"多空收益: {factor['多空收益']:.4f}")
            analysis_lines.append(f"胜率: {factor['胜率']:.2%}")
            analysis_lines.append(f"统计显著性: p值={factor['p值']:.4f}")
            
            # 分析因子表现
            performance_analysis = []
            if abs(factor['IC均值']) > 0.02:
                performance_analysis.append("反向IC绝对值优秀，预测能力强")
            elif abs(factor['IC均值']) > 0.01:
                performance_analysis.append("反向IC绝对值良好，预测能力适中")
            else:
                performance_analysis.append("反向IC绝对值一般，预测能力有待提升")
            
            if factor['IR值'] > 0.5:
                performance_analysis.append("风险调整后收益表现优秀")
            elif factor['IR值'] > 0.3:
                performance_analysis.append("风险调整后收益表现良好")
            else:
                performance_analysis.append("风险调整后收益表现一般")
            
            if factor['胜率'] > 0.6:
                performance_analysis.append("反向策略胜率较高")
            elif factor['胜率'] > 0.5:
                performance_analysis.append("反向策略胜率适中")
            else:
                performance_analysis.append("反向策略胜率偏低，需要优化")
            
            analysis_lines.append("综合评价: " + "；".join(performance_analysis))
        
        # 添加反向策略建议
        analysis_lines.append("\n\n反向投资策略建议:")
        
        if len(negative_factors) > 0:
            # 获取前5个最佳负向因子（最负的IC值）
            top_5_negative = negative_factors.head(5)
            
            analysis_lines.append("\n1. 单因子反向策略:")
            for idx, (_, factor) in enumerate(top_5_negative.iterrows(), 1):
                weight_range = self._get_suggested_weight(factor['评级'], False)
                analysis_lines.append(f"   因子{idx}: {factor['因子名称']} (反向)")
                analysis_lines.append(f"   - 建议配置权重: {weight_range}")
                analysis_lines.append(f"   - 预期年化收益: {abs(factor['IC均值'])*12:.1%} (基于反向IC值估算)")
                analysis_lines.append(f"   - 风险水平: {'低' if factor['IR值'] > 0.5 else '中' if factor['IR值'] > 0.3 else '高'}")
            
            analysis_lines.append("\n2. 反向因子组合策略:")
            analysis_lines.append("   - 选择2-3个不同评级的负向因子组合")
            analysis_lines.append("   - 核心配置: A级负向因子，占比30-50%")
            analysis_lines.append("   - 辅助配置: B级负向因子，占比20-30%")
            analysis_lines.append("   - 风险分散: C级负向因子，占比10-20%")
            analysis_lines.append("   - 注意: 负向因子通常用于风险对冲，不宜配置过高权重")
            
            analysis_lines.append("\n3. 反向策略风险控制:")
            analysis_lines.append("   - 单一反向因子权重不超过20%")
            analysis_lines.append("   - 设置止损点: 反向IC连续高于0.01时考虑剔除")
            analysis_lines.append("   - 定期重新评估: 建议每两周重新计算IC值")
            analysis_lines.append("   - 组合使用: 与正向因子结合使用实现风险对冲")
        
        # 添加对冲策略建议
        analysis_lines.append("\n对冲策略建议:")
        analysis_lines.append("\n1. 市场中性对冲:")
        analysis_lines.append("   - 正向因子: 50-70%")
        analysis_lines.append("   - 负向因子: 30-50%")
        analysis_lines.append("   - 目标: 降低组合整体波动性")
        
        analysis_lines.append("\n2. 行业中性对冲:")
        analysis_lines.append("   - 正向因子: 40-60%")
        analysis_lines.append("   - 负向因子: 40-60%")
        analysis_lines.append("   - 目标: 消除行业偏好风险")
        
        analysis_lines.append("\n3. 时间中性对冲:")
        analysis_lines.append("   - 正向因子: 60-80%")
        analysis_lines.append("   - 负向因子: 20-40%")
        analysis_lines.append("   - 目标: 在特定时间窗口内捕捉机会")
        
        return "\n".join(analysis_lines)
    
    def generate_factor_analysis_report(self, summary_df, process_factors=False, factor_method='standardize', winsorize=False):
        """
        生成精简的因子分析报告
        
        Args:
            summary_df: 因子分析汇总数据框
            process_factors: 是否对因子进行了处理
            factor_method: 因子处理方法，'standardize'（标准化）或 'normalize'（归一化）
            winsorize: 是否进行了缩尾处理
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f'因子分析详情_精简版_{timestamp}.txt'  # 修改文件名格式，生成精简版
    
    # 使用新的分类函数对因子进行分类
    positive_factors, negative_factors = self.classify_factors_by_ic()
    
    # 生成因子分类概览
    classification_overview = self.generate_factor_classification_overview()
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        # 报告标题
        f.write("=" * 80 + "\n")
        f.write("                    因子分析详细报告                   \n")
        f.write("=" * 80 + "\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"数据文件: {DEFAULT_DATA_FILE}\n")
        f.write("\n")
        
        # 1. 因子分类概览
        f.write("1. 因子分类概览\n")
        f.write("=" * 50 + "\n\n")
        f.write(classification_overview)
        f.write("\n")
        
        # 2. 正向因子详细分析
        f.write("2. 正向因子详细分析\n")
        f.write("=" * 50 + "\n\n")
        positive_analysis = self.generate_positive_factors_analysis()
        f.write(positive_analysis)
        f.write("\n")
        
        # 3. 负向因子详细分析
        f.write("3. 负向因子详细分析\n")
        f.write("=" * 50 + "\n\n")
        negative_analysis = self.generate_negative_factors_analysis()
        f.write(negative_analysis)
        f.write("\n")
        
        # 4. 评分标准说明
        f.write("4. 评分标准说明\n")
        f.write("=" * 50 + "\n\n")
        f.write(self._get_scoring_standards())
        f.write("\n")
    
    print(f"详细分析报告已生成: {report_filename}")
    return report_filename
    
    def generate_summary_report(self):
        """
        生成分析汇总报告
        """
        if not self.analysis_results:
            print("错误：请先运行因子分析")
            return
        
        # 创建汇总表
        summary_data = []
        missing_data_count = 0
        
        for factor, results in self.analysis_results.items():
            row = {
                '因子名称': factor,
                'IC均值': results['ic_mean'],
                'IC标准差': results['ic_std'],
                'IR值': results['ir'],
                't统计量': results['t_stat'],
                'p值': results['p_value']
            }
            
            if 'group_results' in results and results['group_results'] is not None:
                row['多空收益'] = results['group_results']['long_short_return']
            
            # 检查缺失值
            if np.isnan(results['ic_std']) or np.isnan(results['ir']):
                missing_data_count += 1
                print(f"警告: 因子 '{factor}' 存在缺失数据 - IC标准差: {results['ic_std']}, IR值: {results['ir']}")
            
            summary_data.append(row)
        
        summary_df = pd.DataFrame(summary_data)
        
        # 创建显示用的数据框，将缺失值替换为'N/A'
        display_df = summary_df.copy()
        for col in ['IC均值', 'IC标准差', 'IR值', 't统计量', 'p值', '多空收益']:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: 'N/A' if pd.isna(x) else f"{x:.3f}")
        
        print("\n=== 因子分析汇总报告 ===")
        print(display_df.to_string(index=False))
        
        # 如果存在缺失数据，显示警告
        if missing_data_count > 0:
            print(f"\n警告: 共有 {missing_data_count} 个因子存在缺失数据，请检查详细信息")
        
        # 保存汇总报告，设置小数位数为3位
        summary_df_rounded = summary_df.round(3)
        # 添加时间戳到文件名，但避免使用可能导致特定格式报告的命名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'因子分析汇总_{timestamp}.csv'  # 修改文件名格式，避免生成'因子分析报告_当日回调_时间戳.csv'
        summary_df_rounded.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n汇总报告已保存到 '{filename}'")
        
        return summary_df
    
    def run_filtered_factor_analysis(self, filter_conditions, use_pearson=False):
        """
        运行带参数的因子分析
        
        Args:
            filter_conditions: 过滤条件字典，格式为 {factor_name: (operator, value)}
                              例如：{"信号发出时上市天数": (">", 1200), "信号当日收盘涨跌幅": ("<", -19.9)}
                              支持的操作符：'>', '<', '>=', '<=', '==', '!='
            use_pearson: 是否使用Pearson相关系数计算IC值，默认为False（使用Spearman相关系数）
        
        Returns:
            bool: 分析是否成功
        """
    
    def optimize_factor_parameter(self, factor_name, operator, initial_value, optimize_metric='long_short_return', use_pearson=False):
        """
        优化因子参数，只保留10等分数据测试
        
        Args:
            factor_name: 要优化的因子名称
            operator: 操作符（实际已不再使用，保留兼容性）
            initial_value: 初始参数值（实际已不再使用，保留兼容性）
            optimize_metric: 优化指标
            use_pearson: 是否使用Pearson相关系数计算IC值，默认为False（使用Spearman相关系数）
        
        Returns:
            dict: 包含10等分测试结果的字典
        """
        # 创建日志文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"参数优化_{factor_name}_decile_test_{timestamp}.txt"
        
        # 日志函数
        def log(message):
            print(message)
            with open(log_filename, 'a', encoding='utf-8') as f:
                f.write(message + '\n')
        
        # 保存原始数据
        original_processed_data = self.processed_data.copy()
        
        # 检查因子是否存在且为数值型
        if factor_name not in self.processed_data.columns:
            error_msg = f"错误：因子 '{factor_name}' 在数据中不存在"
            log(error_msg)
            return None
        
        # 记录参数优化开始信息
        log("\n" + "="*80)
        log(f"参数优化开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log(f"优化因子: {factor_name}")
        log(f"优化指标: {optimize_metric}")
        log("="*80)
        
        # 开始10等分数据测试
        log("\n" + "="*80)
        log(f"开始10等分数据测试")
        log("="*80)
        
        # 按因子值从小到大排序并平均分成10份
        temp_data = original_processed_data.copy()
        if not pd.api.types.is_numeric_dtype(temp_data[factor_name]):
            temp_data[factor_name] = pd.to_numeric(temp_data[factor_name], errors='coerce')
        
        # 去除NaN值
        temp_data = temp_data.dropna(subset=[factor_name])
        
        total_data_count = len(temp_data)
        log(f"数据总量: {total_data_count} 行")
        
        # 如果数据量足够，进行10等分测试
        if total_data_count > 0:
            # 按因子值排序
            temp_data_sorted = temp_data.sort_values(by=factor_name)
            
            # 平均分成10份
            n_bins = 10
            bin_size = len(temp_data_sorted) // n_bins
            decile_performances = []
            
            for i in range(n_bins):
                # 计算每个分位的数据范围
                start_idx = i * bin_size
                end_idx = len(temp_data_sorted) if i == n_bins - 1 else (i + 1) * bin_size
                
                # 获取该分位的数据
                decile_data = temp_data_sorted.iloc[start_idx:end_idx].copy()
                
                # 获取该分位的因子值范围
                decile_min = decile_data[factor_name].min()
                decile_max = decile_data[factor_name].max()
                
                log(f"\n=== 第 {i+1} 等分测试（共{len(decile_data)}行） ===")
                log(f"因子值范围: {decile_min:.3f} 到 {decile_max:.3f}")
                
                # 临时更新处理后的数据
                self.processed_data = decile_data
                
                # 计算性能指标
                try:
                    ic_mean, ic_std, _, _, _ = self.calculate_ic(factor_name, use_pearson=use_pearson)
                    ir = ic_mean / ic_std if not np.isnan(ic_std) and ic_std != 0 else 0.0
                except Exception as e:
                    log(f"  计算IC值时出错: {str(e)}")
                    ic_mean = 0.0
                    ir = 0.0
                
                try:
                    group_results = self.calculate_group_returns(factor_name)
                    long_short_return = group_results.get('long_short_return', 0.0) if group_results else 0.0
                    if np.isnan(long_short_return):
                        long_short_return = 0.0
                except Exception as e:
                    log(f"  计算分组收益时出错: {str(e)}")
                    long_short_return = 0.0
                
                # 计算胜率
                try:
                    win_rate = 0.0
                    if group_results and 'avg_returns' in group_results:
                        avg_returns = group_results['avg_returns']
                        if not avg_returns.empty:
                            positive_groups = (avg_returns['mean_return'] > 0).sum()
                            if len(avg_returns) > 0:
                                win_rate = (positive_groups / len(avg_returns)) * 100
                except Exception as e:
                    log(f"  计算胜率时出错: {str(e)}")
                    win_rate = 0.0
                
                # 存储分位性能
                decile_performances.append({
                    'decile': i + 1,
                    'factor_min': decile_min,
                    'factor_max': decile_max,
                    'data_count': len(decile_data),
                    'long_short_return': long_short_return,
                    'ir': ir,
                    'ic_mean': ic_mean,
                    'win_rate': win_rate
                })
                
                # 记录测试结果
                log(f"  多空收益: {long_short_return:.3f}%")
                log(f"  IR值: {ir:.3f}")
                log(f"  IC均值: {ic_mean:.3f}")
                log(f"  胜率: {win_rate:.1f}%")
            
            # 恢复原始数据
            self.processed_data = original_processed_data.copy()
            
            # 保存10等分测试结果到CSV
            if decile_performances:
                decile_df = pd.DataFrame(decile_performances)
                decile_df = decile_df.fillna(0)
                
                decile_csv_filename = f"十等分测试_{factor_name}_{timestamp}.csv"
                decile_df.to_csv(decile_csv_filename, index=False, encoding='utf-8-sig')
                
                # 找出表现最好的分位
                if optimize_metric == 'long_short_return':
                    best_decile = max(decile_performances, key=lambda x: x['long_short_return'])
                elif optimize_metric == 'ir':
                    best_decile = max(decile_performances, key=lambda x: x['ir'])
                else:
                    best_decile = max(decile_performances, key=lambda x: x['win_rate'])
                
                log(f"\n最佳表现分位: 第 {best_decile['decile']} 等分")
                log(f"因子值范围: {best_decile['factor_min']:.3f} 到 {best_decile['factor_max']:.3f}")
                log(f"多空收益: {best_decile['long_short_return']:.3f}%")
                
                # 存储初始结果
                results = {
                    'best_decile': best_decile,
                    'all_deciles': decile_performances,
                    'csv_file': decile_csv_filename
                }
                
                # 记录参数优化结束信息
                log("\n" + "="*80)
                log(f"参数优化结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                log(f"日志文件保存路径: {log_filename}")
                
                # 恢复原始数据
                self.processed_data = original_processed_data
                
                return results
            else:
                log("警告: 没有生成有效的10等分测试结果")
                return None
        else:
            log("警告: 因子值范围内没有足够的数据进行10等分测试")
            return None
    
    def _generate_filtered_summary_report(self, filtered_analysis_results, condition_str):
        """
        生成带条件的因子分析汇总报告
        
        Args:
            filtered_analysis_results: 过滤后的分析结果
            condition_str: 条件描述字符串
        """
        # 创建汇总表
        summary_data = []
        
        for factor, results in filtered_analysis_results.items():
            row = {
                '因子名称': factor,
                'IC均值': results['ic_mean'],
                'IC标准差': results['ic_std'],
                'IR值': results['ir'],
                't统计量': results['t_stat'],
                'p值': results['p_value']
            }
            
            if 'group_results' in results and results['group_results'] is not None:
                row['多空收益'] = results['group_results']['long_short_return']
            
            summary_data.append(row)
        
        summary_df = pd.DataFrame(summary_data)
        
        print(f"\n=== 带条件的因子分析汇总报告 ({condition_str}) ===")
        print(summary_df.to_string(index=False, float_format='%.3f'))
        
        # 保存汇总报告，设置小数位数为3位
        # 使用条件字符串的简短版本作为文件名
        safe_condition_str = condition_str.replace(' ', '').replace('>', 'gt').replace('<', 'lt').replace('=', 'eq').replace('且', '_')
        # 添加时间戳到文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'因子分析汇总报告_{safe_condition_str}_{timestamp}.csv'
        summary_df_rounded = summary_df.round(3)
        summary_df_rounded.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n带条件的汇总报告已保存到 '{filename}'")
        
        return summary_df
    
    def run_full_analysis(self):
        """
        运行完整的因子分析流程
        """
        if not self.run_factor_analysis():
            return False
        
        print("\n=== 开始可视化分析结果 ===")
        
        # 绘制因子分布图（只有在可视化功能可用时）
        if HAS_PLOT:
            self.plot_factor_distribution()
        
        # 绘制分组收益图（只有在可视化功能可用时）
        if HAS_PLOT:
            self.plot_group_returns()
        
        # 生成汇总报告
        self.generate_summary_report()
        
        print("\n=== 因子分析完成 ===")
        return True




# 删除重复的main函数定义，只保留末尾的完整版本
class ParameterizedFactorAnalyzer:
    """专门针对带参数因子的综合分析器"""
    
    def __init__(self, data, file_path=None):
        """初始化综合因子分析器"""
        self.data = data
        self.file_path = file_path
        self.factors = [
             '信号发出时上市天数',
             '日最大跌幅百分比',
             '信号当日收盘涨跌幅',
             '信号后一日开盘涨跌幅',
             '次日开盘后总体下跌幅度',
             '前10日最大涨幅',
             '当日回调'
         ]
        self.factor_list = self.factors  # 修复：添加factor_list属性
        self.return_col = '持股2日收益率'
        self.sqrt_annualization_factor = np.sqrt(252)
        self.annualization_factor = 252
        
        # 确保数据有效
        if self.data is None or self.data.empty:
            print("错误: 没有有效数据")
            # 不返回值，让对象仍可被创建但处于无效状态
    
    def load_data(self):
        """从文件加载数据"""
        try:
            if self.file_path.endswith('.csv'):
                self.data = pd.read_csv(self.file_path, encoding='utf-8-sig')
            elif self.file_path.endswith('.xlsx') or self.file_path.endswith('.xls'):
                self.data = pd.read_excel(self.file_path)
            else:
                raise ValueError("仅支持CSV和Excel文件格式")
            
            return True
        except Exception as e:
            print(f"数据加载失败: {e}")
            return False
# 已删除复杂的自适应年化计算方法，使用优化版本（第1085行）
# 优化版本特点：
# 1. 使用标准复利年化方法作为主要计算方式
# 2. 保留CAGR方法作为对比方法
# 3. 删除线性年化方法（忽视复利效应）
# 4. 增强数据特征分析和验证机制
    
    def preprocess_data(self):
        """预处理数据"""
        if self.data is None or self.data.empty:
            print("错误: 没有数据可处理")
            return False
        
        try:
            # 复制数据
            df = self.data.copy()
            
            # 处理百分比字符串列（转换百分比）
            percentage_columns = [
                '日最大跌幅百分比', '信号当日收盘涨跌幅', '信号后一日开盘涨跌幅', 
                '次日开盘后总体下跌幅度', '前10日最大涨幅', '当日回调', '持股2日收益率'
            ]
            
            for col in percentage_columns:
                if col in df.columns:
                    # 如果列是字符串类型且包含%
                    if df[col].dtype == 'object':
                        try:
                            df[col] = pd.to_numeric(df[col].astype(str).str.replace('%', ''), errors='coerce') / 100
                            print(f"已转换列 '{col}' 从百分比字符串到数值")
                        except Exception as e:
                            print(f"转换列 '{col}' 时出错: {e}")
            
            # 处理收益率列
            if not pd.api.types.is_numeric_dtype(df[self.return_col]):
                try:
                    if df[self.return_col].dtype == 'object':
                        df[self.return_col] = df[self.return_col].str.replace('%', '')
                    df[self.return_col] = pd.to_numeric(df[self.return_col], errors='coerce')
                    print(f"收益率列 {self.return_col} 转换为数值型")
                except:
                    print(f"警告：无法将 {self.return_col} 转换为数值型")
            
            # 确保日期列正确处理
            if '信号日期' in df.columns:
                try:
                    df['信号日期'] = pd.to_datetime(df['信号日期'], errors='coerce')
                except:
                    print("警告：无法转换信号日期列")
            
            # 删除缺失值
            original_len = len(df)
            df = df.dropna(subset=[self.return_col] + self.factors)
            print(f"数据预处理完成，分析使用 {len(df)} 行有效数据 (删除了 {original_len - len(df)} 行缺失值)")
            
            self.processed_data = df
            return True
            
        except Exception as e:
            print(f"数据预处理失败: {e}")
            return False
    
    def calculate_comprehensive_metrics(self, factor_col):
        """计算综合指标"""
        df_clean = self.processed_data.dropna(subset=[factor_col, self.return_col])
        
        if len(df_clean) < 10:
            print(f"警告: 因子 {factor_col} 有效数据不足")
            return None
        
        try:
            # 计算分组收益（10等分）
            n_groups = 10
            df_clean['分组'] = pd.qcut(df_clean[factor_col], q=n_groups, labels=False, duplicates='drop')
            
            # 计算每组的统计指标
            group_stats = []
            total_samples = len(df_clean)
            
            for group_id in range(n_groups):
                group_data = df_clean[df_clean['分组'] == group_id]
                
                if len(group_data) == 0:
                    continue
                
                # 获取该组的因子值范围
                factor_values = group_data[factor_col]
                min_val = factor_values.min()
                max_val = factor_values.max()
                param_range = f"[{min_val:.3f}, {max_val:.3f}]"
                
                # 计算该组的收益统计
                returns = group_data[self.return_col]
                avg_return = returns.mean()
                return_std = returns.std()
                win_rate = (returns > 0).mean()
                
                # 计算最大回撤
                cumulative_returns = (1 + returns).cumprod()
                running_max = cumulative_returns.expanding().max()
                drawdown = (cumulative_returns - running_max) / running_max
                max_drawdown = drawdown.min()
                
                # 自适应年化指标计算
                try:
                    # 修复：传递正确的参数格式（字典而不是Series）
                    avg_returns_dict = {
                        '平均收益': avg_return,
                        '收益标准差': return_std
                    }
                    # 获取数据特征用于自适应年化计算
                    data_characteristics = {
                        'total_trades': len(group_data),
                        'actual_annual_trades': len(group_data),  # 使用组内数据作为估算
                        'avg_trade_interval': 30,  # 默认30天
                        'observation_period_years': len(group_data) / 252,  # 估算观测期
                        'holding_period_days': 2,  # 修正：持股天数应该是2
                        'trade_frequency_category': '低频'
                    }
                    # 已删除复杂的自适应年化计算，使用简单的252日年化
                    annualized_return = avg_return * 252
                    annualized_std = return_std * np.sqrt(252)
                    adaptive_results = {
                        'base_frequency': 252,
                        'main_annual_return': annualized_return,
                        'annual_std': annualized_std
                    }
                    
                    # 选择主选年化收益率
                    annualized_return = adaptive_results['main_annual_return']
                    annualized_std = adaptive_results['annual_std']
                    
                except Exception as e:
                    print(f"自适应年化计算失败，使用备用方法: {e}")
                    # 备用：使用传统252日年化
                    annualized_return = avg_return * 252
                    annualized_std = return_std * np.sqrt(252)
                
                group_stats.append({
                    '分组': group_id + 1,
                    '参数区间': param_range,
                    '平均收益': avg_return,
                    '收益标准差': return_std,
                    '胜率': win_rate,
                    '最大回撤': max_drawdown,
                    '年化收益率': annualized_return,
                    '年化收益标准差': annualized_std,
                    '样本数量': len(group_data)
                })
            
            if not group_stats:
                return None
            
            group_stats_df = pd.DataFrame(group_stats)
            
            # 计算年化夏普比率和索提诺比率
            sharpe_ratios = []
            sortino_ratios = []
            
            for _, row in group_stats_df.iterrows():
                if row['收益标准差'] > 0:
                    sharpe = row['年化收益率'] / row['收益标准差']
                    sharpe_ratios.append(sharpe)
                    
                    # 计算下行标准差和索提诺比率
                    group_data = df_clean[df_clean['分组'] == row['分组'] - 1][self.return_col]
                    downside_returns = group_data[group_data < 0]
                    if len(downside_returns) > 0:
                        try:
                            # 使用自适应年化计算系统的年化因子
                            downside_std_dict = {'下行收益标准差': downside_returns.std()}
                            # 获取数据特征用于自适应年化计算
                            data_characteristics = {
                                'total_trades': len(group_data),
                                'actual_annual_trades': len(group_data),  # 使用组内数据作为估算
                                'avg_trade_interval': 30,  # 默认30天
                                'observation_period_years': len(group_data) / 252,  # 估算观测期
                                'holding_period_days': 2,  # 修正为合理的持股天数
                                'trade_frequency_category': '低频'
                            }
                            # 选择年化方法
                            # 已删除复杂的自适应年化计算，使用简单的252日年化
                            sqrt_annualization_factor = np.sqrt(252)
                            downside_std = downside_returns.std() * sqrt_annualization_factor
                            sortino = row['年化收益率'] / downside_std if downside_std > 0 else 0
                        except Exception as e:
                            print(f"自适应年化计算失败，使用备用方法: {e}")
                            # 备用：使用传统252日年化
                            downside_std = downside_returns.std() * np.sqrt(252)
                            sortino = row['年化收益率'] / downside_std if downside_std > 0 else 0
                    else:
                        sortino = np.inf if row['年化收益率'] > 0 else 0
                    sortino_ratios.append(sortino)
                else:
                    sharpe_ratios.append(0)
                    sortino_ratios.append(0)
            
            group_stats_df['年化夏普比率'] = sharpe_ratios
            group_stats_df['年化索提诺比率'] = sortino_ratios
            
            # 计算多空收益（最高组 - 最低组）
            long_short_return = group_stats_df['年化收益率'].max() - group_stats_df['年化收益率'].min()
            
            return {
                'group_stats': group_stats_df,
                'long_short_return': long_short_return,
                'total_samples': total_samples,
                'factor_col': factor_col
            }
            
        except Exception as e:
            print(f"计算因子 {factor_col} 综合指标时出错: {e}")
            return None
    
    def calculate_ic(self, factor_col, use_pearson=False):
        """计算信息系数IC"""
        if not hasattr(self, 'processed_data'):
            df_clean = self.data.dropna(subset=[factor_col, self.return_col])
        else:
            df_clean = self.processed_data.dropna(subset=[factor_col, self.return_col])
        
        if len(df_clean) < 2:
            return np.nan, np.nan, np.nan, np.nan
        
        try:
            # 计算相关系数
            if use_pearson:
                ic = df_clean[factor_col].corr(df_clean[self.return_col])
            else:
                ic = df_clean[factor_col].corr(df_clean[self.return_col], method='spearman')
            
            # 计算IC的均值和标准差（使用滚动窗口）
            window_size = min(30, len(df_clean) // 3)
            if window_size < 5:
                return ic, np.nan, np.nan, np.nan
            
            rolling_ic = []
            for i in range(window_size, len(df_clean)):
                subset = df_clean.iloc[i-window_size:i]
                if use_pearson:
                    corr = subset[factor_col].corr(subset[self.return_col])
                else:
                    corr = subset[factor_col].corr(subset[self.return_col], method='spearman')
                if not np.isnan(corr):
                    rolling_ic.append(corr)
            
            if len(rolling_ic) < 2:
                return ic, np.nan, np.nan, np.nan
            
            ic_mean = np.mean(rolling_ic)
            ic_std = np.std(rolling_ic)
            
            # 计算t统计量和p值
            if ic_std > 0:
                t_stat = ic_mean / (ic_std / np.sqrt(len(rolling_ic)))
                try:
                    from scipy.stats import t
                    p_value = 2 * (1 - t.cdf(abs(t_stat), len(rolling_ic) - 1))
                except:
                    p_value = np.nan
            else:
                t_stat = np.nan
                p_value = np.nan
            
            return ic_mean, ic_std, t_stat, p_value
        
        except Exception as e:
            print(f"计算IC时出错: {e}")
            return np.nan, np.nan, np.nan, np.nan
    
    def score_factors(self, factor_results):
        """对因子进行综合评分"""
        all_scores = []  # 存储所有参数区间的评分
        
        for factor, results in factor_results.items():
            group_stats = results['group_stats']
            
            # 对每个参数区间进行单独评分
            for _, group in group_stats.iterrows():
                param_range = group['参数区间']
                win_rate = group['胜率']
                max_drawdown = group['最大回撤'] 
                ann_return = group['年化收益率']
                ann_std = group['年化收益标准差']
                sharpe_ratio = group['年化夏普比率']
                
                # 计算各项指标得分（1-10分）
                
                # 1. 胜率得分（越高越好）
                if win_rate >= 0.7:
                    win_score = 10
                elif win_rate >= 0.6:
                    win_score = 8
                elif win_rate >= 0.5:
                    win_score = 6
                elif win_rate >= 0.4:
                    win_score = 4
                else:
                    win_score = 2
                
                # 2. 最大回撤得分（越小越好，负值越大越好）
                if max_drawdown >= 0:  # 没有回撤或轻微回撤
                    drawdown_score = 10
                elif max_drawdown >= -0.05:  # 回撤在-5%以内
                    drawdown_score = 8
                elif max_drawdown >= -0.1:   # 回撤在-10%以内
                    drawdown_score = 6
                elif max_drawdown >= -0.2:   # 回撤在-20%以内
                    drawdown_score = 4
                else:
                    drawdown_score = 2
                
                # 3. 年化收益率得分
                if ann_return >= 2.0:  # 年化收益率200%以上
                    return_score = 10
                elif ann_return >= 1.0:  # 年化收益率100%以上
                    return_score = 8
                elif ann_return >= 0.5:  # 年化收益率50%以上
                    return_score = 6
                elif ann_return >= 0:    # 正收益率
                    return_score = 4
                else:                    # 负收益率
                    return_score = 2
                
                # 4. 年化收益标准差得分（风险控制，越低越好）
                if ann_std <= 0.5:   # 标准差50%以下（低风险）
                    std_score = 10
                elif ann_std <= 1.0: # 标准差100%以下（中等风险）
                    std_score = 8
                elif ann_std <= 2.0: # 标准差200%以下（高风险）
                    std_score = 6
                elif ann_std <= 3.0: # 标准差300%以下（极高风险）
                    std_score = 4
                else:
                    std_score = 2
                
                # 5. 年化夏普比率得分（综合收益风险比）
                if sharpe_ratio >= 3.0:   # 夏普比率3以上（优秀）
                    sharpe_score = 10
                elif sharpe_ratio >= 2.0: # 夏普比率2以上（良好）
                    sharpe_score = 8
                elif sharpe_ratio >= 1.0: # 夏普比率1以上（一般）
                    sharpe_score = 6
                elif sharpe_ratio >= 0:   # 正夏普比率
                    sharpe_score = 4
                else:                      # 负夏普比率
                    sharpe_score = 2
                
                # 综合得分（加权平均）
                # 胜率30% + 年化收益率25% + 年化夏普比率25% + 风险控制10% + 最大回撤10%
                total_score = (win_score * 0.3 + return_score * 0.25 + 
                              sharpe_score * 0.25 + std_score * 0.1 + 
                              drawdown_score * 0.1)
                
                # 判定因子方向
                factor_direction = "正向" if ann_return >= 0 else "负向"
                
                all_scores.append({
                    '因子名称': factor,
                    '参数区间': param_range,
                    '胜率': win_rate,
                    '最大回撤': max_drawdown,
                    '年化收益率': ann_return,
                    '年化收益标准差': ann_std,
                    '年化夏普比率': sharpe_ratio,
                    '因子方向': factor_direction,
                    '综合得分': total_score,
                    '胜率得分': win_score,
                    '收益率得分': return_score,
                    '夏普得分': sharpe_score,
                    '风险得分': std_score,
                    '回撤得分': drawdown_score
                })
        
        return pd.DataFrame(all_scores)
    
    def generate_parameterized_report(self):
        """生成带参数因子的详细TXT报告（基于新评分体系）"""
        print("开始生成带参数因子综合分析报告...")
        
        # 分析所有因子（包括带参数和不带参数的）
        factor_results = {}
        
        for factor in self.factor_list:
            print(f"分析因子: {factor}")
            results = self.calculate_comprehensive_metrics(factor)
            if results:
                factor_results[factor] = results
        
        if not factor_results:
            print("错误: 没有有效的带参数因子分析结果")
            return None
        
        # 因子评分（基于新的5个指标）
        scores_df = self.score_factors(factor_results)
        
        # 生成TXT报告
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f'带参数因子综合分析报告_{timestamp}.txt'
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            # 报告头部
            f.write("=" * 80 + "\n")
            f.write("              带参数因子综合分析详细报告                \n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"数据文件: 创业板单日下跌14%详细交易日数据（清理后）1114.xlsx\n")
            f.write(f"总因子数量: {len(self.factor_list)}\n")
            f.write(f"有效分析因子: {len(factor_results)}\n")
            f.write(f"分析指标: 胜率、最大回撤、年化收益率、年化收益标准差、年化夏普比率\n")
            f.write(f"评分体系: 每个参数区间作为独立单元进行评分\n\n")
            
            # 1. 参数区间排行榜
            f.write("1. 参数区间排行榜\n")
            f.write("=" * 50 + "\n\n")
            
            # 分离正向和负向因子
            positive_factors = scores_df[scores_df['因子方向'] == '正向'].sort_values('综合得分', ascending=False)
            negative_factors = scores_df[scores_df['因子方向'] == '负向'].sort_values('综合得分', ascending=False)
            
            # 正向参数区间排行榜
            f.write("【正向参数区间排行榜】\n")
            f.write("=" * 40 + "\n")
            f.write(f"{'排名':<4} {'因子名称':<20} {'参数区间':<15} {'得分':<6} {'评级':<6} {'胜率':<6} {'年化收益':<8} {'夏普比率':<8} {'最大回撤':<8}\n")
            f.write("-" * 90 + "\n")
            
            for i, (_, row) in enumerate(positive_factors.iterrows(), 1):
                rating = 'A+' if row['综合得分'] >= 9 else 'A' if row['综合得分'] >= 8 else 'B+' if row['综合得分'] >= 7 else 'B' if row['综合得分'] >= 6 else 'C'
                f.write(f"{i:<4} {row['因子名称']:<20} {row['参数区间']:<15} {row['综合得分']:<6.1f} {rating:<6} {row['胜率']:<6.1%} {row['年化收益率']:<8.3f} {row['年化夏普比率']:<8.3f} {row['最大回撤']:<8.1%}\n")
            
            if len(positive_factors) > 0:
                best_positive = positive_factors.iloc[0]
                f.write(f"\n最佳正向参数区间: {best_positive['因子名称']} {best_positive['参数区间']} (排名第1)\n\n")
            
            # 负向参数区间排行榜
            f.write("【负向参数区间排行榜】\n")
            f.write("=" * 40 + "\n")
            f.write(f"{'排名':<4} {'因子名称':<20} {'参数区间':<15} {'得分':<6} {'评级':<6} {'胜率':<6} {'年化收益':<8} {'夏普比率':<8} {'最大回撤':<8}\n")
            f.write("-" * 90 + "\n")
            
            for i, (_, row) in enumerate(negative_factors.iterrows(), 1):
                rating = 'A+' if row['综合得分'] >= 9 else 'A' if row['综合得分'] >= 8 else 'B+' if row['综合得分'] >= 7 else 'B' if row['综合得分'] >= 6 else 'C'
                f.write(f"{i:<4} {row['因子名称']:<20} {row['参数区间']:<15} {row['综合得分']:<6.1f} {rating:<6} {row['胜率']:<6.1%} {row['年化收益率']:<8.3f} {row['年化夏普比率']:<8.3f} {row['最大回撤']:<8.1%}\n")
            
            if len(negative_factors) > 0:
                best_negative = negative_factors.iloc[0]
                f.write(f"\n最佳负向参数区间: {best_negative['因子名称']} {best_negative['参数区间']} (排名第1)\n\n")
            
            # 2. 最优秀参数区间推荐
            f.write("2. 最优秀参数区间推荐\n")
            f.write("=" * 50 + "\n\n")
            
            # 选出最优秀的5个正向参数区间和5个负向参数区间
            top_5_positive = positive_factors.head(5)
            top_5_negative = negative_factors.head(5)
            
            f.write("【最优秀的5个正向参数区间】\n")
            f.write("-" * 40 + "\n\n")
            
            for i, (_, factor) in enumerate(top_5_positive.iterrows(), 1):
                f.write(f"第{i}名: {factor['因子名称']} {factor['参数区间']}\n")
                f.write(f"综合得分: {factor['综合得分']:.1f}/10\n")
                f.write(f"胜率: {factor['胜率']:.1%}\n")
                f.write(f"年化收益率: {factor['年化收益率']:.3f}\n")
                f.write(f"年化收益标准差: {factor['年化收益标准差']:.3f}\n")
                f.write(f"年化夏普比率: {factor['年化夏普比率']:.3f}\n")
                f.write(f"最大回撤: {factor['最大回撤']:.1%}\n\n")
            
            if len(top_5_negative) > 0:
                f.write("【最优秀的5个负向参数区间】\n")
                f.write("-" * 40 + "\n\n")
                
                for i, (_, factor) in enumerate(top_5_negative.iterrows(), 1):
                    f.write(f"第{i}名: {factor['因子名称']} {factor['参数区间']}\n")
                    f.write(f"综合得分: {factor['综合得分']:.1f}/10\n")
                    f.write(f"胜率: {factor['胜率']:.1%}\n")
                    f.write(f"年化收益率: {factor['年化收益率']:.3f}\n")
                    f.write(f"年化收益标准差: {factor['年化收益标准差']:.3f}\n")
                    f.write(f"年化夏普比率: {factor['年化夏普比率']:.3f}\n")
                    f.write(f"最大回撤: {factor['最大回撤']:.1%}\n\n")
            
            # 3. 详细参数区间分析
            f.write("3. 详细参数区间分析\n")
            f.write("=" * 50 + "\n\n")
            
            # 按综合得分排序，显示所有参数区间
            all_factors_sorted = scores_df.sort_values('综合得分', ascending=False)
            
            for _, factor_row in all_factors_sorted.iterrows():
                f.write(f"【{factor_row['因子名称']} {factor_row['参数区间']}】\n")
                f.write("-" * 60 + "\n")
                
                # 基本信息
                f.write(f"综合得分: {factor_row['综合得分']:.1f}/10\n")
                f.write(f"因子方向: {factor_row['因子方向']}\n")
                
                # 评级
                if factor_row['综合得分'] >= 9:
                    rating = "A级（优秀）"
                elif factor_row['综合得分'] >= 8:
                    rating = "B+级（良好）"
                elif factor_row['综合得分'] >= 6:
                    rating = "B级（一般）"
                else:
                    rating = "C级（较差）"
                f.write(f"综合评级: {rating}\n")
                
                # 核心指标
                f.write(f"核心指标:\n")
                f.write(f"• 胜率: {factor_row['胜率']:.1%}\n")
                f.write(f"• 年化收益率: {factor_row['年化收益率']:.3f}\n")
                f.write(f"• 年化收益标准差: {factor_row['年化收益标准差']:.3f}\n")
                f.write(f"• 年化夏普比率: {factor_row['年化夏普比率']:.3f}\n")
                f.write(f"• 最大回撤: {factor_row['最大回撤']:.1%}\n\n")
                
                # 分组详细数据
                factor_name = factor_row['因子名称']
                if factor_name in factor_results:
                    group_stats = factor_results[factor_name]['group_stats']
                    param_range = factor_row['参数区间']
                    
                    # 找到对应的分组数据
                    group_data = group_stats[group_stats['参数区间'] == param_range]
                    if len(group_data) > 0:
                        group = group_data.iloc[0]
                        f.write("分组详细数据:\n")
                        f.write(f"• 平均收益: {group['平均收益']:.3f}\n")
                        f.write(f"• 收益标准差: {group['收益标准差']:.3f}\n")
                        f.write(f"• 胜率: {group['胜率']:.1%}\n")
                        f.write(f"• 最大回撤: {group['最大回撤']:.1%}\n")
                        f.write(f"• 年化收益率: {group['年化收益率']:.3f}\n")
                        f.write(f"• 年化收益标准差: {group['年化收益标准差']:.3f}\n")
                        f.write(f"• 年化夏普比率: {group['年化夏普比率']:.3f}\n")
                
                f.write("=" * 60 + "\n\n")
            
            # 4. 投资策略建议
            f.write("4. 投资策略建议\n")
            f.write("=" * 50 + "\n\n")
            
            if len(top_5_positive) > 0:
                f.write("推荐参数区间配置:\n")
                f.write("-" * 30 + "\n")
                
                for i, (_, factor) in enumerate(top_5_positive.iterrows(), 1):
                    weight = 0.25 - i * 0.03  # 递减权重
                    f.write(f"第{i}名 {factor['因子名称']} {factor['参数区间']}: {weight*100:.0f}% 权重\n")
                
                if len(top_5_negative) > 0:
                    f.write("\n可选负向参数区间配置:\n")
                    for i, (_, factor) in enumerate(top_5_negative.iterrows(), 1):
                        weight = 0.1 - i * 0.01  # 较小权重
                        f.write(f"第{i}名 {factor['因子名称']} {factor['参数区间']}: {weight*100:.0f}% 权重\n")
                
                f.write(f"\n策略说明:\n")
                f.write("• 重点配置排名前5的正向参数区间\n")
                f.write("• 可选择性配置负向参数区间作为对冲\n")
                f.write("• 每个参数区间独立考虑收益风险特征\n")
                f.write("• 根据实际参数区间效果动态调整权重\n")
                f.write("• 定期重新评估参数区间有效性\n")
                f.write("• 严格控制单个参数区间仓位风险\n")
            
            # 5. 风险提示
            f.write("\n5. 风险提示\n")
            f.write("=" * 50 + "\n\n")
            f.write("• 历史表现不代表未来收益\n")
            f.write("• 带参数因子有效性可能随市场环境变化\n")
            f.write("• 参数区间设置需要谨慎验证\n")
            f.write("• 建议结合其他分析方法使用\n")
            f.write("• 注意分散投资，控制总体风险\n")
            f.write("• 每个参数区间需独立监控其表现\n")
        
        print(f"带参数因子综合分析报告已保存到 '{report_filename}'")
        
        # 保存详细数据CSV
        csv_filename = f'带参数因子分析数据_{timestamp}.csv'
        scores_df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        print(f"详细数据已保存到 '{csv_filename}'")
        
        # 保存各因子分组数据，保留3位小数
        for factor_name, results in factor_results.items():
            factor_csv = f'带参数因子详细分析_{factor_name}_{timestamp}.csv'
            
            # 创建格式化后的DataFrame副本，保留3位小数
            formatted_group_stats = results['group_stats'].copy()
            
            # 对数值列格式化，保留3位小数
            numeric_columns = ['平均收益', '收益标准差', '胜率', '最大回撤', 
                             '年化收益率', '年化收益标准差', '年化夏普比率', '年化索提诺比率']
            for col in numeric_columns:
                if col in formatted_group_stats.columns:
                    formatted_group_stats[col] = formatted_group_stats[col].round(3)
            
            formatted_group_stats.to_csv(factor_csv, index=False, encoding='utf-8-sig')
        
        return report_filename

# 主函数示例
def main():
    """主函数"""
    # 初始化日志记录器
    logger = Logger()
    sys.stdout = logger  # 重定向输出到日志记录器
    
    print("因子分析程序启动")
    
    # 创建因子分析对象
    analyzer = FactorAnalysis()
    
    # 加载数据
    if not analyzer.load_data():
        print("数据加载失败，程序退出")
        logger.close()  # 关闭日志记录器
        return
    
    # 预处理数据
    print("\n=== 数据预处理 ===")
    
    # 使用Spearman相关系数
    use_pearson = False
    
    # 使用标准处理方式
    process_factors = True
    factor_method = 'standardize'
    winsorize = True
    
    # 执行数据预处理
    if not analyzer.preprocess_data(process_factors=process_factors, factor_method=factor_method, winsorize=winsorize):
        print("数据预处理失败，程序退出")
        logger.close()  # 关闭日志记录器
        return
    
    # 显示可用的因子列表
    print("\n=== 因子分析选项 ===")
    print("\n可用的因子列表:")
    for i, factor in enumerate(analyzer.factors, 1):
        print(f"{i}. {factor}")
    
    # 执行全因子分析
    print("\n执行全因子分析...")
    try:
        analyzer.run_factor_analysis(use_pearson=use_pearson)
        
        # 生成汇总报告
        if hasattr(analyzer, 'analysis_results') and analyzer.analysis_results:
            summary_df = analyzer.generate_summary_report()
            # 生成TXT格式的详细分析报告
            analyzer.generate_factor_analysis_report(summary_df, process_factors=process_factors, 
                                                    factor_method=factor_method, winsorize=winsorize)
        else:
            print("分析结果为空，无法生成报告")
    except Exception as e:
        print(f"执行全因子分析时出错: {str(e)}")
    
    # 自动对所有因子进行分析
    print("\n开始对所有因子执行10等分因子分析...")
    
    # 选择所有因子进行分析
    selected_factors = analyzer.factors.copy()
    valid_indices = list(range(1, len(analyzer.factors) + 1))
            
    # 为选择的因子运行分析
    for factor_name in selected_factors:
        print(f"\n=== 分析因子: {factor_name} ===")
        
        try:
            # 计算IC
            ic_mean, ic_std, t_stat, p_value, _ = analyzer.calculate_ic(factor_name, use_pearson=use_pearson)
            
            # 计算分组收益
            group_results = analyzer.calculate_group_returns(factor_name, n_groups=10)
            
            if group_results:
                # 从返回的字典中获取avg_returns和long_short_return
                avg_returns = group_results['avg_returns']
                long_short_return = group_results['long_short_return'] if not np.isnan(group_results['long_short_return']) else 0
                ir = ic_mean / ic_std if ic_std != 0 else np.nan
                
                # 保存结果到analysis_results中，以便生成报告
                analyzer.analysis_results[factor_name] = {
                    'ic_mean': ic_mean,
                    'ic_std': ic_std,
                    'ir': ir,
                    't_stat': t_stat,
                    'p_value': p_value,
                    'group_results': group_results
                }
                
                # 打印分析结果
                print(f"IC均值: {ic_mean:.4f}")
                print(f"IC标准差: {ic_std:.4f}")
                print(f"信息比率: {ir:.4f}" if not np.isnan(ir) else "信息比率: N/A")
                print(f"多空收益: {long_short_return:.4f}%")
                print("\n10等分分组收益:")
                print(avg_returns.to_string(index=False, float_format='%.3f'))
                
                # 注意：分组收益详细数据将由带参数因子分析器统一生成
                print(f"  因子 {factor_name} 的详细分组收益数据将由带参数因子分析器生成")
            else:
                print(f"无法计算因子 '{factor_name}' 的分组收益")
                continue
            
        except Exception as e:
            print(f"分析因子 '{factor_name}' 时出错: {str(e)}")
    
    # 汇总分析结果
    print("\n=== 因子分析结果已保存 ===")
    
    # ================================
    # 新增：带参数因子综合分析报告
    # ================================
    print("\n开始生成带参数因子综合分析报告...")
    
    try:
        # 创建带参数因子分析器
        parameterized_analyzer = ParameterizedFactorAnalyzer(analyzer.data.copy())
        
        # 预处理数据
        if parameterized_analyzer.preprocess_data():
            # 生成带参数因子TXT报告
            report_filename = parameterized_analyzer.generate_parameterized_report()
            
            if report_filename:
                print(f"[OK] 带参数因子综合分析报告已生成: {report_filename}")
                print("该报告包含以下内容：")
                print("  • 因子排行榜（正向和负向因子分别排名）")
                print("  • 最优秀因子推荐（3个最优秀的正向和负向因子）")
                print("  • 详细因子分析（每个因子的完整指标分析）")
                print("  • 分组详细数据（每个因子的10等分分组表现）")
                print("  • 投资策略建议（基于因子表现的组合配置建议）")
                print("  • 风险提示（使用注意事项）")
                print("\n同时生成的CSV文件：")
                print("  • 带参数因子分析数据_[时间戳].csv（综合评分数据）")
                print("  • 带参数因子详细分析_[因子名称]_[时间戳].csv（各因子分组数据）")
            else:
                print("[ERROR] 带参数因子综合分析报告生成失败")
        else:
            print("[ERROR] 带参数因子数据预处理失败")
            
    except Exception as e:
        print(f"生成带参数因子综合分析报告时出错: {str(e)}")
    
    print("\n因子分析程序已完成")
    
    # 关闭日志记录器
    logger.close()

if __name__ == "__main__":
    main()
