import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load the n=6 summary data
df = pd.read_excel("temperature_exp_analysis_n=6.xlsx", sheet_name="mean_sd")
# The 'mean_sd' sheet has columns: Temperature, TVBN_mean, TVBN_std, Sample

plt.rcParams['font.family'] = 'Arial'
sns.set_style("white")
colors = {'pork': '#E69F00', 'beef': '#D55E00', 'chicken': '#499BC0'}

fig, ax = plt.subplots(figsize=(14, 9.5))
for meat in df['Sample'].unique():
    subset = df[df['Sample'] == meat].sort_values('Temperature')
    x = subset['Temperature'].values
    y = subset['TVBN_mean'].values
    yerr = subset['TVBN_std'].values
    ax.plot(x, y, color=colors[meat], linewidth=2, label=meat.capitalize())
    ax.scatter(x, y, color=colors[meat], s=80, zorder=5)
    ax.fill_between(x, y - yerr, y + yerr, color=colors[meat], alpha=0.25)

ax.set_xlabel('Temperature (°C)', fontsize=32, fontweight='bold')
ax.set_ylabel('TVB-N (mg/100g)', fontsize=32, fontweight='bold')
ax.set_title('TVB-N of Different Meats', fontsize=40, fontweight='bold', pad=20)
ax.set_xticks(np.arange(15, 41, 5))
ax.set_yticks(np.arange(6, 14, 1))
ax.tick_params(axis='both', which='major', direction='in', length=12, width=2, labelsize=28, pad=12)
ax.spines[['top','right']].set_visible(False)
ax.spines[['left','bottom']].set_linewidth(2)
ax.set_ylim(6, 13.5)
ax.legend(loc='lower left', bbox_to_anchor=(0.02, 0.05), prop={'size': 28})
plt.subplots_adjust(top=0.92, bottom=0.1)
plt.savefig('TVBN_lineplot_bio_replicates.tiff', dpi=300, bbox_inches='tight')
plt.show()
