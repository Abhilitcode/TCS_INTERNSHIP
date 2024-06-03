from PyPDF2 import PdfReader
from tabula import read_pdf
# from tabulate import tabulate
import pandas as pd
import json
import streamlit as st
# import numpy as np

# my_bool = bool(1)  # or just bool


def highlight(row):
    if row['Status'] == "Match":
        return ['background-color: lightgreen']*len(row)
    elif row['Status'] == "Not Match":
        return ['background-color: tomato']*len(row)
    else:
        return ['']*len(row)
    
def delete_null_columns(data_frame):
    cnp = data_frame.isnull().mean()
    
    columns_to_drop = cnp[cnp > 0.5].index
    data_frame.drop(columns = columns_to_drop, inplace = True)
    
    return data_frame

def delete_null_rows(data_frame):
    rnp = data_frame.isnull().mean(axis = 1)
    
    rows_to_drop = rnp[rnp > 0.5].index
    data_frame.drop(index = rows_to_drop, inplace = True)
    
    return data_frame

def preprocess(data_frame):
    data_frame.dropna(axis = 0, how = 'all', inplace = True)
    data_frame.dropna(axis = 1, how = 'all', inplace = True)
    
    data_frame = delete_null_columns(data_frame)
    data_frame = delete_null_rows(data_frame)
    
    return data_frame

def compare(pdf_file, excel_file):
    df = read_pdf(pdf_file, pages = 'all')
    
    for n, (data, sheet) in enumerate(zip(df, excel_file.sheet_names)):
        data = preprocess(data)
        
        json_string = data.to_json(orient = 'records', lines = True)
        
        match_df = pd.DataFrame(columns = ['PDF Value', 'Excel Value', 'Status'])
        
        json_data = pd.read_json(json_string, orient = 'records', lines = True)
        excel_data = pd.read_excel(excel_file, sheet)
        
        for i, (prow, exrow) in enumerate(zip(json_data.itertuples(index = False), excel_data.itertuples(index = False)), start = 1):
            for j, (pdf_val, excel_val) in enumerate(zip(prow, exrow), start = 1):
                excel_val = excel_val.replace("\n", "\r")
                if pdf_val.lower() == excel_val.lower():
                    status = "Match"
                else:
                    status = "Not Match"
                
                row_data = {'PDF Value': pdf_val, 'Excel Value': excel_val, 'Status': status}
                temp_df  = pd.DataFrame(row_data, index = [i])
                match_df = pd.concat([match_df, temp_df])
                
        match_df.reset_index(drop = True, inplace = True)
        styled_df = match_df.style.apply(highlight, axis = 1)
        
        st.table(styled_df)
        
st.title("Billing Automation")
pdf_file = st.file_uploader("Upload PDF", type = "pdf")
excel_file = st.file_uploader("Upload Excel", type = ["xls", "xlsx", "csv"])

if excel_file is not None:
    excel_file = pd.ExcelFile(excel_file)
    
if st.button("Compare"):
    compare(pdf_file, excel_file)