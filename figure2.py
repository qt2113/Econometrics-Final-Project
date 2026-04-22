import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 1. 载入数据
df = pd.read_stata('patent_classes.dta')

# 2. 创建分组变量 (与Table 1一致：德国+奥地利)
emigre_counts = df.groupby('main').agg({
    'uspat_ger_2070': 'max',
    'uspat_aus_2070': 'max'
}).reset_index()
emigre_counts['total_emigre'] = emigre_counts['uspat_ger_2070'] + emigre_counts['uspat_aus_2070']

# Figure 2A 分组：1个、2-4个、5+个移民专利
def get_group_f2a(x):
    if x == 0:
        return 'Research fields of other German chemists'
    elif x == 1:
        return 'Emigre fields: 1 emigré patent'
    elif x <= 4:
        return 'Emigre fields: 2-4 emigré patents'
    else:
        return 'Emigre fields: 5+ emigré patents'

emigre_counts['group_f2a'] = emigre_counts['total_emigre'].apply(get_group_f2a)

# 合并分组信息
df = df.merge(emigre_counts[['main', 'group_f2a', 'total_emigre']], on='main', how='left')

# 3. 计算每年每组的平均专利数
trend_f2a = df.groupby(['gyear', 'group_f2a'])['count_us'].mean().unstack()

# 重新排序列顺序
col_order = [
    'Research fields of other German chemists',
    'Emigre fields: 1 emigré patent',
    'Emigre fields: 2-4 emigré patents',
    'Emigre fields: 5+ emigré patents'
]
trend_f2a = trend_f2a[col_order]

# ============================================
# Figure 2A: 两条线 (简单对比: Emigre vs Control)
# ============================================
df['emigre_class'] = (df['uspat_ger_2070'] + df['uspat_aus_2070']) > 0

trend_f2a = df.groupby(['gyear', 'emigre_class'])['count_us'].mean().unstack()
trend_f2a.columns = ['Research fields of other German chemists', 'Research fields of emigrés']

plt.figure(figsize=(10, 6))
plt.plot(trend_f2a.index, trend_f2a['Research fields of other German chemists'], 
        label='Research fields of other German chemists', color='#2E4057', linewidth=2)
plt.plot(trend_f2a.index, trend_f2a['Research fields of emigrés'], 
        label='Research fields of emigrés', color='#D62828', linewidth=2)

plt.axvline(x=1933, color='black', linestyle='--', linewidth=1.5, alpha=0.7)
plt.xlabel('Year', fontsize=12)
plt.ylabel('Average patents per class by US inventors', fontsize=12)
plt.legend(loc='upper left', fontsize=10)
plt.xlim(1920, 1970)
plt.grid(True, alpha=0.3)
plt.title('Figure 2A: US Patents per Class and Year', fontsize=12)
plt.tight_layout()
plt.savefig('Figure2A.png', dpi=150)
plt.close()
print('Figure 2A (2条线) 已保存!')

# ============================================
# Figure 2B: 四条线 (按1个、2-4个、5+个移民专利分组)
# ============================================

# 重新排序列顺序
col_order = [
    'Research fields of other German chemists',
    'Emigre fields: 1 emigré patent',
    'Emigre fields: 2-4 emigré patents',
    'Emigre fields: 5+ emigré patents'
]
trend_f2b = df.groupby(['gyear', 'group_f2a'])['count_us'].mean().unstack()
trend_f2b = trend_f2b[col_order]

plt.figure(figsize=(10, 6))
colors = ['#2E4057', '#048A54', '#FCBF49', '#D62828']
linestyles = ['-', '--', '-.', ':']

for i, col in enumerate(col_order):
    plt.plot(trend_f2b.index, trend_f2b[col], 
            label=col, color=colors[i], linestyle=linestyles[i], linewidth=2)

plt.axvline(x=1933, color='black', linestyle='--', linewidth=1.5, alpha=0.7)
plt.xlabel('Year', fontsize=12)
plt.ylabel('Average patents per class by US inventors', fontsize=12)
plt.legend(loc='upper left', fontsize=9)
plt.xlim(1920, 1970)
plt.grid(True, alpha=0.3)
plt.title('Figure 2B: US Patents per Class and Year by Research Field', fontsize=12)
plt.tight_layout()
plt.savefig('Figure2B.png', dpi=150)
plt.close()
print('Figure 2B (4条线) 已保存!')

# ============================================
# 6. 输出关键数据验证
# ============================================
print('\n=== Figure 2A 关键年份数据验证 ===')
print(trend_f2a.loc[[1920, 1932, 1933, 1970]])

print('\n=== Figure 2B 关键年份数据验证 ===')
print(trend_f2b.loc[[1920, 1932, 1933, 1970]])

print('\n=== 各组类别数量验证 ===')
print(emigre_counts['group_f2a'].value_counts())