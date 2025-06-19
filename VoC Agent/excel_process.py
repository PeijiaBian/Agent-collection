import pandas as pd

# Read the Excel file
df = pd.read_excel('/Users/brianna/Desktop/海底捞200数据.xlsx')

# Extract the '摘要' column, drop missing values, and convert to a list of strings
abstracts = df['摘要'].dropna().astype(str).tolist()

# Group every 20 items into a single string
grouped = []
for i in range(0, len(abstracts), 20):
    group = abstracts[i:i+20]
    # Join the 20 items into one string, separated by newline
    grouped.append('\n'.join(group))

# 'grouped' is now a list of strings, each containing 20 entries from '摘要'
print(grouped)
