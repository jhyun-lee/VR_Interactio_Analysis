import pandas as pd
import numpy as np
from scipy.stats import friedmanchisquare
from statsmodels.stats.anova import AnovaRM

# ===============================
# 샘플 데이터 (Agency)
# ===============================
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



#     'Evaluation factors' : ['Agency', 'Agency'],

df = pd.DataFrame(data)

# ===============================
# 데이터 Long Format으로 변환
# ===============================
df_long = df.melt(id_vars=['way of working'], var_name='Participant', value_name='Score')



# 참가자 번호 숫자로 변환
df_long['Participant'] = df_long['Participant'].astype(int)



# ===============================
# Friedman Test (비정규 데이터)
# ===============================
# pivot: 참가자별 각 조건별 점수
pivot = df_long.pivot(index='Participant', columns='way of working', values='Score')

from numpy.random import seed
from numpy.random import randn

data1 = 5 * randn(100) + 50
data2 = 5 * randn(100) + 50
data3 = 5 * randn(100) + 52

print(data1)

print(pivot)


# Friedman Test
data_for_test = [pivot[col].values for col in pivot.columns]
print(data_for_test)

stat, p_value = friedmanchisquare(*data_for_test)





print("=== Friedman Test ===")
print(f"Statistic: {stat:.4f}, p-value: {p_value:.4f}")

# ===============================
# Repeated Measures ANOVA (정규 데이터)
# ===============================
# AnovaRM 데이터: Participant, way of working, Score
aovrm = AnovaRM(df_long, depvar='Score', subject='Participant',
                within=['way of working'])
anova_results = aovrm.fit()

print("\n=== Repeated Measures ANOVA ===")
print(anova_results)
