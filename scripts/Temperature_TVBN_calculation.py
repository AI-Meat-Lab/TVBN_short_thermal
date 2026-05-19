import pandas as pd
import numpy as np
from scipy import stats
from itertools import combinations
from statsmodels. stats. multitest import multipletests


# ---------------------- 1. Functions ------------------------
def split_by_last_underscore(data):
    last_underscore = data.rfind("_")
    biological_parallelism = data[:last_underscore]
    technological_parallelism = data[last_underscore+1:]
    return pd.Series([biological_parallelism, technological_parallelism]) # assigned to two new columns

def meat_vs_temperature_ttest(data,meat_type):
    """same meat, different temperature, ttest"""
    # data = rawdata_mean.copy()
    # meat_type = "pork"

    data_meat = data[data['Sample'] == f"{meat_type}"].copy()
    data_meat_calculate = data_meat.groupby('Temperature', as_index=False).agg({
        'TVBN': ['mean', 'std'],  # 计算均值、标准差和计数
        'Sample': 'first'  # 保留样本信息
    })
    data_meat_calculate.columns = ['_'.join(filter(None, col)).strip('_')
                                   for col in data_meat_calculate.columns]
    data_meat_calculate["mean±sd"] = data_meat_calculate['TVBN_mean'].round(3).astype(str)+"±"+data_meat_calculate['TVBN_std'].round(3).astype(str)

    # t student
    temp_40 = data_meat[data_meat['Temperature'] == 40]['TVBN'].values
    temp_30 = data_meat[data_meat['Temperature'] == 30]['TVBN'].values
    t_stat, p_value = stats.ttest_ind(temp_30, temp_40, equal_var=False)
    pooled_std = np.sqrt(((len(temp_40) - 1) * np.var(temp_40, ddof=1) +
                          (len(temp_30) - 1) * np.var(temp_30, ddof=1)) /
                         (len(temp_40) + len(temp_30) - 2))
    Cohens_d = (np.mean(temp_30) - np.mean(temp_40)) / pooled_std
    data_meat_calculate = data_meat_calculate.assign(
        t_stat=t_stat,
        p_value=p_value,
        Cohens_d=Cohens_d
    )

    return data_meat_calculate

def calculate_mean_sd(data,meat_type):
    """same meat, different temperature"""
    # data = df.copy()
    # meat_type = "pork"

    data_meat = data[data['Sample'] == f"{meat_type}"].copy()
    data_meat_calculate = data_meat.groupby('Temperature', as_index=False).agg({
        'TVBN': ['mean', 'std'],  # 计算均值、标准差和计数
        'Sample': 'first'  # 保留样本信息
    })
    data_meat_calculate.columns = ['_'.join(filter(None, col)).strip('_')
                                   for col in data_meat_calculate.columns]
    data_meat_calculate = data_meat_calculate.rename(columns={
        'Sample_first': 'Sample'
    })
    data_meat_calculate["mean±sd"] = data_meat_calculate['TVBN_mean'].round(3).astype(str)+"±"+data_meat_calculate['TVBN_std'].round(3).astype(str)

    return data_meat_calculate

def meat_vs_temperature_MWU(data, meat_type):
    """same meat, different temperature, use the Mann-Whitney-U statistic to calculate"""
    # data = df.copy()
    # meat_type = "beef"

    data_meat = data[data['Sample'] == f"{meat_type}"].copy()

    groups = data_meat["Temperature"].unique()
    result = []
    for group1, group2 in combinations(groups, 2):
        data1 = data_meat[data_meat['Temperature'] == group1]['TVBN'].values
        data2 = data_meat[data_meat['Temperature'] == group2]['TVBN'].values

        # Mann-Whitney U test
        try:
            u_stat, p_value = stats.mannwhitneyu(data1, data2, alternative='two-sided')

            # calculate effect size
            n1, n2 = len(data1), len(data2)
            r_rb = 1 - (2 * u_stat) / (n1 * n2)
            cles = u_stat / (n1 * n2)
            if cles < 0.5:
                cles_interpret = 1 - cles
                direction = f"{group2} > {group1}"
            else:
                cles_interpret = cles
                direction = f"{group1} > {group2}"

            result.append({
                'group1': group1,
                'group2': group2,
                'U_stat': round(u_stat,6),
                # 'p_value': round(p_value,6),
                'p_value': p_value,
                'Rank_Biserial': round(r_rb,6),
                'Cles': round(cles_interpret,6),
                'direction': direction
            })
        except Exception as e:
            print(e)

    result_df = pd.DataFrame(result)
    # if not result_df.empty:
    #     m = len(result_df)
    #     result_df["p_adj"] = result_df['p_value'] * m
    #     result_df["p_adj"] = result_df['p_adj'].apply(lambda x: min(x,1.0)) # 将p值限制在0-1之间，如果值>1，则按照1计算
    result_df["Sample"] = meat_type

    return result_df

def calculate_all_repeat (data):
    """calculate all repeat data (gather bio and tech repeat together)"""
    df_beef_mean_sd = calculate_mean_sd(data, "beef")
    df_beef_test = meat_vs_temperature_MWU(data,"beef")
    df_pork_mean_sd = calculate_mean_sd(data, "pork")
    df_pork_test = meat_vs_temperature_MWU(data,"pork")
    df_chicken_mean_sd = calculate_mean_sd(data, "chicken")
    df_chicken_test = meat_vs_temperature_MWU(data,"chicken")

    df_result_mean = pd.concat([df_beef_mean_sd,df_pork_mean_sd,df_chicken_mean_sd],axis=0)
    df_result_test = pd.concat([df_beef_test,df_pork_test,df_chicken_test],axis=0)

    # p_adj
    reject, p_adj, _, _ = multipletests(pvals=df_result_test['p_value'].values, alpha=0.05, method='fdr_bh')
    df_result_test['p_adj_fdr'] = p_adj

    return df_result_mean,df_result_test


def calculate_bio_repeat(data):
    """calculate the mean of technical repeat first, then calculate the mean and test of bio repeat"""
    data[['Biological_parallelism','Technical_parallelism']] = data['ID'].apply(split_by_last_underscore)
    data_bio_mean = data.groupby('Biological_parallelism', as_index=False).agg({
        'TVBN': ['mean'],  # 计算均值、标准差和计数
        'Sample': 'first',  # 保留样本信息
        'Temperature': 'first'
    })
    data_bio_mean.columns = ['_'.join(filter(None, col)).strip('_')
                                   for col in data_bio_mean.columns]
    data_bio_mean = data_bio_mean.rename(columns={
        'TVBN_mean': 'TVBN',
        'Sample_first': 'Sample',
        'Temperature_first': 'Temperature'
    })

    df_beef_mean_sd = calculate_mean_sd(data_bio_mean, "beef")
    df_beef_test = meat_vs_temperature_MWU(data_bio_mean, "beef")
    df_pork_mean_sd = calculate_mean_sd(data_bio_mean, "pork")
    df_pork_test = meat_vs_temperature_MWU(data_bio_mean, "pork")
    df_chicken_mean_sd = calculate_mean_sd(data_bio_mean, "chicken")
    df_chicken_test = meat_vs_temperature_MWU(data_bio_mean, "chicken")

    df_result_bio_mean = pd.concat([df_beef_mean_sd, df_pork_mean_sd, df_chicken_mean_sd], axis=0)
    df_result_bio_test = pd.concat([df_beef_test, df_pork_test, df_chicken_test], axis=0)

    # p_adj
    reject, p_adj, _, _ = multipletests(pvals=df_result_bio_test['p_value'].values, alpha=0.05, method='fdr_bh')
    df_result_bio_test['p_adj_fdr'] = p_adj

    return df_result_bio_mean, df_result_bio_test


# ---------------------- 2. main() ------------------------
def main():
    df = pd.read_excel(r"temperature_exp.xlsx")
    # calculate all repeat
    df_result_all_mean,df_result_all_test = calculate_all_repeat(df)
    # calculate the bio repeat
    df_result_bio_mean, df_result_bio_test = calculate_bio_repeat(df)
    with pd.ExcelWriter(r"../data/temperature_exp_analysis_n=18.xlsx",engine='openpyxl') as writer:
        df.to_excel(writer,sheet_name='original_data',index=False)
        df_result_all_mean.to_excel(writer, sheet_name='mean_sd', index=False)
        df_result_all_test.to_excel(writer, sheet_name='test', index=False)
    with pd.ExcelWriter(r"../data/temperature_exp_analysis_n=6.xlsx",engine='openpyxl') as writer:
        df.to_excel(writer,sheet_name='original_data',index=False)
        df_result_bio_mean.to_excel(writer, sheet_name='mean_sd', index=False)
        df_result_bio_test.to_excel(writer, sheet_name='test', index=False)

if __name__ == "__main__":
    main()




