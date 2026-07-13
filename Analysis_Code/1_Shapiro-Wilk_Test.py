import pandas as pd
import os
from scipy.stats import shapiro

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
    

# 시트 읽기
df = pd.read_excel(file_path, sheet_name=sheet_name)

# way of working, Evaluation factors 결측값 채우기
df['way of working'].ffill(inplace=True)
df['Evaluation factors'].ffill(inplace=True)

# 참가자 점수만 숫자로 변환
df_scores = df.drop(['way of working', 'Evaluation factors'], axis=1)
df_scores = df_scores.apply(pd.to_numeric, errors='coerce')

# way_of_working, evaluation_factors 컬럼 붙이기
df_cleaned = pd.concat([df[['way of working', 'Evaluation factors']], df_scores], axis=1)

# way_of_working & Evaluation factors 그룹화 → 참가자별 평균점수]
df_grouped = df_cleaned.groupby(['way of working', 'Evaluation factors']).mean(numeric_only=True).reset_index()

print(" 데이터 정리 및 평균점수 계산 완료!")
print(df_grouped)



# 결과 저장 리스트
shapiro_results = []

# Shapiro-Wilk test를 진행할 평가요소 리스트
evaluation_factors = ['Embodiment', 'Immersion', 'Agency']


# 각 그룹별로 정규성 검정
for factor in evaluation_factors:
    subset = df_grouped[df_grouped['Evaluation factors'] == factor]
    
    for idx, row in subset.iterrows():

        group_name = f"{row['way of working']} - {row['Evaluation factors']}"
        scores = row.iloc[2:].values  # 첫 2열은 way of working과 Evaluation factors이므로, 이후부터 참가자 점수
        
        # NaN 제거
        scores = scores[~pd.isnull(scores)]


        print(row)
        print(f"[DEBUG] {group_name} - 점수 벡터: {scores}")
        print(f"[DEBUG] {group_name} - 점수 개수: {len(scores)}")


        print(f"{group_name},   {factor}")
        print(scores)
        # 샤피로-윌크 검정
        stat, p_value = shapiro(scores)
        normality = 'yes' if p_value > 0.05 else 'No'

        shapiro_results.append({
            'way of working'    : row['way of working'],
            'Evaluation factors': row['Evaluation factors'],
            'Statistic'         : stat,
            'p-value'           : p_value,
            'normalization'     : normality
        })

# 결과를 데이터프레임으로 저장
shapiro_df = pd.DataFrame(shapiro_results)

# 확인
print("Shapiro-Wilk Test 완료")
print(shapiro_df)


save_mode = 'a' if os.path.exists(output_file) else 'w'

# 엑셀로 저장
with pd.ExcelWriter(output_file, mode=save_mode, engine='openpyxl') as writer:
    df_grouped.to_excel(writer, sheet_name=f'{Type_name}_df_grouped', index=False)
    shapiro_df.to_excel(writer, sheet_name=f'{Type_name}_Shapiro-Wilk', index=False)