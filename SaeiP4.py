# Family_income_analysis_g7
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import openpyxl
import pygwalker as pyg
import re
# import data
file_names = [
    'U98.xlsx', 'U99.xlsx', 'U1400.xlsx', 'U1401.xlsx', 'R98.xlsx', 'R99.xlsx', 'R1400.xlsx', 'R1401.xlsx',
]
M98_1401=[]
for file_name in file_names:
    xls = pd.ExcelFile(file_name)
    temp=re.findall(r'\d+',file_name)
    print(temp)
    for sheet_name in xls.sheet_names:
        p = xls.parse(sheet_name)
        p['dataYear'] = np.full(len(p), temp)
        p['R/U']='U' if file_name.startswith('U') else 'R'
        M98_1401.append(p)
temp=M98_1401.copy()
M98_1401=[]
for i in range(1,22):
    i=i-1
    M98_1401.append(pd.concat((temp[i],temp[i+21],temp[i+2*21],temp[i+3*21],temp[i+4*21],temp[i+5*21],temp[i+6*21],temp[i+7*21]),axis=0))
# perproccessing
## P1,P2,P3
info_Family = M98_1401[0][['Address','Fasl','province','dataYear','R/U']].merge(M98_1401[3],on='Address',how='outer')
info_Member = M98_1401[1].copy()

cost1 = pd.concat((M98_1401[3],M98_1401[4]),axis=0)# food & drink
cost2 = M98_1401[6]# renting
M98_1401[15]['value'] = pd.to_numeric(M98_1401[15]['value'], errors='coerce')
M98_1401[16]['value'] = pd.to_numeric(M98_1401[16]['value'], errors='coerce')
cost3 = pd.concat((M98_1401[5],M98_1401[7],M98_1401[8],M98_1401[9],M98_1401[10],M98_1401[11],M98_1401[12],M98_1401[13],M98_1401[14],M98_1401[15],M98_1401[16]),axis=0).reset_index(drop=True) #other expence
cost = pd.concat((cost1,cost2,cost3),axis = 0)
# final_cost=cost[['Address','code','value','dataYear','R/U']]
#.merge(info_Family.iloc[:,0:3],on='Address',how='outer')
cost = cost.fillna(0)

cost['Kilogram'] = cost['gram'].astype('float64')/1000 + cost['kilogram'].astype('float64')
final_cost = cost[['Address','purchased','Kilogram','value','mortgage','dataYear','R/U']]
## P4
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
'Employed','ISCO_w','ISIC_w','Status','Hours','Days','ISCO_s','ISIC_s','netincome_w_m','netincome_w_y','agriculture','sale','income_s_y',
'income_pension','income_rent','income_interest','income_aid','income_resale','income_transfer','subsidy_month','subsidy','Fasl','dataYear','R/U'
]]
final_income = final_income.fillna(0)
## IQR
def Iqr_F(T):
    d1 = T.quantile(0.25)
    d3 = T.quantile(0.75)
    iqr = d3 - d1
    low_bound = d1 - 3 * iqr
    up_bound = d3 + 3 * iqr
    outliers = T[(T < low_bound) | (T > up_bound)].index
    T_copy = T.copy()
    # T_copy[outliers] = np.nan
    T_copy = T.clip(lower=low_bound, upper=up_bound)
    return pd.DataFrame(T_copy)
## Statistic
plt.hist(info_Member['age'],bins=100)
plt.show()
plt.bar(info_Member['degree'].value_counts().index,info_Member['degree'].value_counts().to_list())
plt.show()
plt.bar(info_Member['relation'].value_counts().index,info_Member['relation'].value_counts().to_list())
plt.show()
plt.bar(info_Member['literacy'].value_counts().index,info_Member['literacy'].value_counts().to_list())
plt.show()
plt.bar(info_Member['occupationalst'].value_counts().index,info_Member['occupationalst'].value_counts().to_list())
plt.show()
