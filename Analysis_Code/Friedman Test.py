import pandas as pd
import numpy as np
from scipy.stats import friedmanchisquare
from statsmodels.stats.anova import AnovaRM

data = {
    'way of working': [
        'Controller raycasting interaction',
        'Direct controller interaction',
        'Hand tracking interaction'
    ],
    '1': [4, 5, 3.5],
    '2': [2, 3, 3.5],
    '3': [5, 3.5, 5],
    '4': [5, 5, 4],
    '5': [4, 5, 4.5],
    '6': [4, 3.5, 5],
    '7': [5, 5, 5],
    '8': [3, 5, 4],
    '9': [2.5, 5, 5],
    '10': [3.5, 5, 4.5],
    '11': [1, 5, 4.5],
    '12': [3, 5, 4.5],
    '13': [4.5, 5, 3],
    '14': [5, 4, 5],
    '15': [3, 4.5, 5],
    '16': [1, 3, 5],
    '17': [5, 4.5, 5],
    '18': [2.5, 4, 5],
    '19': [3, 4, 5]
}

df = pd.DataFrame(data)

df_long = df.melt(id_vars=['way of working'], var_name='Participant', value_name='Score')
df_long['Participant'] = df_long['Participant'].astype(int)

pivot = df_long.pivot(index='Participant', columns='way of working', values='Score')

data_for_test = [pivot[col].values for col in pivot.columns]
stat, p_value = friedmanchisquare(*data_for_test)

print("=== Friedman Test ===")
print(f"Statistic: {stat:.4f}, p-value: {p_value:.4f}")

df_long.rename(columns={'way of working': 'way_of_working'}, inplace=True)
aovrm = AnovaRM(df_long, depvar='Score', subject='Participant', within=['way_of_working'])
anova_results = aovrm.fit()

print("\n=== Repeated Measures ANOVA ===")
print(anova_results)
