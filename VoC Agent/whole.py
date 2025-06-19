import pandas as pd

# 读取文件和两个 Sheet
excel_path = "/Users/brianna/Desktop/海底捞舆情数据样本.2025.xlsx"
full_df = pd.read_excel(excel_path, sheet_name="全部数据")
dedup_df = pd.read_excel(excel_path, sheet_name="去重数据")

# 清洗列名
dedup_df.columns = dedup_df.columns.str.strip()
full_df.columns = full_df.columns.str.strip()

# 主键
key_column = "序号"

# 自动识别标签列
label_keywords = ["口味", "服务", "资讯", "宣传", "信心"]
label_columns = [col for col in dedup_df.columns if any(k in col for k in label_keywords)]
print("识别到的标签列：", label_columns)

# 为避免 _x/_y 后缀，先删除 full_df 中可能已有的同名标签列
full_df = full_df.drop(columns=[col for col in full_df.columns if col in label_columns], errors='ignore')

# 合并：默认会将新列添加在末尾
merged_df = full_df.merge(
    dedup_df[[key_column] + label_columns],
    on=key_column,
    how="left"
)

# 不做列顺序调整，直接保存
merged_df.to_excel("完整版_已加标签.xlsx", index=False)
print("✅ 完成！标签已添加至末尾，文件已保存为 '完整版_已加标签.xlsx'")
