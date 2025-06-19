import os
import math
import pandas as pd

# 1. 输入/输出路径
input_path = '/Users/brianna/Desktop/总体.xlsx'
out_dir    = '/Users/brianna/Desktop/splits'

# 2. 读取 Excel
df = pd.read_excel(input_path)

# 3. Strip 所有列名
df.columns = df.columns.map(lambda x: str(x).strip())

# 4. 重命名 Unnamed:0 为 序号，Unnamed:3 为 摘要
rename_map = {}
if 'Unnamed: 0' in df.columns:
    rename_map['Unnamed: 0'] = '序号'
if 'Unnamed: 3' in df.columns:
    rename_map['Unnamed: 3'] = '摘要'
df = df.rename(columns=rename_map)

# 5. 强制将 序号 转为数值，解析失败置为 NaN，并丢弃这些行
df['序号'] = pd.to_numeric(df['序号'], errors='coerce')
df = df.dropna(subset=['序号'])
df['序号'] = df['序号'].astype(int)

# 6. 确保 摘要 列存在
if '摘要' not in df.columns:
    raise KeyError("未找到名为 '摘要' 的列，请检查实际列名。")

# 7. 只保留 序号 和 摘要 列
df = df[['序号', '摘要']]

# 8. 创建输出目录
os.makedirs(out_dir, exist_ok=True)

# 9. 每 100 行拆分并保存
chunk_size = 100
total_rows = len(df)
num_chunks = math.ceil(total_rows / chunk_size)

for i in range(num_chunks):
    start_idx = i * chunk_size
    end_idx   = min(start_idx + chunk_size, total_rows)

    chunk = df.iloc[start_idx:end_idx]
    start_seq = int(chunk['序号'].min())
    end_seq   = int(chunk['序号'].max())
    filename  = f"{start_seq}-{end_seq}.xlsx"
    output_path = os.path.join(out_dir, filename)

    chunk.to_excel(output_path, index=False)
    print(f"Saved {output_path} ({start_idx+1}-{end_idx} rows)")
