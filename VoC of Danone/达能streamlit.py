import streamlit as st
import pandas as pd
import requests
import json
import numpy as np

# Streamlit 页面标题
st.title("Excel 数据处理")

# 文件上传
uploaded_file = st.file_uploader("上传 Excel 文件", type=["xlsx"])

if uploaded_file is not None:
    # 读取 Excel 文件
    df = pd.read_excel(uploaded_file)

    # 提取第一列数据
    first_column_data = df.iloc[:, 0].tolist()

    # 每 30 行提取数据并转换为嵌套 JSON 格式
    json_data = []
    for i in range(0, len(first_column_data), 30):
        chunk = first_column_data[i:i + 30]
        json_data.append({"data": chunk})

    # 调用外部 API
    response = requests.post("https://www.kofe.ai/agent", json=json_data)
    processed_data = response.json()

    # 合并数据并输出为 Excel
    output_df = pd.DataFrame(processed_data)
    output_file = "processed_data.xlsx"
    output_df.to_excel(output_file, index=False)

    st.success(f"处理完成，输出文件: {output_file}")