import string
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

def calculate_mean_sd(data,meat_type):
    """same meat, different temperature"""
    data_meat = data[data['Sample'] == f"{meat_type}"].copy()

    data_meat[['Biological_parallelism', 'Technical_parallelism']] = data_meat['ID'].apply(split_by_last_underscore)

    tech_agg = (
        data_meat.groupby(["Temperature", "Biological_parallelism"])
        .agg(
            tech_sd=("TVBN", "sd"),
            tech_count=("TVBN", "count"),
        )
        .reset_index()
    )

    tech_agg["df"] = tech_agg["tech_count"] - 1

    tech_agg["variance_contribution"] = tech_agg["df"] * (
            tech_agg["tech_sd"] ** 2
    )

    pool_sd_df = tech_agg.groupby("Temperature").agg(
        sum_df=("df", "sum"), sum_var_contrib=("variance_contribution", "sum")
    )

    pool_sd_df["pool_sd"] = np.sqrt(
        pool_sd_df["sum_var_contrib"] / pool_sd_df["sum_df"]
    )
    pool_sd_df = pool_sd_df[["pool_sd"]].reset_index()

    data_meat_calculate = data_meat.groupby('Temperature', as_index=False).agg({
        'TVBN': ['mean'],
        'Sample': 'first'
    })
    data_meat_calculate.columns = ['_'.join(filter(None, col)).strip('_')
                                   for col in data_meat_calculate.columns]
    data_meat_calculate = data_meat_calculate.rename(columns={
        'Sample_first': 'Sample'
    })

    data_meat_calculate = pd.merge(
        data_meat_calculate, pool_sd_df, on="Temperature", how="left"
    )

    data_meat_calculate["mean±sd"] = data_meat_calculate['TVBN_mean'].round(3).astype(str)+"±"+pool_sd_df['pool_sd'].round(3).astype(str)

    custom_order = [
        "Sample",
        "Temperature",
        "TVBN_mean",
        "pool_sd",
        "mean±sd"
    ]

    data_meat_calculate = data_meat_calculate[custom_order]

    return data_meat_calculate

def meat_vs_temperature_MWU(data, meat_type):
    """same meat, different temperature, use the Mann-Whitney-U statistic to calculate"""

    data_meat = data[data['Sample'] == f"{meat_type}"].copy()
    data_meat[['Biological_parallelism', 'Technical_parallelism']] = data_meat['ID'].apply(split_by_last_underscore)

    data_meat_bio = (
        data_meat.groupby(["Sample", "Temperature", "Biological_parallelism"])[
            "TVBN"
        ]
        .mean()
        .reset_index()
    )

    group_means = (
        data_meat_bio.groupby("Temperature")["TVBN"]
        .mean()
        .sort_values(ascending=False)
    )
    groups = list(group_means.index.tolist())
    result = []
    for group1, group2 in combinations(groups, 2):
        data1 = data_meat_bio[data_meat_bio['Temperature'] == group1]['TVBN'].values
        data2 = data_meat_bio[data_meat_bio['Temperature'] == group2]['TVBN'].values

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
                'p_value': p_value,
                'Rank_Biserial': round(r_rb,6),
                'Cles': round(cles_interpret,6),
                'direction': direction
            })
        except Exception as e:
            print(e)

    result_df = pd.DataFrame(result)

    # calculate p_adj
    rejected, p_adjusted, _, _ = multipletests(
        result_df["p_value"], alpha=0.05, method="holm"
    )
    result_df["p_adj"] = p_adjusted

    # calculate significant letter
    adj_matrix = {g: {g} for g in groups}
    for idx, row in result_df.iterrows():
        if row["p_adj"] >= 0.05:
            adj_matrix[row["group1"]].add(row["group2"])
            adj_matrix[row["group2"]].add(row["group1"])

    def find_maximal_cliques(nodes, current_clique, potential_nodes, cliques):
        if not potential_nodes and not current_clique == []:
            is_maximal = True
            for c in cliques:
                if set(current_clique).issubset(set(c)):
                    is_maximal = False
                    break
            if is_maximal:
                cliques.append(list(current_clique))
            return

        for node in list(potential_nodes):
            new_clique = current_clique + [node]
            new_potential = [
                n for n in potential_nodes if n in adj_matrix[node] and n != node
            ]
            find_maximal_cliques(nodes, new_clique, new_potential, cliques)
            potential_nodes.remove(node)

    cliques = []
    find_maximal_cliques(groups, [], list(groups), cliques)

    cliques = sorted(cliques, key=lambda x: groups.index(x[0]))

    letters = list(string.ascii_lowercase)
    group_letters_dict = {g: [] for g in groups}

    for i, clique in enumerate(cliques):
        current_letter = letters[i if i < len(letters) else 0]
        for g in clique:
            group_letters_dict[g].append(current_letter)

    letter_mapping = {
        g: "".join(sorted(group_letters_dict[g])) for g in groups
    }

    # add significant letter to result_df
    result_df["group1_letter"] = result_df["group1"].map(letter_mapping)
    result_df["group2_letter"] = result_df["group2"].map(letter_mapping)

    result_df["p_value"] = result_df["p_value"].apply(
        lambda x: f"{x:.4e}" if x < 0.001 else round(x, 4)
    )
    result_df["p_adj"] = result_df["p_adj"].apply(
        lambda x: f"{x:.4e}" if x < 0.001 else round(x, 4)
    )
    result_df["Sample"] = meat_type

    custom_columns = [
        "Sample",
        "group1",
        "group1_letter",
        "group2",
        "group2_letter",
        "U_stat",
        "p_value",
        "p_adj",
        "Rank_Biserial",
        "Cles",
        "direction",
    ]
    result_df = result_df[
        [col for col in custom_columns if col in result_df.columns]
    ]

    result_df = result_df.sort_values(by="group1", ascending=True).reset_index(
        drop=True
    )

    return result_df

def calculate_repeat (data):
    """calculate all repeat data (gather bio and tech repeat together)"""
    df_beef_mean_sd = calculate_mean_sd(data, "beef")
    df_beef_test = meat_vs_temperature_MWU(data,"beef")
    df_pork_mean_sd = calculate_mean_sd(data, "pork")
    df_pork_test = meat_vs_temperature_MWU(data,"pork")
    df_chicken_mean_sd = calculate_mean_sd(data, "chicken")
    df_chicken_test = meat_vs_temperature_MWU(data,"chicken")

    df_result_mean = pd.concat([df_beef_mean_sd,df_pork_mean_sd,df_chicken_mean_sd],axis=0)
    df_result_test = pd.concat([df_beef_test,df_pork_test,df_chicken_test],axis=0)

    return df_result_mean,df_result_test

# ---------------------- 2. main() ------------------------
def main():
    df = pd.read_excel(r"../data/temperature_exp.xlsx")
    # calculate the bio repeat
    df_result_bio_mean, df_result_bio_test = calculate_repeat(df)
    with pd.ExcelWriter(r"../data/temperature_exp_analysis_n=6.xlsx",engine='openpyxl') as writer:
        df.to_excel(writer,sheet_name='original_data',index=False)
        df_result_bio_mean.to_excel(writer, sheet_name='mean_sd', index=False)
        df_result_bio_test.to_excel(writer, sheet_name='test', index=False)

if __name__ == "__main__":
    main()




