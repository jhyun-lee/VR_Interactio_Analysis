import pandas as pd
import numpy as np
import os
from scipy.stats import friedmanchisquare
import statsmodels.api as sm
from statsmodels.stats.anova import AnovaRM
import openpyxl

# 엑셀 파일
file_path = "VR_Interactions_Python.xlsx"

Type_name= "UI"
output_file = f"VR_Interactions_Analysis_{Type_name}_Results.xlsx"

if Type_name=="Keyboard":
    sheet_name = "키보드타이핑"
elif Type_name=="object":
    sheet_name = "오브젝트상호작용"
elif Type_name=="UI":
    sheet_name = "UI컨트롤"
    
# 2'키보드타이핑' 시트 읽기
df = pd.read_excel(file_path, sheet_name=sheet_name)




df['way of working'].ffill(inplace=True)
df['Evaluation factors'].ffill(inplace=True)

# 참가자 점수만 숫자로 변환
df_scores = df.drop(['way of working', 'Evaluation factors'], axis=1)
df_scores = df_scores.apply(pd.to_numeric, errors='coerce')

# way_of_working, evaluation_factors 컬럼 붙이기
df_cleaned = pd.concat([df[['way of working', 'Evaluation factors']], df_scores], axis=1)


# df_cleaned에서 long format으로 변환
df_long = df_cleaned.melt(id_vars=['way of working', 'Evaluation factors'],
                          var_name='Participant',
                          value_name='Score')

# 결과 저장 리스트
analysis_results = []

# Shapiro-Wilk 결과 불러오기
shapiro_df = pd.read_excel(output_file, sheet_name=f'{Type_name}_Shapiro-Wilk')

# Friedman Test & RM-ANOVA 루프
evaluation_factors = ['Embodiment', 'Immersion', 'Agency']


for factor in evaluation_factors:
    # 분석할 데이터만 추출
    sub_df = df_long[df_long['Evaluation factors'] == factor]
    
    print(sub_df)
    # Shapiro-Wilk에서 그룹별로 확인
    for group_name in sub_df['way of working'].unique():
        normality_row = shapiro_df[
            (shapiro_df['way of working'] == group_name) &
            (shapiro_df['Evaluation factors'] == factor)
        ]


        if normality_row.empty:
            print(f"{group_name} - {factor} 그룹에 대한 Shapiro-Wilk Test 결과가 없어 넘어갑니다.")
            continue
        
        normality = normality_row['normalization'].values[0]
        group_data = sub_df[sub_df['way of working'] == group_name]
        
        # 참가자별로 pivot
        pivot_df = sub_df.pivot_table(index='Participant',
                                      columns='way of working',
                                      values='Score')
        
        # NaN 제거
        pivot_df = pivot_df.dropna()
        
        if pivot_df.shape[0] < 2:
            print(f"{group_name} - {factor}는 데이터가 부족하여 분석에서 제외됩니다.")
            continue
        
        if normality == 'yes':
            try:
                # Repeated Measures ANOVA
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
                print(f"{group_name} - {factor} RM-ANOVA 실행 오류: {e}")
        else:
            try:
                # Friedman Test
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
                print(f"{group_name} - {factor} Friedman Test 실행 오류: {e}")

#결과 DataFrame으로 저장
analysis_df = pd.DataFrame(analysis_results)

print("조건 평가 분석 완료!")
print(analysis_df)

sheet_name = f'{Type_name}_Condition Evaluation'
book = openpyxl.load_workbook(output_file)

# 시트가 이미 있으면 삭제
if sheet_name in book.sheetnames:
    std = book[sheet_name]
    book.remove(std)
    book.save(output_file)



save_mode = 'a' if os.path.exists(output_file) else 'w'


# pandas로 저장
with pd.ExcelWriter(output_file, mode=save_mode, engine='openpyxl') as writer:
    analysis_df.to_excel(writer, sheet_name=sheet_name, index=False)