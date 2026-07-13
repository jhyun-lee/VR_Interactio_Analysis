import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statannotations.Annotator import Annotator
import os

# ===================== 설정 =====================
Type_name = "UI"
file_path = f"VR_Interactions_Analysis_{Type_name}_Results.xlsx"

if Type_name == "Keyboard":
    Name = "Keyboard Typing"
elif Type_name == "object":
    Name = "Object Interaction"
elif Type_name == "UI":
    Name = "UI Controls"

# ===================== 데이터 불러오기 =====================
df_scores = pd.read_excel(file_path, sheet_name=f"{Type_name}_df_grouped")
df_posthoc = pd.read_excel(file_path, sheet_name=f"{Type_name}_Posthoc_Wilcoxon")

# ===================== 폴더 =====================
output_dir = f"{Type_name}_boxplot_posthoc_annotated"
os.makedirs(output_dir, exist_ok=True)



# ===================== 시각화 반복 =====================
for factor in df_scores["Evaluation factors"].unique():
    df_sub = df_scores[df_scores["Evaluation factors"] == factor].copy()

    save_path = os.path.join(output_dir, f"{Type_name}_{factor}_boxplot.png")

    # 참가자 점수만 추출
    score_columns = df_sub.columns[2:]
    df_long = df_sub.melt(id_vars=["way of working", "Evaluation factors"],
                          value_vars=score_columns,
                          var_name="Participant", value_name="Score").dropna()

    if df_long.empty:
        continue

    # 카테고리 순서를 강제 설정 (고정된 4개 순서로)
    work_order = df_long["way of working"].unique().tolist()
    work_order.sort()
    df_long["way of working"] = pd.Categorical(df_long["way of working"], categories=work_order, ordered=True)

    # 사후분석 결과에서 유의한 비교쌍만 추출
    df_posthoc_sub = df_posthoc[(df_posthoc["Evaluation factors"] == factor) & 
                                (df_posthoc["Significant"] == "유의")]

    pairs = []
    pvals = []
    for _, row in df_posthoc_sub.iterrows():
        w1, w2 = row["Comparison"].split(" vs ")
        pairs.append((w1.strip(), w2.strip()))
        pvals.append(row["corrected p-value"])

    # ===================== 박스플롯 =====================
    plt.figure(figsize=(8, 9))
    sns.set(style="whitegrid", font_scale=1.2)
    custom_palette = ["#8FBAC8", "#F4A259", "#90BE6D", "#F28482"]

    ax = sns.boxplot(data=df_long, x="way of working", y="Score",
                    hue="way of working", palette=custom_palette,
                    dodge=False, legend=False)

    ax.set_ylabel("Score", fontsize=15, weight="bold")
    ax.set_ylim(0, 7.5)
    ax.set_xticks(range(4))
    ax.set_xticklabels(["0", "1", "2", "3"], ha='right')

    ax.set_xlabel("") 
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # 사후분석 주석 (내부)
    if pairs:
        annotator = Annotator(ax, pairs=pairs, data=df_long, x="way of working", y="Score")
        annotator.configure(test=None, text_format='star', loc='inside')
        annotator.set_pvalues(pvals)
        annotator.annotate()

    plt.figtext(0.5, 0.98, f"{Name} – {factor} - boxPlot", ha="center", fontsize=18, weight="bold")
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
print(f"\n📊 모든 박스플롯 이미지 저장 완료 경로: {output_dir}")
