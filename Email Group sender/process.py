import pandas as pd
import os

def clean_email(cell):
    if pd.isna(cell) or cell == "-":
        return None
    # 分隔多个邮箱地址，只取第一个（支持逗号或分号）
    first_email = str(cell).split(",")[0].split(";")[0].strip()
    # 过滤 qq.com 邮箱
    if "qq.com" in first_email.lower():
        return None
    return first_email

def clean_excel_emails(file_path):
    # 读取文件
    df = pd.read_excel(file_path)

    # 尝试识别邮箱列
    email_col = None
    for col in df.columns:
        if "邮箱" in col:
            email_col = col
            break
    if not email_col:
        raise ValueError("未找到包含‘邮箱’的列名。")

    # 清洗邮箱数据
    df[email_col] = df[email_col].apply(clean_email)
    df_cleaned = df.dropna(subset=[email_col])
    df_cleaned = df_cleaned.drop_duplicates(subset=[email_col])

    # 重命名邮箱列为“邮箱地址”
    df_cleaned = df_cleaned.rename(columns={email_col: "邮箱地址"})

    # 确保“企业名称”列存在，且作为第一列
    if "企业名称" not in df_cleaned.columns:
        raise ValueError("未找到‘企业名称’列，请确认原始数据中包含该列。")

    # 添加新行：企业名称为光之舟，邮箱地址为 zheyangli@lightark.ai
    new_row = {col: "" for col in df_cleaned.columns}
    new_row["企业名称"] = "光之舟"
    new_row["邮箱地址"] = "zheyangli@lightark.ai"
    df_cleaned = pd.concat([df_cleaned, pd.DataFrame([new_row])], ignore_index=True)

    # 调整列顺序：将“企业名称”列放到第一列
    cols = list(df_cleaned.columns)
    cols.insert(0, cols.pop(cols.index("企业名称")))
    df_cleaned = df_cleaned[cols]

    # 构造输出路径
    filename = os.path.basename(file_path)
    dirname = os.path.dirname(file_path)
    cleaned_filename = f"clean_{filename}"
    output_path = os.path.join(dirname, cleaned_filename)

    # 保存为 Excel
    df_cleaned.to_excel(output_path, index=False)
    print(f"清洗完成，保存为: {output_path}")

    return output_path

# 示例调用（替换为你自己的文件路径）
clean_excel_emails("/Users/brianna/Desktop/06.09~06.13/【企查查】企业搜索“人力资源”20250611(0611_129297365)_深圳.xlsx")

