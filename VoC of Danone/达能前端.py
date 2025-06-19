import streamlit as st
import pandas as pd
import requests
import os
import json
import concurrent.futures
from io import BytesIO

# Streamlit 页面标题
st.title("达能VOC-负面情绪检测")

# 文件上传
uploaded_file = st.file_uploader("上传一个 Excel 文件", type=["xlsx"])

# 定义 Kofe API 的主机地址和API密钥
HOST = 'https://www.kofe.ai'
api_key = 'app-KY29NI4S296SLlBkLeHZ5nap'

def upload_json(json_str, user):
    upload_url = f"{HOST}/v1/files/upload"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "user": user,
        "type": "JSON",
        "content": json_str
    }
    
    try:
        response = requests.post(upload_url, headers=headers, json=data)
        response.raise_for_status()
        return response.json().get("id")
    except Exception as e:
        st.error(f"JSON 上传失败: {str(e)}")
        return None

def run_workflow(json_data, user, response_mode="blocking"):
    workflow_url = f"{HOST}/v1/workflows/run"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "inputs": {
                "json_input": json_data
        },
        "response_mode": response_mode,
        "user": user
    }

    try:
        response = requests.post(workflow_url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"工作流执行失败: {str(e)}")
        return None

def process_batch(batch_data, user):
    json_data = json.dumps({"data": batch_data}, ensure_ascii=False)
    if json_data:
        return run_workflow(json_data, user)
    return None

if uploaded_file is not None:
    # 初始化进度条
    progress_bar = st.progress(0)
    progress_text = st.empty()

    # 读取 Excel 文件
    df = pd.read_excel(uploaded_file)
    total_input_texts = len(df)
    st.write(f"输入文件中的文本内容数: {total_input_texts}")

    # 提取第一列数据
    first_column_data = df.iloc[:, 0]
    
    # 每30行分组并准备任务
    user = "difyuser"
    tasks = [(first_column_data[i:i+30].tolist(), user) for i in range(0, len(first_column_data), 30)]

    # 并发处理任务
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_batch = {executor.submit(process_batch, batch, user): batch for batch, user in tasks}
        total_tasks = len(tasks)
        for i, future in enumerate(concurrent.futures.as_completed(future_to_batch), start=1):
            result = future.result()
            if result:
                results.append(result)
            progress_percentage = i / total_tasks
            progress_bar.progress(progress_percentage)
            progress_text.write(f"进度: {i}/{total_tasks} 批次已完成")

    # 提取并处理结果
    if results:
        extracted_data = []
        for result in results:
            outputs = result.get('data', {}).get('outputs', {})
            for key in ['negative', 'other']:
                if outputs.get(key):  # 确保 key 存在且不为 None
                    parsed_json = json.loads(outputs[key].strip('```json\n'))
                    for item in parsed_json:
                        extracted_data.append({
                            'text': item.get('text', ''),
                            'score': item.get('score', ''),
                            'reason': item.get('reason', '')
                        })

        # 创建 DataFrame
        final_df = pd.DataFrame(extracted_data)

        # 统计输出内容数
        total_output_texts = len(final_df)
        st.write(f"输出文件中的消极情绪数: {total_output_texts}")

        # # 在页面展示输出文件内容（转换为 HTML 表格）
        # st.write("输出文件内容:")
        # st.dataframe(final_df)
        

        # 使用内存中的 BytesIO 缓存文件数据
        output_buffer = BytesIO()
        final_df.to_excel(output_buffer, index=False, engine='openpyxl')
        output_buffer.seek(0)

        # 提供下载链接
        st.success("所有批次处理完成！")
        st.download_button(
            label="下载结果",
            data=output_buffer,
            file_name="final_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # 在页面展示输出文件内容（转换为 HTML 表格）
        st.write("输出文件内容:")
        html_table = final_df.to_html(index=False, escape=False)
        st.markdown(html_table, unsafe_allow_html=True)
