# Family_income_analysis_g7
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# import data
U1401xls = pd.ExcelFile('U1401.xlsx')
R1401xls = pd.ExcelFile('R1401.xlsx')
U1400xls = pd.ExcelFile('U1400.xlsx')
R1400xls = pd.ExcelFile('R1400.xlsx')
U99xls = pd.ExcelFile('U99.xlsx')
R99xls = pd.ExcelFile('R99.xlsx')
U98xls = pd.ExcelFile('U98.xlsx')
R98xls = pd.ExcelFile('R98.xlsx')
M98_1401=[]
for sheet_name in U1401xls.sheet_names:
    p=U1401xls.parse(sheet_name)
    p['dataYear']=1401
    p['R/U']='R'
    M98_1401.append(p)
for sheet_name in R1401xls.sheet_names:
    p=R1401xls.parse(sheet_name)
    p['dataYear']=1401
    p['R/U']='U'
    M98_1401.append(p)
for sheet_name in U1400xls.sheet_names:
    p=U1400xls.parse(sheet_name)
    p['dataYear']=1400
    p['R/U']='R'
    M98_1401.append(p)
for sheet_name in R1400xls.sheet_names:
    p=R1400xls.parse(sheet_name)
    p['dataYear']=1400
    p['R/U']='U'
    M98_1401.append(p)
for sheet_name in U99xls.sheet_names:
    p=U99xls.parse(sheet_name)
    p['dataYear']=1399
    p['R/U']='R'
    M98_1401.append(p)
for sheet_name in R99xls.sheet_names:
    p=R99xls.parse(sheet_name)
    p['dataYear']=1399
    p['R/U']='U'
    M98_1401.append(p)
for sheet_name in U98xls.sheet_names:
    p=U98xls.parse(sheet_name)
    p['dataYear']=1398
    p['R/U']='R'
    M98_1401.append(p)
for sheet_name in R98xls.sheet_names:
    p=R98xls.parse(sheet_name)
    p['dataYear']=1398
    p['R/U']='U'
    M98_1401.append(p)
for x in M98_1401:
    x.reset_index(drop=True)
# perproccessing
income = M98_1401[17].merge(M98_1401[18].iloc[:,0:16],on=['Address','member'],how='outer') \
.merge(M98_1401[19].iloc[:,0:8].merge(M98_1401[20].iloc[:,0:5],on=['Address','member'],how='outer'),on=['Address','member'],how='outer').drop('DYCOL00',axis=1)# \
cleaned_income =income.copy()
cleaned_income['employed_w'] = cleaned_income['employed_w'].replace(' ', np.nan)
cleaned_income['employed_s'] = cleaned_income['employed_s'].replace(' ', np.nan)
cleaned_income['employed_w'] = cleaned_income['employed_w'].fillna(0)
cleaned_income['employed_s'] = cleaned_income['employed_s'].fillna(0)
cleaned_income['status_w'] = pd.to_numeric(cleaned_income['status_w'], errors='coerce')
cleaned_income['status_s'] = pd.to_numeric(cleaned_income['status_s'], errors='coerce')
cleaned_income['hours_w'] = pd.to_numeric(cleaned_income['hours_w'], errors='coerce')
cleaned_income['hours_s'] = pd.to_numeric(cleaned_income['hours_s'], errors='coerce')
cleaned_income['days_w'] = pd.to_numeric(cleaned_income['days_w'], errors='coerce')
cleaned_income['days_s'] = pd.to_numeric(cleaned_income['days_s'], errors='coerce')
cleaned_income['income_s_y'] = pd.to_numeric(cleaned_income['income_s_y'], errors='coerce')
cleaned_income['Employed'] = cleaned_income['employed_w'].astype('float64') + cleaned_income['employed_s'].astype('float64')
cleaned_income['ISCO']=cleaned_income.ISCO_w + cleaned_income.ISCO_s
cleaned_income['ISIC']=cleaned_income.ISIC_w + cleaned_income.ISIC_s
cleaned_income['Status']=cleaned_income.status_w + cleaned_income.status_s
cleaned_income['Hours']=cleaned_income.hours_w+cleaned_income.hours_s
cleaned_income['Days']=cleaned_income.days_w+cleaned_income.days_s
final_income = cleaned_income[[
'Employed',
'ISCO_w',
'ISIC_w',
'Status',
'Hours',
'Days',
'ISCO_s',
'ISIC_s',
'netincome_w_m',
'netincome_w_y',
'agriculture',
'sale',
'income_s_y',
'income_pension',
'income_rent',
'income_interest',
'income_aid',
'income_resale',
'income_transfer',
'subsidy_month',
'subsidy',
'Fasl',
'dataYear',
'R/U']]
final_income = final_income.fillna(0)
