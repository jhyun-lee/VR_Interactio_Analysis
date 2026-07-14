import pandas as pd
import numpy as np
import os
from scipy.stats import friedmanchisquare
from statsmodels.stats.anova import AnovaRM
import openpyxl

file_path = "VR_Interactions_Python_EN.xlsx"
Type_name = "UI"
output_file = f"VR_Interactions_Analysis_{Type_name}_Results.xlsx"

sheet_name = Type_name

df = pd.read_excel(file_path, sheet_name=sheet_name)
df['way of working'].ffill(inplace=True)
df['Evaluation factors'].ffill(inplace=True)

df_scores = df.drop(['way of working', 'Evaluation factors'], axis=1)
df_scores = df_scores.apply(pd.to_numeric, errors='coerce')

df_cleaned = pd.concat([df[['way of working', 'Evaluation factors']], df_scores], axis=1)

df_long = df_cleaned.melt(id_vars=['way of working', 'Evaluation factors'],
                          var_name='Participant',
                          value_name='Score')

analysis_results = []
shapiro_df = pd.read_excel(output_file, sheet_name=f'{Type_name}_Shapiro-Wilk')
evaluation_factors = ['Embodiment', 'Immersion', 'Agency']

for factor in evaluation_factors:
    sub_df = df_long[df_long['Evaluation factors'] == factor]

    for group_name in sub_df['way of working'].unique():
        normality_row = shapiro_df[
            (shapiro_df['way of working'] == group_name) &
            (shapiro_df['Evaluation factors'] == factor)
        ]

        if normality_row.empty:
            continue

        normality = normality_row['normalization'].values[0]
        group_data = sub_df[sub_df['way of working'] == group_name]

        pivot_df = sub_df.pivot_table(index='Participant',
                                      columns='way of working',
                                      values='Score')
        pivot_df = pivot_df.dropna()

        if pivot_df.shape[0] < 2:
            continue

        if normality == 'yes':
            try:
                anova_data = pivot_df.reset_index().melt(id_vars='Participant',
                                                         var_name='way_of_working',
                                                         value_name='Score')
                aovrm = AnovaRM(anova_data, depvar='Score', subject='Participant',
                                within=['way_of_working'])
                result = aovrm.fit()
                f_value = result.anova_table['F Value'][0]
                p_value = result.anova_table['Pr > F'][0]
                significance = 'yes' if p_value < 0.05 else 'no'

                analysis_results.append({
                    'Test': 'Repeated Measures ANOVA',
                    'Evaluation factors': factor,
                    'way of working': group_name,
                    'Statistic': f_value,
                    'p-value': p_value,
                    'Significant': significance
                })
            except Exception as e:
                pass
        else:
            try:
                data_for_test = [pivot_df[col].values for col in pivot_df.columns]
                stat, p_value = friedmanchisquare(*data_for_test)
                significance = 'yes' if p_value < 0.05 else 'no'

                analysis_results.append({
                    'way of working': group_name,
                    'Evaluation factors': factor,
                    'Test': 'Friedman Test',
                    'Statistic': stat,
                    'p-value': p_value,
                    'Significant': significance
                })
            except Exception as e:
                pass

analysis_df = pd.DataFrame(analysis_results)

sheet_name = f'{Type_name}_Condition Evaluation'
book = openpyxl.load_workbook(output_file)

if sheet_name in book.sheetnames:
    std = book[sheet_name]
    book.remove(std)
    book.save(output_file)

save_mode = 'a' if os.path.exists(output_file) else 'w'
with pd.ExcelWriter(output_file, mode=save_mode, engine='openpyxl') as writer:
    analysis_df.to_excel(writer, sheet_name=sheet_name, index=False)