import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import openpyxl
import pygwalker as pyg
import re

# وارد کردن داده‌ها
file_names = [
    'U98.xlsx', 'U99.xlsx', 'U1400.xlsx', 'U1401.xlsx', 'R98.xlsx', 'R99.xlsx', 'R1400.xlsx', 'R1401.xlsx',
]

# لیست برای ذخیره داده‌های خوانده شده
M98_1401 = []

# خواندن فایل‌ها و افزودن ستون‌های جدید
for file_name in file_names:
    xls = pd.ExcelFile(file_name)
    temp = re.findall(r'\d+', file_name)
    for sheet_name in xls.sheet_names:
        p = xls.parse(sheet_name)
        p['dataYear'] = np.full(len(p), temp)
        p['R/U'] = 'U' if file_name.startswith('U') else 'R'
        M98_1401.append(p)

# ادغام داده‌ها
temp = M98_1401.copy()
M98_1401 = []
for i in range(1, 22):
    i = i - 1
    M98_1401.append(pd.concat((temp[i], temp[i+21], temp[i+2*21], temp[i+3*21], temp[i+4*21], temp[i+5*21], temp[i+6*21], temp[i+7*21]), axis=0))

# پیش‌پردازش
## اطلاعات خانواده
info_Family = M98_1401[0][['Address', 'Fasl', 'province', 'dataYear', 'R/U']].merge(M98_1401[3], on='Address', how='outer')

## اطلاعات اعضا
info_Member = M98_1401[1].copy()

## هزینه‌ها
## هزینه‌های خوراک و نوشیدنی
cost1 = pd.concat((M98_1401[3], M98_1401[4]), axis=0)

### هزینه‌های اجاره
cost2 = M98_1401[6]

### سایر هزینه‌ها
M98_1401[15]['value'] = pd.to_numeric(M98_1401[15]['value'], errors='coerce')
M98_1401[16]['value'] = pd.to_numeric(M98_1401[16]['value'], errors='coerce')
cost3 = pd.concat((M98_1401[5], M98_1401[7], M98_1401[8], M98_1401[9], M98_1401[10], M98_1401[11], M98_1401[12], M98_1401[13], M98_1401[14], M98_1401[15], M98_1401[16]), axis=0).reset_index(drop=True)

### ادغام همه هزینه‌ها
cost = pd.concat((cost1, cost2, cost3), axis=0)

# پاکسازی داده‌ها
cost = cost.fillna(0)

## ایجاد ستون دسته‌بندی
cost['catagory'] = cost.code.astype(str).str[:1]

## پاک‌سازی ستون‌های 'gram' و 'kilogram'
cost['gram'] = pd.to_numeric(cost['gram'], errors='coerce')
cost['kilogram'] = pd.to_numeric(cost['kilogram'], errors='coerce')

## محاسبه ستون 'Kilogram'
cost['Kilogram'] = cost['gram'] / 1000 + cost['kilogram']

## گروه‌بندی داده‌ها بر اساس آدرس، سال داده، دسته‌بندی و نوع (شهری/روستایی)
grouped_cost = cost.groupby(['Address', 'dataYear', 'catagory', 'R/U'])[['value', 'Kilogram']].sum().reset_index()

## استفاده از np.isin برای ایجاد ماسک بولی
mask = np.isin(grouped_cost['catagory'], ['1', '3', '4', '6', '7', '11'])

## فیلتر کردن داده‌ها بر اساس ماسک بولی
filtered_cost = grouped_cost[mask]

# ادغام داده‌های درآمد
income = M98_1401[17].merge(M98_1401[18].iloc[:, 0:16], on=['Address', 'member'], how='outer') \
    .merge(M98_1401[19].iloc[:, 0:8].merge(M98_1401[20].iloc[:, 0:5], on=['Address', 'member'], how='outer'), on=['Address', 'member'], how='outer').drop('DYCOL00', axis=1)

# پاک‌سازی داده‌های درآمد
cleaned_income = income.copy()
cleaned_income['employed_w'] = cleaned_income['employed_w'].replace(' ', np.nan).fillna(0).astype('float64')
cleaned_income['employed_s'] = cleaned_income['employed_s'].replace(' ', np.nan).fillna(0).astype('float64')
cleaned_income['status_w'] = pd.to_numeric(cleaned_income['status_w'], errors='coerce').fillna(0)
cleaned_income['status_s'] = pd.to_numeric(cleaned_income['status_s'], errors='coerce').fillna(0)
cleaned_income['hours_w'] = pd.to_numeric(cleaned_income['hours_w'], errors='coerce').fillna(0)
cleaned_income['hours_s'] = pd.to_numeric(cleaned_income['hours_s'], errors='coerce').fillna(0)
cleaned_income['days_w'] = pd.to_numeric(cleaned_income['days_w'], errors='coerce').fillna(0)
cleaned_income['days_s'] = pd.to_numeric(cleaned_income['days_s'], errors='coerce').fillna(0)
cleaned_income['income_s_y'] = pd.to_numeric(cleaned_income['income_s_y'], errors='coerce').fillna(0)

# ایجاد ستون‌های جدید بر اساس محاسبات
cleaned_income['Employed'] = cleaned_income['employed_w'] + cleaned_income['employed_s']
cleaned_income['ISCO'] = cleaned_income['ISCO_w'] + cleaned_income['ISCO_s']
cleaned_income['ISIC'] = cleaned_income['ISIC_w'] + cleaned_income['ISIC_s']
cleaned_income['Status'] = cleaned_income['status_w'] + cleaned_income['status_s']
cleaned_income['Hours'] = cleaned_income['hours_w'] + cleaned_income['hours_s']
cleaned_income['Days'] = cleaned_income['days_w'] + cleaned_income['days_s']

# انتخاب ستون‌های نهایی برای تحلیل درآمد
final_income = cleaned_income[[
    'Employed', 'ISCO_w', 'ISIC_w', 'Status', 'Hours', 'Days', 'ISCO_s', 'ISIC_s', 'netincome_w_m', 'netincome_w_y', 'agriculture', 'sale', 'income_s_y',
    'income_pension', 'income_rent', 'income_interest', 'income_aid', 'income_resale', 'income_transfer', 'subsidy_month', 'subsidy', 'Fasl', 'dataYear', 'R/U'
]].fillna(0)

# تابع محاسبه IQR و حذف نقاط دورافتاده
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

# تحلیل آماری
## توزیع سنی اعضای خانواده
plt.figure(figsize=(10, 6))
plt.hist(info_Member['age'], bins=100)
plt.xlabel('سن')
plt.ylabel('تعداد')
plt.title('توزیع سن اعضای خانواده')
plt.show()
## میزان تحصیلات اعضای خانواده
plt.figure(figsize=(10, 6))
plt.bar(info_Member['degree'].value_counts().index, info_Member['degree'].value_counts().to_list())
plt.xlabel('مدرک تحصیلی', rotation=45, ha='right')  # rotation=45 برای چرخش متن به زاویه 45 درجه
plt.ylabel('تعداد')
plt.title('توزیع مدرک تحصیلی اعضای خانواده')
plt.show()
## رابطه اعضای خانواده با سرپرست
plt.figure(figsize=(10, 6))
plt.bar(info_Member['relation'].value_counts().index, info_Member['relation'].value_counts().to_list())
plt.xlabel('نسبت', rotation=45, ha='right')  # rotation=45 برای چرخش متن به زاویه 45 درجه
plt.ylabel('تعداد')
plt.title('توزیع نسبت اعضای خانواده')
plt.show()
## سطح سواد اعضای خانواده
plt.figure(figsize=(10, 6))
plt.bar(info_Member['literacy'].value_counts().index, info_Member['literacy'].value_counts().to_list())
plt.xlabel('سطح سواد', rotation=45, ha='right')  # rotation=45 برای چرخش متن به زاویه 45 درجه
plt.ylabel('تعداد')
plt.title('توزیع سطح سواد اعضای خانواده')
plt.show()
## وضعیت شغلی اعضای خانواده
plt.figure(figsize=(10, 6))
plt.bar(info_Member['occupationalst'].value_counts().index, info_Member['occupationalst'].value_counts().to_list())
plt.xlabel('وضعیت شغلی', rotation=45, ha='right')  # rotation=45 برای چرخش متن به زاویه 45 درجه
plt.ylabel('تعداد')
plt.title('توزیع وضعیت شغلی اعضای خانواده')
plt.show()














