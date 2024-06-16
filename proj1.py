from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.metrics import accuracy_score
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
info_Family = M98_1401[0][['Address', 'Fasl', 'province','khanevartype', 'dataYear', 'R/U']]

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
income = M98_1401[17].merge(M98_1401[18].iloc[:, 0:16], on=['Address', 'member'], how='inner') \
    .merge(M98_1401[19].iloc[:, 0:8].merge(M98_1401[20].iloc[:, 0:5], on=['Address', 'member'], how='inner'), on=['Address', 'member'], how='inner').drop('DYCOL00', axis=1)

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
    'Address','Employed', 'ISCO_w', 'ISIC_w', 'Status', 'Hours', 'Days', 'ISCO_s', 'ISIC_s', 'netincome_w_m', 'netincome_w_y', 'agriculture', 'sale', 'income_s_y',
    'income_pension', 'income_rent', 'income_interest', 'income_aid', 'income_resale', 'income_transfer', 'subsidy_month', 'subsidy', 'Fasl', 'dataYear', 'R/U'
]].fillna(0)
## ذخیره داده پاک
info_Family.to_csv('info_Family.csv')
info_Member.to_csv('info_Member.csv')
filtered_cost.to_csv('filtered_cost.csv')
final_income.to_csv('final_income.csv')
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


from scipy.stats import norm
# آزمون فرض آماری
final_income_p = final_income.merge(info_Family[['Address','province']],on='Address',how='inner')
province_data = final_income_p[final_income_p['province'] == 'CharmahalBakhtiari']

# درآمد خانوارهای شهری و روستایی
shahri =  province_data[province_data['R/U'] == 'U']['netincome_w_y'] # داده‌های درآمد خانواده‌های شهری
roosta = province_data[province_data['R/U'] == 'R']['netincome_w_y'] # داده‌های درآمد خانواده‌های روستایی

# محاسبه میانگین و واریانس نمونه‌ها
mean_shahri = np.mean(shahri)
mean_roosta = np.mean(roosta)
var_shahri = np.var(shahri, ddof=1)  # استفاده از ddof=1 برای محاسبه واریانس نمونه‌ای
var_roosta = np.var(roosta, ddof=1)
n_shahri = len(shahri)
n_roosta = len(roosta)

# محاسبه آماره z
z_stat = (mean_shahri - mean_roosta) / np.sqrt((var_shahri / n_shahri) + (var_roosta / n_roosta))

# محاسبه مقدار p
p_value = 2 * (1 - norm.cdf(abs(z_stat)))

# نمایش نتایج
print("z-statistic:", z_stat)
print("p-value:", p_value)

# تصمیم‌گیری
alpha = 0.05
if p_value < alpha:
    print("فرض صفر رد می‌شود: میانگین درآمد خانواده‌های شهری و روستایی برابر نیست.")
else:
    print("فرض صفر رد نمی‌شود: میانگین درآمد خانواده‌های شهری و روستایی برابر است.")

# کاهش اندازه داده‌ها به 5% داده‌های اصلی
sampled_data = scaled_data[np.random.choice(scaled_data.shape[0], size=int(scaled_data.shape[0] * 0.05, replace=False))]

dbscan = DBSCAN(eps=0.5, min_samples=10)
labels_dbscan = dbscan.fit_predict(sampled_data)

plt.figure(figsize=(12, 8))
sns.scatterplot(x=sampled_data[:, 0], y=sampled_data[:, 1], hue=labels_dbscan, palette='viridis', legend='full', s=50, alpha=0.6)
plt.xlabel('cost')
plt.ylabel('income')
plt.title('DBSCAN')
plt.legend(title='clusters')
plt.grid(True)
plt.show()

transport=filtered_cost[filtered_cost["catagory"]=="7"]
transport.drop(["Kilogram"],axis=1,inplace=True)

merged_data= pd.merge(final_income,transport, on=["Address","dataYear","R/U"], how='inner')
numeric_data=merged_data.select_dtypes(include='number')
dataplot = sns.heatmap(numeric_data.corr(), cmap="YlGnBu")  
plt.show() 

#one hot encoder
merged_data= pd.concat([merged_data,pd.get_dummies(merged_data['R/U'],drop_first=True)],axis=1)
merged_data=merged_data.drop(['R/U'],axis=1)
merged_data

test_data= merged_data[(merged_data["Fasl"]==4) & (merged_data["dataYear"]=="1401")]
y_test=test_data.value
train_data= merged_data[~((merged_data["Fasl"]==4) & (merged_data["dataYear"]=="1401"))]
y_data= train_data['value']
X_data = train_data.drop('value',axis=1)
X_train, X_val, y_train, y_val = train_test_split(X_data,y_data, test_size=0.30)
from sklearn.ensemble import RandomForestRegressor

# فیلتر و پیش‌پردازش داده برای دسته حمل و نقل
transport = filtered_cost[filtered_cost["catagory"] == "7"]
transport.drop(["Kilogram"], axis=1, inplace=True)

# ادغام داده‌های درآمد و حمل و نقل
merged_data = pd.merge(final_income, transport, on=["Address", "dataYear", "R/U"], how='inner')

# One hot کدگذاری برای متغیرهای دسته‌بندی
merged_data = pd.concat([merged_data, pd.get_dummies(merged_data['R/U'], drop_first=True)], axis=1)
merged_data.drop(['R/U'], axis=1, inplace=True)

# آماده‌سازی داده‌های آموزشی و اعتبارسنجی
test_data = merged_data[(merged_data["Fasl"] == 4) & (merged_data["dataYear"] == "1401")]
y_test = test_data["value"]
train_data = merged_data[~((merged_data["Fasl"] == 4) & (merged_data["dataYear"] == "1401"))]
y_data = train_data['value']
X_data = train_data.drop('value', axis=1)
X_train, X_val, y_train, y_val = train_test_split(X_data, y_data, test_size=0.30)

# ساخت و آموزش مدل جنگل تصادفی
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# پیش‌بینی روی مجموعه اعتبارسنجی
y_pred_val = rf_model.predict(X_val)

# ارزیابی مدل
r2_val = r2_score(y_val, y_pred_val)
mse_val = mean_squared_error(y_val, y_pred_val)
print(f"R-squared score on validation set: {r2_val:.2f}")
print(f"Mean Squared Error on validation set: {mse_val:.2f}")

# param_grid = {
#     'max_depth': [2, 4, 6, 8, 10],
#     'min_samples_split': [2, 5, 10],
#     'min_samples_leaf': [1, 2, 4]
# }
# #using 5-fold cross-validation 
# grid_search = GridSearchCV(estimator=cls, param_grid=param_grid, cv=5)
# grid_search.fit(X_train, y_train)

# best_estimator = grid_search.best_estimator_
# best_params = grid_search.best_params_

# y_test_pred = best_estimator.predict(X_test)
# test_accuracy = accuracy_score(y_test, y_test_pred)
# print(f"Test Accuracy: {test_accuracy:.2f}")

# # Print the best hyperparameters
# print("Best Hyperparameters:")
# print(best_params)

y_pred_test = model.predict(X_test)
loss = np.mean((y_test- y_pred_test) ** 2)
r_squared = r2_score(y_test, y_pred_test)

# Plot the loss
plt.figure(figsize=(8, 6))
plt.plot(loss)
plt.title('Loss')
plt.xlabel('Iteration')
plt.ylabel('Loss')
plt.show()

# Plot the R-squared
plt.figure(figsize=(8, 6))
plt.plot(r_squared)
plt.title('R-squared')
plt.xlabel('Iteration')
plt.ylabel('R-squared')
plt.show()
