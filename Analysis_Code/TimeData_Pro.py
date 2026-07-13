import os
import pandas as pd
import re
from pathlib import Path
from collections import defaultdict

# 기본 경로 설정
base_dir = Path("TimeData")  # Main 폴더가 현재 스크립트 위치와 동일한 경로에 있어야 함

# 저장 구조
data_structure = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
valid_conditions = ["Controller_Direct", "Controller_Raycast", "Hand_Direct", "Real", "Wrist"]

# 디렉토리 순회 및 데이터 수집
for root, _, files in os.walk(base_dir):
    for file in files:
        match = re.match(r"Player_\d+_(Keyboard|Tangram|Videoplayer)_(.+)\.txt", file)
        if match:
            task, condition = match.groups()
            if condition not in valid_conditions:
                continue

            dir_match = re.search(r"results_(\d+)", root)
            if not dir_match:
                continue
            dir_idx = f"results_{dir_match.group(1)}"

            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            numeric_values = []
            for line in lines:
                try:
                    val = float(line.strip())
                    numeric_values.append(val)
                except ValueError:
                    continue

            data_structure[task][condition][dir_idx] = numeric_values

# 엑셀 파일 저장 (조건별 시트 + Summary)
for task, condition_data in data_structure.items():
    save_path = os.path.join(base_dir,f"{task}_TimeData.xlsx")
    summary_dict = {}

    with pd.ExcelWriter(save_path, engine="openpyxl") as writer:
        for condition, dir_data in condition_data.items():
            all_dirs = sorted(dir_data.keys(), key=lambda x: int(x.split('_')[1]))
            max_len = max(len(v) for v in dir_data.values())
            df = pd.DataFrame()

            for dir_idx in all_dirs:
                col = dir_data[dir_idx]
                padded = col + [None] * (max_len - len(col))
                df[dir_idx] = padded

            df.to_excel(writer, sheet_name=condition[:31], index=False)

            # 행 단위 평균 계산 (skipna=True)
            row_means = df.mean(axis=1, skipna=True)
            summary_dict[condition] = row_means

        # Summary 시트 작성
        summary_df = pd.DataFrame(summary_dict)
        summary_df.to_excel(writer, sheet_name="Summary", index=False)

    print(f"✅ {save_path} 생성 완료")
