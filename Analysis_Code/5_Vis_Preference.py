import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

Type_name = "UI"
file_path = "VR_Interactions_Python_EN.xlsx"

sheet_name = f"{Type_name}_Preference"

output_dir = f"Preference_Visualization"
os.makedirs(output_dir, exist_ok=True)

try:
    df = pd.read_excel(file_path, sheet_name=sheet_name)
except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found. Please check the file path.")
    exit()
except Exception as e:
    print(f"Error reading Excel file: {e}")
    exit()

# 한글 컬럼이 존재할 경우를 대비해 영문으로 변환 (하위 호환성 유지)
df.rename(columns={"평가항목": "Category", "문항": "Q"}, inplace=True)

df_long = df.melt(id_vars=["Category", "Q"], var_name="Participant", value_name="Input_Method")

method_mapping = {
    "Direct controller interaction": 0,
    "Controller raycasting interaction": 1,
    "Hand tracking interaction": 2,
    "Wrist rotation interaction": 3
}

df_long["Input_Method_mapped"] = df_long["Input_Method"].map(method_mapping)

if df_long["Input_Method_mapped"].isnull().any():
    unmapped_values = df_long[df_long["Input_Method_mapped"].isnull()]["Input_Method"].unique()
    print(f"Warning: Some 'Input_Method' values were not mapped: {unmapped_values}. They will be excluded from the visualization.")
    df_long = df_long.dropna(subset=["Input_Method_mapped"])

method_df = pd.crosstab(df_long["Q"], df_long["Input_Method_mapped"])

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

for idx, col in enumerate(method_percent.columns):
    ax.barh(y_pos, method_percent[col].values, left=bottoms, color=colors[idx], label=method_labels[col])
    bottoms = [i + j for i, j in zip(bottoms, method_percent[col].values)]

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

ax.set_yticks(y_pos)
ax.set_yticklabels(method_percent.index, fontsize=10)

ax.legend(title="Input Method", loc="upper center", bbox_to_anchor=(0.5, -0.08), 
          ncol=4, fontsize=10, title_fontsize=12, frameon=False)
plt.tight_layout()

plt.savefig(os.path.join(output_dir, f"{Type_name}_stacked_method_bar.png"))
plt.close(fig)

print(f"Visualization saved to {os.path.join(output_dir, f'{Type_name}_stacked_method_bar.png')}")

method_count = pd.crosstab(df_long["Q"], df_long["Input_Method_mapped"])
method_count.rename(columns=method_labels, inplace=True)

excel_save_path = os.path.join(output_dir, f"{Type_name}_method_count_by_question.xlsx")
method_count.to_excel(excel_save_path, index=True)

print(f"Method count saved to {excel_save_path}")