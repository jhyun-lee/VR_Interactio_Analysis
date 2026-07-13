import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statannotations.Annotator import Annotator
import os

# ===================== 설정 =====================
Type_name = "UI"
file_path = f"VR_Interactions_Analysis_{Type_name}_Results.xlsx"
output_path = f"{Type_name}_Grouped_Boxplot.png"

if Type_name == "Keyboard":
    Name = "Keyboard Typing"
elif Type_name == "object":
    Name = "Object Interaction"
elif Type_name == "UI":
    Name = "UI Controls"

# ===================== 데이터 불러오기 =====================
df_scores = pd.read_excel(file_path, sheet_name=f"{Type_name}_df_grouped")
df_posthoc = pd.read_excel(file_path, sheet_name=f"{Type_name}_Posthoc_Wilcoxon")

# ===================== 데이터 전처리 =====================
score_columns = df_scores.columns[2:]
df_long = df_scores.melt(id_vars=["way of working", "Evaluation factors"],
                         value_vars=score_columns,
                         var_name="Participant", value_name="Score").dropna()

# 순서 고정
factors = ["Agency", "Embodiment", "Immersion"]
df_long = df_long[df_long["Evaluation factors"].isin(factors)]
df_long["Evaluation factors"] = pd.Categorical(df_long["Evaluation factors"], categories=factors, ordered=True)

work_order = sorted(df_long["way of working"].unique())
df_long["way of working"] = pd.Categorical(df_long["way of working"], categories=work_order, ordered=True)

# ===================== 시각화 =====================
plt.figure(figsize=(8, 10))
sns.set(style="whitegrid", font_scale=1.2)

ax = sns.boxplot(data=df_long,
                 x="way of working",
                 y="Score",
                 hue="Evaluation factors",
                 palette="Set2",
                 dodge=True)

ax.set_ylim(0, 7.5)
ax.set_xlabel("") 
ax.set_ylabel("Score", fontsize=14, weight="bold")
ax.set_xlabel("Interaction Method", fontsize=14, weight="bold")
ax.set_xticklabels(["0", "1", "2", "3"])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# ===================== 사후분석 주석 생성 =====================
pairs = []
pvals = []

for factor in factors:
    df_posthoc_sub = df_posthoc[(df_posthoc["Evaluation factors"] == factor) &
                                (df_posthoc["Significant"] == "유의")]
    for _, row in df_posthoc_sub.iterrows():
        w1, w2 = row["Comparison"].split(" vs ")
        pairs.append(((w1.strip(), factor), (w2.strip(), factor)))
        pvals.append(row["corrected p-value"])

# ===================== 주석 적용 =====================
if pairs:
    annotator = Annotator(ax, pairs=pairs, data=df_long,
                          x="way of working", y="Score", hue="Evaluation factors")
    annotator.configure(
        test=None,
        text_format='star',
        loc='inside',
        line_offset_to_group=10,  # 주석 라벨과 박스 사이 거리
        line_height=0.005,           # 주석 라인 높이 간격
    )


    annotator.set_pvalues(pvals)
    annotator.annotate()

# ===================== 저장 =====================
plt.title(f"{Name} – Comparison of All Factors", fontsize=18, weight="bold")
plt.tight_layout()
plt.savefig(output_path, dpi=300, bbox_inches="tight")
print(f"✅ 저장 완료: {output_path}")
