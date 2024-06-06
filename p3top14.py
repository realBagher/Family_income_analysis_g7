import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import openpyxl
# نام فایل‌ها
file_names = [
    'U98', 'U99', 'U1400', 'U1401', 'R98', 'R99', 'R1400', 'R1401',
]

# مسیر فایل‌ها
file_path_template = '../../data/{}.xlsx'

# نام شیت‌ها برای هر فایل
sheet_names_template = [
    '{}P3S08', '{}P3S09', '{}P3S10', '{}P3S11', '{}P3S12', '{}P3S13'
]

# لیست برای ذخیره داده‌ها از هر فایل
all_data_frames = []
p3s14_data_frames = []

for file_name in file_names:
    # مسیر فایل کامل
    file_path = file_path_template.format(file_name)
    
    # نمایش نام شیت‌ها برای هر فایل
    xls = pd.ExcelFile(file_path)

    # پردازش شیت های <filename>P3S07 تا <filename>P3S13

    data_frames = []

    for sheet_template in sheet_names_template:
        sheet_name = sheet_template.format(file_name)
        
        if sheet_name in xls.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            if not df.empty:
                data_frames.append(df)
        else:
            print(f"Sheet {sheet_name} not found in file {file_name}")
            continue

    if data_frames:
        combined_df = pd.concat(data_frames, ignore_index=True)

        # حذف ستون های اضافه
        combined_df.drop(columns=['purchased'], inplace=True)

        # تنظیم ستون Address به عنوان index
        combined_df.set_index('Address', inplace=True)

        # تبدیل ستون 'value' به عدد و حذف مقادیر غیرعددی
        combined_df['value'] = pd.to_numeric(combined_df['value'], errors='coerce')

        # حذف ردیف‌هایی که 'value' آن‌ها عدد نیست (مقدار NaN)
        combined_df.dropna(subset=['value'], inplace=True)

        # جمع value ها
        grouped_df = combined_df.groupby(['Address', 'code'])['value'].sum().reset_index()

        # مدیریت داده‌های پرت در ستون value
        value_mean = grouped_df['value'].mean()
        value_std = grouped_df['value'].std()
        upper_limit_value = value_mean + 3 * value_std
        lower_limit_value = value_mean - 3 * value_std
        grouped_df['value'] = grouped_df['value'].clip(lower=lower_limit_value, upper=upper_limit_value)

        # تبدیل ستون ها به دسته‌بندی
        columns_to_convert = ['Address', 'code']
        for column in columns_to_convert:
            grouped_df[column] = grouped_df[column].astype('category')

        # افزودن ستون R/U و year
        grouped_df['Year'] = file_name[1:]  # استخراج سال از نام فایل
        grouped_df['R/U'] = 'U' if file_name.startswith('U') else 'R'

        # افزودن داده‌های پردازش شده به لیست کل
        all_data_frames.append(grouped_df)
    
    # پردازش شیت <filename>P3S14
    p3s14_sheet_name = f'{file_name}P3S14'
    if p3s14_sheet_name in xls.sheet_names:
        df_p3s14 = pd.read_excel(file_path, sheet_name=p3s14_sheet_name)
        
        # حذف ستون‌های غیرمفید
        columns_to_drop = ['code', 'purchased']
        df_p3s14.drop(columns=columns_to_drop, inplace=True)

        # تبدیل ستون Address به دسته بندی
        df_p3s14['Address'] = df_p3s14['Address'].astype('category')

        # تبدیل ستون Address به index
        df_p3s14.set_index('Address', inplace=True)

        # جمع value ها به ازای Address های یکسان
        grouped_p3s14_df = df_p3s14.groupby('Address', observed=False).sum()

        grouped_p3s14_df['value'] = pd.to_numeric(grouped_p3s14_df['value'], errors='coerce')

        # Drop rows with NaN values in 'value' column
        grouped_p3s14_df = grouped_p3s14_df.dropna(subset=['value'])

        # مدیریت داده‌های پرت در ستون value
        value_mean_p3s14 = grouped_p3s14_df['value'].mean()
        value_std_p3s14 = grouped_p3s14_df['value'].std()
        upper_limit_value_p3s14 = value_mean_p3s14 + 3 * value_std_p3s14
        lower_limit_value_p3s14 = value_mean_p3s14 - 3 * value_std_p3s14
        grouped_p3s14_df['value'] = grouped_p3s14_df['value'].clip(lower=lower_limit_value_p3s14, upper=upper_limit_value_p3s14)
        
        # افزودن ستون Year و R/U
        grouped_p3s14_df['Year'] = file_name[1:]  # استخراج سال از نام فایل
        grouped_p3s14_df['R/U'] = 'U' if file_name.startswith('U') else 'R'
        
        # افزودن داده‌های پردازش شده به لیست کل
        p3s14_data_frames.append(grouped_p3s14_df)

# ترکیب تمام داده‌های شیت‌های اصلی در یک DataFrame
final_df = pd.concat(all_data_frames, ignore_index=True)

# ترکیب تمام داده‌های شیت‌های P3S14 در یک DataFrame
final_p3s14_df = pd.concat(p3s14_data_frames, ignore_index=True)

# نمایش داده نهایی
print(final_df)
print(final_p3s14_df)


