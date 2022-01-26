import pandas as pd
import numpy as np
from datetime import datetime as dt, timedelta

# Create a df of daily averages
def daily_avg(df, product, costType, industry):
    # Drop columns not needed
    df = df.drop(['Unnamed: 0'], axis = 1)

    # Alter date field
    df["month_day_date"] = df["Day"].str[-5:]
    df["month_day_date"] = pd.to_datetime(df['month_day_date'], format='%m-%d', errors='coerce')

    # Segment data based on filters
    df = df[df['Product Type'] == product]
    df = df[df['Cost Method'] == costType]
    df = df[df['Target'] != 'Inclusion List']
    if industry:
        df = df[df['Brand Vertical Classification'] == industry] 

    print(df.head())

    if costType == 'CPV':
        df = calculate_cpv(df)
        print("CPV Route")
        print(df)
    elif costType == 'CPM':
        df = calculate_cpm(df)
        print("CPM Route")
        print(df)

    return df

def calculate_cpv(df):
    # Create Pivot Table on day
    pivot = pd.pivot_table(data=df,index='month_day_date',aggfunc={'Cost':np.sum,'Views':np.sum})
    pivot['COST'] = pivot['Cost']/pivot['Views']
    pivot['Date'] = pivot.index

    # Interpolate
    idx = pd.date_range('1900-01-01', '1900-12-31')
    s = pivot.reindex(idx, fill_value=np.nan)
    s['COST'] = s['COST'].interpolate()

    return s

def calculate_cpm(df):
    # Create Pivot Table on day
    pivot = pd.pivot_table(data=df,index='month_day_date',aggfunc={'Cost':np.sum,'Impr.':np.sum})
    pivot['COST'] = (pivot['Cost']/pivot['Impr.']) * 1000
    pivot['Date'] = pivot.index

    # Interpolate
    idx = pd.date_range('1900-01-01', '1900-12-31')
    s = pivot.reindex(idx, fill_value=np.nan)
    s['COST'] = s['COST'].interpolate()

    return s

# Obtain a df from user inputted date range
def date_range(df, start_date, end_date):
    start = dt.strptime(start_date, '%Y-%m-%d').date()
    end = dt.strptime(end_date, '%Y-%m-%d').date()

    print(start)

    # Date
    delta = end - start
    number_days = delta.days + 1

    # Create date list for the campaign flight
    date_list = [(start+ timedelta(days = day)).isoformat() for day in range(number_days)]

    print(date_list)

    # Create an empty df for predictions
    column_names = ["Date", "COST", "Date_18"]
    predictions = pd.DataFrame(columns = column_names)

    for x in date_list:
        Date_18 = '1900' + x[4:]
        cpv = df['COST'][Date_18]
    
        #Append New Row
        new_row = {'Date':x, 'Cost':cpv, 'Date_18':Date_18}
        predictions = predictions.append(new_row, ignore_index=True)

    print("Predictions")
    print(predictions)
    print("______")
    
    return predictions

# Obtains the average across each quarter
def quarter_avg(pivot_df):
    # Get Quarter Rate Progression with Q1 Base
    cost_q1 = pivot_df['COST'].iloc[0:90].mean()
    cost_q2 = pivot_df['COST'].iloc[90:181].mean()
    cost_q3 = pivot_df['COST'].iloc[181:273].mean()
    cost_q4 = pivot_df['COST'].iloc[273:365].mean()
    quarter_avg = [cost_q1, cost_q2, cost_q3, cost_q4]
    newlist = [round(element, 4) for element in quarter_avg]
    return newlist

