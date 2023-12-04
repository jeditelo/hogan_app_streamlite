import os
import re
import warnings
import fitz  
import streamlit as st
import pandas as pd
import numpy as np
from pdfreader import SimplePDFViewer
import base64

warnings.filterwarnings('ignore')


def read_file(path_to_file):
    #fd = open(path_to_file, "rb")
    viewer = SimplePDFViewer(path_to_file)
    viewer.render()
    return viewer

def get_canvas(viewer):
    page_1_canvas = viewer.canvas.text_content
    if not os.path.exists(r'.\tmp'):
            os.makedirs(r'.\tmp')

    with open(r".\tmp\page_1_canvas.txt", "w", encoding='utf8') as f:
        f.write(page_1_canvas)

    viewer.navigate(2)
    viewer.render()
    page_2_canvas = viewer.canvas.text_content

    with open(r".\tmp\page_2_canvas.txt", "w", encoding='utf8') as f:
        f.write(page_2_canvas)


def first_page():
    df = pd.read_csv(r".\tmp\page_1_canvas.txt", header=[1], sep='\t')
    df.rename(columns={' q':'col1'}, inplace=True)
    df['col2'] = df['col1'].str.findall(r"\)\] TJ")
    df.col2 = df.col2.apply(lambda y: np.nan if len(y)==0 else y)
    df_name = df.loc[(df.col2.isnull()!=True)]
    df_name.drop(columns=['col2'], inplace=True)
    df_name.col1 = df_name.col1.astype('str')
    df_name['col2'] = df_name.apply(lambda x: re.sub("\(\ \)", "_", x['col1']), axis=1)
    df_name['col2'] = df_name.apply(lambda x: re.sub("\(|\)|TJ|\[|\]|\ ", '', x['col2']), axis=1)
    df_name = df_name[3:-10]
    df_name.reset_index(drop=True, inplace=True)
    df_name['count_'] = df_name.col2.str.len()
    df_count = df_name.loc[df_name.count_<=3]
    df_name_ = df_name.loc[df_name.count_>3]
    df_count.index = df_count.index-1
    df_name_.count_ = df_count.col2
    df_name_.drop(columns=['col1'], inplace=True)
    df_name_.rename(columns={
        'col2':'col2',
        'count_':'count'
    }, inplace=True)
    df_name_.reset_index(drop=True, inplace=True)
    df_name_[:1].col2 = 'HPI'
    df_name_[8:9].col2 = 'HDS'
    df_name_[20:21].col2 = 'MVPI'
    df_name_['cat']=np.nan
    df_name_['cat'] = df_name_.loc[df_name_['count'].isnull()==True, 'col2']
    df_name_.cat.fillna(method='pad', inplace=True)
    df_name_ = df_name_.loc[df_name_['count'].isnull()==False]
    df_name_['sub_cat'] = np.nan

    return df_name_


def second_page():
    mapping = {'0':'0',
         '1':'39',
         '2':'69',
         '3':'89',
         '4':'100',}
    grey = '0.901 0.905 0.909 rg'
    df = pd.read_csv(r".\tmp\page_2_canvas.txt", header = [1])
    df.rename(columns={' q':'col1'}, inplace=True)
    df['col2'] = df['col1'].str.findall(r"\)\] TJ")
    df.col2 = df.col2.apply(lambda y: np.nan if len(y)==0 else y)
    df_name = df.loc[(df.col2.isnull()!=True)]
    df_name.drop(columns=['col2'], inplace=True)
    df_name.col1 = df_name.col1.astype('str')
    df_name['col2'] = df_name.apply(lambda x: re.sub("\(\ \)", "_", x['col1']), axis=1)
    df_name['col2'] = df_name.apply(lambda x: re.sub("\(|\)|TJ|\[|\]|\ ", '', x['col2']), axis=1)
    
    try:
        test_df = pd.DataFrame(index=range(0,100),columns=['A'], dtype='float')
        for ind in range(df_name.shape[0]):
            i = df_name.index[ind]
            j = df_name.index[ind+1]
            name = 'col'+str(i)
            tmp = df.col1[i:j].reset_index(drop=True)
            test_df[name] = tmp
    except:
        pass
    
    test_df.dropna(thresh=15, axis=1, inplace=True)
    count_grey = pd.DataFrame(np.sum(test_df==grey, axis=0), columns=['count'])
    count_grey.index = count_grey.index.str.replace('col', '')
    df_name.index = df_name.index.astype('str')
    df_name['count']=None
    df_name.update(count_grey)
    df_name.fillna(999, inplace=True)
    df_name.dropna(inplace=True)
    df_name['count'] = 4 - df_name['count']
    df_name.replace(-995, ' ', inplace=True)
    df_name.drop(columns=['col1'], inplace=True)
    df_name = df_name[:157]
    df_name.reset_index(drop=True, inplace=True)
    df_name['count'][df_name.col2=='Баллы_по_субшкалам'] = np.nan
    df_name['sub_cat'] = np.nan
    df_name['sub_cat'] = df_name.loc[df_name['count']==' ']
    df_name[:1].col2 = 'HPI'
    df_name[51:52].col2 = 'HDS'
    df_name[96:97].col2 = 'MVPI'
    df_name['cat']=np.nan
    df_name['cat'] = df_name.loc[df_name['count'].isnull()==True, 'col2']
    df_name.sub_cat.fillna(method='pad', inplace=True)
    df_name.cat.fillna(method='pad', inplace=True)
    df_name = df_name.loc[df_name['count']!=' ']
    df_name = df_name.loc[df_name['count'].isnull()==False]
    df_name['count'] = df_name['count'].astype('int')
    df_name.loc[df_name.cat=='HDS', 'count']  = df_name.loc[df_name.cat=='HDS', 'count'].astype('str').apply(lambda val: mapping[val])
    df_name.loc[df_name.cat=='MVPI', 'count'] *= 25
    df_name.loc[df_name.cat=='HPI', 'count']*= 25
    return df_name

def concat_frame(page1, page2, name):
    df = pd.concat([page1, page2])
    df['name']  = name
    df = df[['name', 'cat', 'sub_cat', 'col2', 'count']]
    df.rename(columns={
        'name':'Name',
        'cat':'lvl 1',
        'sub_cat':'lvl 2',
        'col2':'lvl 3',
        'count':'Score '
    },  inplace=True)
    df.reset_index(drop=True, inplace=True)
    df[42:43]['lvl 2'] = 'Амбициозность'
    df[42:43]['lvl 3'] = 'Отсутствие_социальной_тревожности'
    df[28:29]['lvl 1'] = ''
    return df

def write_file(excel_path, frame):
    df_excel = pd.read_excel(excel_path, engine='openpyxl')
    df_excel.reset_index(drop=True, inplace=True)
    result = pd.concat([frame, df_excel],axis=0, ignore_index=True)
    result.to_excel(excel_path, index=False)

def old_file_version_proc(excel_path, file, file_name):

    pdf_document = fitz.open(file)
    data = ''
    page = pdf_document.load_page(0)

    data += page.get_text()

    pdf_document.close()

    start_index = data.index('Hogan Personality Inventory')
    end_index = data.index('© 2017 HOGAN ASSESSMENT SYSTEMS, INC.')
    trimmed_data = data[start_index:end_index]

    split_data = trimmed_data.split('\n')

    split_data = [line for line in split_data if line]

    categories = []
    indicators = []
    scores = []

    current_category = ''
    for line in split_data:
        if line in ['Hogan Personality Inventory', 'Hogan Development Survey', 'Motives, Values, Preferences Inventory']:
            current_category = line
        else:
            if line.isdigit() or line.startswith(' '):
                scores.append(line.strip())
            else:
                indicators.append(line)
                categories.append(current_category)

    df = pd.DataFrame({
        'Name':file_name,
        'Category': categories,
        'Indicator': indicators,
        'Score': scores
    })
    df.to_excel(excel_path, index=False)
    



def main():
    st.title("Hogan test. PDF to Excel")
    st.subheader("PDF files")
    uploaded_files = st.file_uploader("Choose a PDF files", type=['pdf'], accept_multiple_files=True, key=None)
	
    if st.button("Process"):
        with st.spinner('Wait for it...'):
            if not os.path.exists(r'.\results'):
                os.makedirs(r'.\results')
            path = r".\results"
            excel_name = 'result.xlsx'
            excel_path = os.path.join(path, excel_name)
            with pd.ExcelWriter(excel_path ,mode='w') as writer:
                pd.DataFrame().to_excel(writer, sheet_name='Sheet_name_1')
            #path_to_file = r".\examples\test.pdf"
            #folder = r".\examples"
            #files = [x for x in os.listdir(folder) if x.endswith(".pdf")]
            for file in uploaded_files:
                
                #path_to_file = os.path.join(folder, file)
                path_to_file = file.name
                st.write(file)
		st.write(file.size)
		if file.size>100609
                    viewer = read_file(file)
                    get_canvas(viewer)
                    df_page1 = first_page()
                    df_page2 = second_page()
                    fin_df = concat_frame(df_page1, df_page2, path_to_file)
                    write_file(excel_path, fin_df)
                else:
                    old_file_version_proc(excel_path, file, path_to_file)
            st.success('Done!')
            with open(excel_path, 'rb') as f:
                data = f.read()
                bin_str = base64.b64encode(data).decode()
                href = f'<a href="data:application/octet-stream;base64,{bin_str}"  download="{os.path.basename(excel_path)}">Download Result Excel</a>'
                st.markdown(href, unsafe_allow_html=True)

if __name__ == '__main__':
	main()
