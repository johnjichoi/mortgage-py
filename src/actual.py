#!/usr/bin/env python3
# TODO description

import pandas as pd 
import os
from dotenv import load_dotenv

load_dotenv()

file_name = os.getenv('FILE_NAME')
file_path = os.path.join(os.getcwd(), f'data/{file_name}')

# read file
try:
    df = pd.read_csv(file_path)
except FileNotFoundError:
    raise FileNotFoundError('File not found')

# tag money in or out
df['type'] = ''
df.loc[df['Credit'].notna(), 'type'] = 'in'
df.loc[df['Debit'].notna(), 'type'] = 'out' 

# previous balance
df['prev_balance'] = df['Balance'].shift(periods=-1)

# days in month
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
df['days_in_month'] = df['Date'].dt.days_in_month
df['is_leap_year'] = df['Date'].dt.is_leap_year
df['days_in_year'] = 0
df.loc[df['is_leap_year'] == True, 'days_in_year'] = 366
df.loc[df['is_leap_year'] == False, 'days_in_year'] = 365

# calc percentage
df['out_perc'] = 0.0
df['out_perc_pa'] = 0.0
mask = df['type'] == 'out'
if len(df[mask].index) > 0:
    df.loc[mask, 'out_perc'] = (df[mask]['Debit']/df[mask]['prev_balance']) * 100
    df.loc[mask, 'out_perc_pa'] = (df[mask]['out_perc']/df[mask]['days_in_month']) * df[mask]['days_in_year']

# print Interest Charge
mask = df['Description'].str.contains('Interest Charge')
if len(df[mask].index) > 0:
    print(df[mask].to_markdown())