#!/usr/bin/env python3
# TODO description

import numpy_financial as npf
import pandas as pd
from datetime import datetime
import os
import csv
from dotenv import load_dotenv

load_dotenv()

def get_interest_rate():
    """ Get env file name for interest rates and load into
        list of dicts
    Raises:
        KeyError:       Env calculated file does not exist
        FileNotFound:   File does not exist

    Returns:
        list of dict:   CSV as list of dicts
    """
    file_name = os.getenv('CALCULATED_FILE')
    if not file_name:
        raise KeyError('File name does not exist')
    
    file_path = os.path.join(os.getcwd(), f'data/{file_name}')
    if not os.path.isfile(file_path):
        raise FileNotFoundError('File does not exist')
        
    with open(file_path, 'r') as data:
        dict_reader = csv.DictReader(data)
        return list(dict_reader)
    
def get_years():
    """ Get env mortgage duration in years

    Raises:
        ValueError: Env years does not exist or is not numeric

    Returns:
        int: Mortgage duration in years
    """
    try:
        return int(os.getenv('YEARS'))
    except ValueError:
        raise LookupError('Years not set')
    
def get_payments_per_year():
    """ Get env number of payments per year

    Raises:
        ValueError: Env payments per year does not exist or is not numeric

    Returns:
        int: Number of payments per year
    """
    try:
        return int(os.getenv('PAYMENTS_PER_YEAR'))
    except ValueError:
        raise LookupError('Payments not set')

def get_principal():
    """ Get env starting principal

    Raises:
        ValueError: Env principal does not exist or not numeric

    Returns:
        int: Starting principal
    """
    try:
        return int(os.getenv('PRINCIPAL'))
    except ValueError:
        raise LookupError('Principal not set')

def get_start_date():
    """ Get env start date of mortgage

    Raises:
        LookupError: Env start date does not exist or not in format dd/mm/yyyy

    Returns:
        datetime: Start date
    """
    try:
        return datetime.strptime(os.getenv('START_DATE'), '%d/%m/%Y')
    except ValueError:
        raise LookupError('Start date not set')

def build_df(start_date: datetime, periods: int):
    """ Build dataframe and populate with payment dates

    Args:
        start_date (datetime): Start date of mortgage
        period (int): Number of periods in mortgage
        
    Returns:
        df (pd.DataFrame): Initialised dataframe
    """
    df = pd.DataFrame(columns=['payment_date', 'interest_rate', 'payment', 'principal', 'interest', 'balance'], dtype='float')
    df['payment_date'] = pd.date_range(start_date, periods=periods, freq='M')
    df['payment_month'] = df['payment_date'].dt.month
    df['payment_year'] = df['payment_date'].dt.year
    return df
    
def calculate(
    df: pd.DataFrame, 
    interest_rate: float, 
    payments_per_year: int, 
    periods: int, 
    principal: float
):
    """ Calculate payment, principal and interest

    Args:
        df (pd.DataFrame): Dataframe with dates
        interest_rate (float): Interest rate of mortgage
        payments_per_year (int): Number of payments per year
        periods (int): Number of periods in mortgage
        principal (float): Initial principal of mortgage

    Returns:
        df (pd.DataFrame): _description_
    """
    df['interest_rate'] = interest_rate * 100
    df['payment'] = npf.pmt(interest_rate/payments_per_year, periods, principal)
    df['principal'] = npf.ppmt(interest_rate/payments_per_year, df.index, periods, principal)
    df['interest'] = npf.ipmt(interest_rate/payments_per_year, df.index, periods, principal)
    return df

def calculate_balance(df: pd.DataFrame, principal: float):
    """_summary_

    Args:
        df (pd.DataFrame): _description_
        principal (float): _description_

    Returns:
        _type_: _description_
    """
    df.loc[0, 'balance'] = principal + df.loc[0, 'principal']

    for i in range(1, len(df)):
        df.loc[i, 'balance'] = df.loc[i-1, 'balance'] + df.loc[i, 'principal']

    return df

if __name__ == "__main__":
    interest_rates = get_interest_rate()
    years = get_years()
    payments_per_year = get_payments_per_year() 
    principal = get_principal()
    start_date = get_start_date()

    df = build_df(start_date, years * payments_per_year)
    
    final_month = df.iloc[-1]['payment_month']
    final_year = df.iloc[-1]['payment_year']
    start_balance = None
    for interest_rate_dict in interest_rates:
        interest_rate = float(interest_rate_dict['interest_rate'])
        
        start_date = datetime.strptime(interest_rate_dict['start_date'], '%d/%m/%Y')
        start_month = start_date.month
        start_year = start_date.year
        
        end_date = datetime.strptime(interest_rate_dict['end_date'], '%d/%m/%Y')
        end_month = end_date.month
        end_year = end_date.year
        
        periods = (final_year - start_year) * 12 + final_month - start_month + 1
        
        temp_df = build_df(start_date, periods)
        
        if not start_balance:
            temp_df = calculate(temp_df, interest_rate, payments_per_year, periods, principal)
        else:
            temp_df = calculate(temp_df, interest_rate, payments_per_year, periods, start_balance)
        
        temp_df = temp_df[temp_df['payment_date'] <= end_date]
        
        if not start_balance:
            temp_df = calculate_balance(temp_df, principal)
        else:
            temp_df = calculate_balance(temp_df, start_balance)
         
        start_balance = temp_df.iloc[-1]['balance']
        
        df = df.merge(
            temp_df, 
            how='left',
            on=['payment_date', 'payment_month', 'payment_year']
        )
        
        df['interest_rate'] = df['interest_rate_y'].fillna(df['interest_rate_x'])
        df.drop(['interest_rate_x', 'interest_rate_y'], axis=1, inplace=True)
        df['payment'] = df['payment_y'].fillna(df['payment_x'])
        df.drop(['payment_x', 'payment_y'], axis=1, inplace=True)
        df['principal'] = df['principal_y'].fillna(df['principal_x'])
        df.drop(['principal_x', 'principal_y'], axis=1, inplace=True)
        df['interest'] = df['interest_y'].fillna(df['interest_x'])
        df.drop(['interest_x', 'interest_y'], axis=1, inplace=True)
        df['balance'] = df['balance_y'].fillna(df['balance_x'])
        df.drop(['balance_x', 'balance_y'], axis=1, inplace=True)
        
    df.drop(['payment_month', 'payment_year'], axis=1, inplace=True)
    # output
    print(df.to_markdown())