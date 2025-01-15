import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
import datetime
import matplotlib.pyplot as plt
import matplotlib 
from io import BytesIO
import plotly.graph_objects as go   
import numpy as np
from bs4 import BeautifulSoup
import plotly.express as px
import plotly.figure_factory as ff
from openpyxl import Workbook

# caching
# 인자가 바뀌지 않는 함수 실행 결과를 저장 후 크롬의 임시 저장 폴더에 저장 후 재사용
@st.cache_data
def get_stock_info():
    base_url =  "http://kind.krx.co.kr/corpgeneral/corpList.do"    
    method = "download"
    url = "{0}?method={1}".format(base_url, method)   
    df = pd.read_html(url, header=0,encoding='cp949')[0]
    df['종목코드']= df['종목코드'].apply(lambda x: f"{x:06d}")     
    df = df[['회사명','종목코드']]
    return df

def get_ticker_symbol(company_name):     
    df = get_stock_info()
    code = df[df['회사명']==company_name]['종목코드'].values    
    ticker_symbol = code[0]
    return ticker_symbol

today = datetime.datetime.now()
start_year = today.year - 16
next_year = today.year + 6
jan_1 = datetime.date(start_year, 1, 1)
dec_31 = datetime.date(next_year, 12, 31)

# 코드 조각 추가
st.sidebar.write("## 회사 이름과 기간을 입력하세요")
st.write("# 무슨 주식을 사야 부자가 되려나...")
stock_name = st.sidebar.text_input("회사 이름")
date_range = st.sidebar.date_input("시작일 - 종료일",
    (),
    jan_1,
    dec_31)
bt = st.sidebar.button("주식 데이터 확인")
if stock_name:
    ticker_symbol = get_ticker_symbol(stock_name)

    if bt:
        start_p = date_range[0]               
        end_p = date_range[1]
        df = fdr.DataReader(f'KRX:{ticker_symbol}', start_p, end_p).iloc[:,:6]
        df.index = df.index.date

        st.subheader(f"[{stock_name}] 주가 데이터")
        st.dataframe(df.head(7))
        df = df.reset_index()

        df.rename(columns = {'index' : 'Date'}, inplace = True)

        fig = go.Figure()

        fig.add_trace(go.Line(
            x= df.Date,
            y= df.Close,
        ))
        fig.update_layout(title_text=f"{stock_name}의 종가 데이터", title_x = 0.5)
        fig.update_xaxes(title_text='날짜')
        fig.update_yaxes(title_text='종가', range=[df.Close.min()-1000,df.Close.max()+1000])

        st.plotly_chart(fig, use_container_width = True)
        excel_data = BytesIO()      
        df.to_excel(excel_data)


        left_column, right_column = st.columns(2)

        left_column.download_button("엑셀 파일 다운로드", 
                excel_data, file_name='stock_data_to_excel.xlsx')
        csv = df.to_csv().encode('utf-8')
        right_column.download_button("csv 파일 다운로드", 
            data = csv, file_name='stock_data_to_csv.csv',
            mime = 'text/csv')