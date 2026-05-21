import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ============================================
# 1. 从 Excel 读取数据（第二个工作表 'mean_sd'）
# ============================================
file_path = r"../data/temperature_exp_analysis_n=6.xlsx"
df_raw = pd.read_excel(file_path, sheet_name='mean_sd')

# 重命名列以匹配绘图代码中的变量名
# 原列名: Sample, Temperature, TVBN_mean, pool_sd, mean±sd
df = df_raw.rename(columns={
    'Sample': 'Meat',
    'TVBN_mean': 'TVBN_mean',
    'pool_sd': 'TVBN_pooled sd'
})

# 确保数据类型正确
df['Temperature'] = df['Temperature'].astype(int)
df['TVBN_mean'] = df['TVBN_mean'].astype(float)
df['TVBN_pooled sd'] = df['TVBN_pooled sd'].astype(float)

# ============================================
# 2. 全局设置
# ============================================
plt.rcParams['font.family'] = 'Arial'
sns.set_style("white")

colors = {
    'pork': '#E69F00',
    'beef': '#D55E00',
    'chicken': '#499BC0'
}

# ============================================
# 3. 绘图
# ============================================
fig, ax = plt.subplots(figsize=(14, 9.5))

for meat in df['Meat'].unique():
    subset = df[df['Meat'] == meat].sort_values('Temperature')
    x = subset['Temperature'].values
    y_mean = subset['TVBN_mean'].values
    y_std = subset['TVBN_pooled sd'].values

    ax.plot(x, y_mean, color=colors[meat], linestyle='-', linewidth=2, label=meat.capitalize())
    ax.scatter(x, y_mean, color=colors[meat], marker='o', s=80, zorder=5)
    ax.fill_between(x, y_mean - y_std, y_mean + y_std, color=colors[meat], alpha=0.25)

# ========== 坐标轴标签与标题 ==========
ax.set_xlabel('Temperature (°C)', fontsize=32, fontweight='bold')
ax.set_ylabel('TVB-N (mg/100g)', fontsize=32, fontweight='bold')
ax.set_title('TVB-N of Different Meats', fontsize=40, fontweight='bold', pad=20)

# ========== 均匀的主刻度 ==========
x_major = np.arange(15, 41, 5)        # [15,20,25,30,35,40]
y_major = np.arange(6, 14, 1)         # [6,7,8,9,10,11,12,13]
ax.set_xticks(x_major)
ax.set_yticks(y_major)

# ========== 刻度线设置 ==========
ax.tick_params(axis='both', which='major', direction='in',
               left=True, bottom=True, right=False, top=False,
               length=12, width=2, labelsize=28, pad=12)

# ========== 边框设置 ==========
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_linewidth(2)
ax.spines['bottom'].set_linewidth(2)

# ========== y轴上限留白 ==========
ax.set_ylim(6, 13.5)

# ============================================
# 4. 图例
# ============================================
ax.legend(loc='lower left', bbox_to_anchor=(0.02, 0.05),
          prop={'size': 28}, handlelength=1.8, frameon=True,
          fancybox=True, shadow=True)

# ============================================
# 5. 调整布局
# ============================================
plt.subplots_adjust(top=0.92, bottom=0.1)

# ============================================
# 6. 保存并显示
# ============================================
plt.savefig('TVBN_lineplot_final.tiff', dpi=300, bbox_inches='tight')
plt.show()
