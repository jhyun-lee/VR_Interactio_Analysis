import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ============ 설정 ============ #
Type_name = "UI" # 예시: "Keyboard", "object", "UI"
file_path = "VR_Interactions_Python.xlsx" # 실제 파일 경로

if Type_name == "Keyboard":
    sheet_name = "키보드선호도"
elif Type_name == "object":
    sheet_name = "오브젝트선호도"
elif Type_name == "UI":
    sheet_name = "UI선호도"
else:
    raise ValueError("Invalid Type_name. Must be 'Keyboard', 'object', or 'UI'.")

output_dir = f"Preference_Visualization"
os.makedirs(output_dir, exist_ok=True)

# ============ 데이터 불러오기 및 전처리 ============ #
try:
    df = pd.read_excel(file_path, sheet_name=sheet_name)
except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found. Please check the file path.")
    exit()
except Exception as e:
    print(f"Error reading Excel file: {e}")
    exit()

df_long = df.melt(id_vars=["평가항목", "문항"], var_name="참여자", value_name="입력방식")

method_mapping = {
    "컨트롤러 직접": 0,
    "컨트롤러 레이캐스팅": 1,
    "핸드트래킹": 2,
    "손목회전": 3
}

df_long["입력방식_mapped"] = df_long["입력방식"].map(method_mapping)

if df_long["입력방식_mapped"].isnull().any():
    unmapped_values = df_long[df_long["입력방식_mapped"].isnull()]["입력방식"].unique()
    print(f"Warning: Some '입력방식' values were not mapped: {unmapped_values}. They will be excluded from the visualization.")
    df_long = df_long.dropna(subset=["입력방식_mapped"])

method_df = pd.crosstab(df_long["문항"], df_long["입력방식_mapped"])


method_percent = method_df.div(method_df.sum(axis=1), axis=0) * 100
method_percent = method_percent[::-1].copy()

colors = ["#8FBAC8", "#F4A259", "#90BE6D", "#F28482"]
method_labels = {
    0: "Direct controller",
    1: "Raycasting",
    2: "Hand tracking",
    3: "Wrist rotation"
}

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False 

fig, ax = plt.subplots(figsize=(10, 8))


num_questions = len(method_percent)
y_pos = range(num_questions)

bottoms = [0] * num_questions 

# 시각화
for idx, col in enumerate(method_percent.columns):
    ax.barh(y_pos, method_percent[col].values, left=bottoms, color=colors[idx], label=method_labels[col])
    bottoms = [i + j for i, j in zip(bottoms, method_percent[col].values)]

# 퍼센트 텍스트 표시
for i, row in enumerate(method_percent.values):
    left = 0
    for j, val in enumerate(row):
        if val > 5: 
            ax.text(left + val / 2, y_pos[i], f"{int(val)}%", va="center", ha="center",
                    fontsize=9, weight="bold", color="black") 
        left += val

ax.set_xlabel("Percentage (%)", fontsize=12)
ax.set_title(f"{Type_name} Preferred Input Method by Question (Stacked Bar)", fontsize=16)
ax.set_ylabel("Question", fontsize=12)

# y축 틱 라벨을 문항 이름으로 설정
ax.set_yticks(y_pos)
ax.set_yticklabels(method_percent.index, fontsize=10)

ax.legend(title="Input Method", loc="upper center", bbox_to_anchor=(0.5, -0.08), 
          ncol=4, fontsize=10, title_fontsize=12, frameon=False)
plt.tight_layout()

plt.savefig(os.path.join(output_dir, f"{Type_name}_stacked_method_bar.png"))
plt.close(fig)

print(f"Visualization saved to {os.path.join(output_dir, f'{Type_name}_stacked_method_bar.png')}")



# ============ 문항별 입력방식 개수 저장 ============ #
method_count = pd.crosstab(df_long["문항"], df_long["입력방식_mapped"])

# 컬럼명을 사람이 보기 좋게 method_labels로 변경
method_count.rename(columns=method_labels, inplace=True)

# 파일 저장
excel_save_path = os.path.join(output_dir, f"{Type_name}_method_count_by_question.xlsx")
method_count.to_excel(excel_save_path, index=True)

print(f"Method count saved to {excel_save_path}")