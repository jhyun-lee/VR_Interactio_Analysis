import pandas as pd
import os
from scipy.stats import shapiro

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
df_grouped = df_cleaned.groupby(['way of working', 'Evaluation factors']).mean(numeric_only=True).reset_index()

shapiro_results = []
evaluation_factors = ['Embodiment', 'Immersion', 'Agency']

for factor in evaluation_factors:
    subset = df_grouped[df_grouped['Evaluation factors'] == factor]
    for idx, row in subset.iterrows():
        group_name = f"{row['way of working']} - {row['Evaluation factors']}"
        scores = row.iloc[2:].values
        scores = scores[~pd.isnull(scores)]

        stat, p_value = shapiro(scores)
        normality = 'yes' if p_value > 0.05 else 'No'

        shapiro_results.append({
            'way of working': row['way of working'],
            'Evaluation factors': row['Evaluation factors'],
            'Statistic': stat,
            'p-value': p_value,
            'normalization': normality
        })

shapiro_df = pd.DataFrame(shapiro_results)
print("Shapiro-Wilk Test 완료")

save_mode = 'a' if os.path.exists(output_file) else 'w'
with pd.ExcelWriter(output_file, mode=save_mode, engine='openpyxl') as writer:
    df_grouped.to_excel(writer, sheet_name=f'{Type_name}_df_grouped', index=False)
    shapiro_df.to_excel(writer, sheet_name=f'{Type_name}_Shapiro-Wilk', index=False)