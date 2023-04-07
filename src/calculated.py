#!/usr/bin/env python3
# TODO description

import numpy_financial as npf
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def get_interest_rate():
    """ Get env interest rate percentage and convert to decimal percentage

    Raises:
        ValueError: Env interest rate does not exist or is not numeric

    Returns:
        float: Interest rate as decimal percentage
    """
    try:
        return float(os.getenv('INTEREST_RATE'))/100
    except ValueError:
        raise LookupError('Interest rate not set')

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

def build_df(start_date: datetime, years: int, payments_per_year: int):
    """ Init dataframe and populate with payment dates

    Args:
        start_date (datetime): Start date or mortgage
        years (int): Duration of mortgage in years
        payments_per_year (int): Number of mortgage repayments per year

    Returns:
        df (pd.DataFrame): Initialised dataframe
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