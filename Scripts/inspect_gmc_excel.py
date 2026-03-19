import pandas as pd

# Read the GMC Excel file and print columns and row count
df = pd.read_excel('Files to update/Flux Google Merchant Center – Products source.xlsx')
print('Columns:', len(df.columns))
print('Rows:', len(df))
print('Column names:', df.columns.tolist())
