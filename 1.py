import pandas as pd
from scipy import stats

# 1. 载入原始数据
df = pd.read_stata('patent_classes.dta')

# 2. 【核心逻辑】在全局层面锁定每个类别的属性，确保 166/60/106/48/118 准确无误
# 根据论文定义：
# - Emigre Class: 1920-1970年间有德国或奥地利移民专利 (uspat_ger + uspat_aus > 0)
# - Dismissed Class: 1933年前有被解雇科学家专利 (dispat_ger + dispat_aus > 0)
# 注意：论文中的"German"包括德国和奥地利移民
class_traits = df.groupby('main').agg({
    'uspat_ger_2070': 'max',
    'uspat_aus_2070': 'max',
    'dispat_ger_2032': 'max',
    'dispat_aus_2032': 'max'
}).reset_index()

# 修正：需要同时计算德国+奥地利的专利
class_traits['has_emigre'] = (class_traits['uspat_ger_2070'] + class_traits['uspat_aus_2070']) > 0
class_traits['has_dismissed'] = (class_traits['dispat_ger_2032'] + class_traits['dispat_aus_2032']) > 0

col2_mains = class_traits[class_traits['has_emigre'] == True]['main'].unique()
col3_mains = class_traits[class_traits['has_emigre'] == False]['main'].unique()
col4_mains = class_traits[class_traits['has_dismissed'] == True]['main'].unique()
col5_mains = class_traits[class_traits['has_dismissed'] == False]['main'].unique()

# 3. 筛选 5 个列对应的 DataFrame
dfs = [
    df,                                  # (1) All
    df[df['main'].isin(col2_mains)],     # (2) w/ Emigre
    df[df['main'].isin(col3_mains)],     # (3) w/o Emigre
    df[df['main'].isin(col4_mains)],     # (4) w/ Dismissed
    df[df['main'].isin(col5_mains)]      # (5) w/o Dismissed
]

col_names = [
    "All classes",
    "Classes with 1920–1970 patents by US émigrés",
    "Classes without 1920–1970 patents by US émigrés",
    "Classes with pre-1933 patents by dismissed",
    "Classes without pre-1933 patents by dismissed"
]

# 4. 计算所有行指标
rows = []
for d in dfs:
    d_32 = d[d['gyear'] == 1932]
    rows.append({
        'total_pat': d['count_us'].sum(),
        'n_class': d['main'].nunique(),
        'age_32': d_32['class_age'].mean(),
        'age_vals': d_32['class_age'].dropna(),
        'for_32': d_32['count_for'].mean(),
        'for_vals': d_32['count_for'].dropna(),
        'mean_20_70': d['count_us'].mean(),
        'mean_20_32': d[d['gyear'] < 1933]['count_us'].mean(),
        'mean_33_70': d[d['gyear'] >= 1933]['count_us'].mean()
    })

# 5. 格式化输出 (1:1 还原截图布局)
final_data = []

# 第一板块
final_data.append(["Patents by US inventors 1920–1970"] + [f"{r['total_pat']:,}" for r in rows])
final_data.append(["Number of classes"] + [r['n_class'] for r in rows])

# 第二板块: 1932 特征
final_data.append(["Mean class age in 1932"] + [round(r['age_32'], 2) for r in rows])
# P-value Age (2vs3 and 4vs5)
p_age_23 = round(stats.ttest_ind(rows[1]['age_vals'], rows[2]['age_vals'])[1], 3)
p_age_45 = round(stats.ttest_ind(rows[3]['age_vals'], rows[4]['age_vals'])[1], 3)
final_data.append(["  p-value of equality of means test"] + ["", p_age_23, "", p_age_45, ""])

final_data.append(["Mean number of foreign patents in 1932"] + [round(r['for_32'], 2) for r in rows])
# P-value Foreign
p_for_23 = round(stats.ttest_ind(rows[1]['for_vals'], rows[2]['for_vals'])[1], 3)
p_for_45 = round(stats.ttest_ind(rows[3]['for_vals'], rows[4]['for_vals'])[1], 3)
final_data.append(["  p-value of equality of means test"] + ["", p_for_23, "", p_for_45, ""])

# 第三板块: 均值产出
final_data.append(["Mean patents per class and year 1920–1970"] + [round(r['mean_20_70'], 2) for r in rows])
final_data.append(["Mean patents per class and year 1920–1932"] + [round(r['mean_20_32'], 2) for r in rows])
final_data.append(["Mean patents per class and year 1933–1970"] + [round(r['mean_33_70'], 2) for r in rows])

# 6. 生成 DataFrame 并导出 Excel
full_headers = ["Variable"] + [f"({i+1}) {name}" for i, name in enumerate(col_names)]
result_table = pd.DataFrame(final_data, columns=full_headers)

result_table.to_excel("Table1_Final_Replication.xlsx", index=False)
print("表格已完美生成！请查看 Table1_Final_Replication.xlsx")
print(result_table.iloc[:2, :]) # 打印前两行核对 2,073,771 和 166