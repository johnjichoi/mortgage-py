#!/usr/bin/env python3
# TODO description

import numpy_financial as npf
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def get_interest_rate():
    """_summary_

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    try:
        return float(os.getenv('INTEREST_RATE'))/100
    except ValueError:
        raise LookupError('Interest rate not set')

def get_years():
    """_summary_

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    try:
        return int(os.getenv('YEARS'))
    except ValueError:
        raise LookupError('Years not set')
    
def get_payments_per_year():
    """_summary_

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    try:
        return int(os.getenv('PAYMENTS_PER_YEAR'))
    except ValueError:
        raise LookupError('Payments not set')

def get_principal():
    """_summary_

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    try:
        return int(os.getenv('PRINCIPAL'))
    except ValueError:
        raise LookupError('Principal not set')

def get_start_date():
    """_summary_

    Raises:
        LookupError: _description_

    Returns:
        _type_: _description_
    """
    try:
        return datetime.strptime(os.getenv('START_DATE'), '%d/%m/%Y')
    except ValueError:
        raise LookupError('Start date not set')

def build_df(start_date: datetime, years: int, payments_per_year: int):
    """_summary_

    Args:
        start_date (datetime): _description_
        years (int): _description_
        payments_per_year (int): _description_

    Returns:
        _type_: _description_
    """
    # freq -> MS = month start, M = month end
    rng = pd.date_range(start_date, periods=years * payments_per_year, freq='M')
    rng.name = "payment_date"
    df = pd.DataFrame(index=rng,columns=['payment', 'principal', 'interest', 'balance'], dtype='float')
    df.reset_index(inplace=True)
    df.index += 1
    df.index.name = "period"
    return df
    
def calculate(interest_rate: float, payments_per_year: int, years: int, principal: int):
    """_summary_

    Args:
        interest_rate (float): _description_
        payments_per_year (int): _description_
        years (int): _description_
        principal (int): _description_

    Returns:
        _type_: _description_
    """
    # calculate payment, principal and interest
    df['payment'] = npf.pmt(interest_rate/payments_per_year, years*payments_per_year, principal)
    df['principal'] = npf.ppmt(interest_rate/payments_per_year, df.index, years*payments_per_year, principal)
    df['interest'] = npf.ipmt(interest_rate/payments_per_year, df.index, years*payments_per_year, principal)
    # calculate balance
    df.loc[1, 'balance'] = principal + df.loc[1, 'payment'] # should be first period

    for i in range(2, len(df)):
        df.loc[i, 'balance'] = df.loc[i-1, 'balance'] + df.loc[i, 'principal']

    return df

if __name__ == "__main__":
    # get environment variables
    interest_rate = get_interest_rate()
    years = get_years()
    payments_per_year = get_payments_per_year() 
    principal = get_principal()
    start_date = get_start_date()

    # build dataframe
    df = build_df(start_date, years, payments_per_year)
    
    # calculate
    df = calculate(interest_rate, payments_per_year, years, principal)
    
    # output
    print(df.to_markdown())