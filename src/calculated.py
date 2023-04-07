#!/usr/bin/env python3
# TODO description

import numpy_financial as npf
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

interest_rate = float(os.getenv('INTEREST_RATE'))/100
years = int(os.getenv('YEARS'))
payments_per_year = int(os.getenv('PAYMENTS_PER_YEAR'))
principal = int(os.getenv('PRINCIPAL'))
start_date = datetime.strptime(os.getenv('START_DATE'), '%d/%m/%Y')

# this is for start of month, date should actually be end of month
rng = pd.date_range(start_date, periods=years * payments_per_year, freq='MS')
rng.name = "Payment_date"
df = pd.DataFrame(index=rng,columns=['payment', 'principal', 'interest', 'balance'], dtype='float')
df.reset_index(inplace=True)
df.index += 1
df.index.name = "period"

df["payment"] = npf.pmt(interest_rate/payments_per_year, years*payments_per_year, principal)
df["principal"] = npf.ppmt(interest_rate/payments_per_year, df.index, years*payments_per_year, principal)
df["interest"] = npf.ipmt(interest_rate/payments_per_year, df.index, years*payments_per_year, principal)

# calculate balance
df.loc[1, 'balance'] = principal + df.loc[1, 'payment'] # should be first period

for i in range(2, len(df)):
    df.loc[i, 'balance'] = df.loc[i-1, 'balance'] + df.loc[i, 'principal']

print(df.to_markdown())