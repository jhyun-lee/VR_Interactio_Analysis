import pandas as pd
from scipy.stats import wilcoxon
from statsmodels.stats.multitest import multipletests
import numpy as np
import os

file_path = "VR_Interactions_Python_EN.xlsx"
Type_name = "UI"
output_file = f"VR_Interactions_Analysis_{Type_name}_Results.xlsx"

sheet_name = Type_name

df = pd.read_excel(file_path, sheet_name=sheet_name)
df['way of working'] = df['way of working'].replace('', np.nan).ffill()
df['Evaluation factors'] = df['Evaluation factors'].replace('', np.nan).ffill()

df_scores = df.drop(['way of working', 'Evaluation factors'], axis=1)
df_scores = df_scores.apply(pd.to_numeric, errors='coerce')

df_cleaned = pd.concat([df[['way of working', 'Evaluation factors']], df_scores], axis=1)
posthoc_results_all = []

def run_posthoc_wilcoxon(evaluation_factor, df_input):
    df_filtered_factor = df_input[df_input['Evaluation factors'] == evaluation_factor]
    ways_of_working = df_filtered_factor['way of working'].unique()
    participant_cols = df_filtered_factor.columns[2:]

    p_values = []
    comparisons = []
    stat_values = []

    for i, way1 in enumerate(ways_of_working):
        for j, way2 in enumerate(ways_of_working):
            if i < j:
                way1_data = df_filtered_factor[df_filtered_factor['way of working'] == way1][participant_cols]
                way2_data = df_filtered_factor[df_filtered_factor['way of working'] == way2][participant_cols]

                way1_scores = pd.Series(way1_data.values.flatten()).dropna()
                way2_scores = pd.Series(way2_data.values.flatten()).dropna()

                n_min = min(len(way1_scores), len(way2_scores))
                if n_min < 3:
                    continue

                way1_scores = way1_scores[:n_min]
                way2_scores = way2_scores[:n_min]

                try:
                    stat, p = wilcoxon(way1_scores, way2_scores, alternative='two-sided', zero_method='wilcox')
                    p_values.append(p)
                    stat_values.append(stat)
                    comparisons.append((way1, way2))
                except Exception as e:
                    pass

    if p_values:
        reject, pvals_corrected, _, _ = multipletests(p_values, alpha=0.05, method='holm')
        for (way1, way2), stat, pval, pval_corr, rej in zip(comparisons, stat_values, p_values, pvals_corrected, reject):
            result = "Significant" if rej else "Not significant"
            posthoc_results_all.append({
                'Evaluation factors': evaluation_factor,
                'Comparison': f"{way1} vs {way2}",
                'Statistic': stat,
                'raw p-value': pval,
                'corrected p-value': pval_corr,
                'Significant': result
            })

for factor in ['Embodiment', 'Immersion', 'Agency']:
    run_posthoc_wilcoxon(factor, df_cleaned)

posthoc_df = pd.DataFrame(posthoc_results_all)
save_mode = 'a' if os.path.exists(output_file) else 'w'

with pd.ExcelWriter(output_file, mode=save_mode, engine='openpyxl') as writer:
    posthoc_df.to_excel(writer, sheet_name=f'{Type_name}_Posthoc_Wilcoxon', index=False)
