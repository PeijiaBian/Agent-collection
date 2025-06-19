import pandas as pd
import os

def clean_email(cell):
    if pd.isna(cell) or cell == "-":
        return None
    # 分隔多个邮箱地址，只取第一个（支持逗号或分号）
    first_email = str(cell).split(",")[0].split(";")[0].strip()
    # 只保留 163.com 邮箱
    if "163.com" not in first_email.lower():
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

    # 构造输出文件路径
    filename = os.path.basename(file_path)
    dirname = os.path.dirname(file_path)
    cleaned_filename = f"clean_163{filename}"
    output_path = os.path.join(dirname, cleaned_filename)

    # 保存为新的 Excel 文件
    df_cleaned.to_excel(output_path, index=False)
    print(f"清洗完成，保存为: {output_path}")

    return output_path

# 示例调用（替换为你自己的文件路径）
clean_excel_emails("/Users/brianna/Desktop/06.09~06.13/【企查查】企业搜索“人力资源”20250611(0611_129296494)_北京.xlsx")
