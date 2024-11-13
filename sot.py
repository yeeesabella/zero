import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# BHS fixed at age 65
# generate BHS table
current_year = 2024
years = list(range(current_year-8, current_year + 1))
known_bhs = [49800, 52000, 54500, 57200, 60000, 63000, 66000, 68500, 71500]

data = {'year': years,
        'BHS': known_bhs
}

bhs_df = pd.DataFrame(data)

# FRS fixed at age 55. note: 2016 do not have frs, hence taking 2015 numbers instead
# generate FRS table
years = list(range(1995, 2027+1))
known_frs = [40000, 45000, 50000, 55000, 60000, 65000, 70000, 75000, 80000, 84500, 
             90000, 94600, 99600, 106000, 117000, 123000, 131000, 139000, 148000,
             155000, 161000, 161000, 166000, 171000, 176000, 181000, 186000, 192000,
             198800, 205800, 213000, 220400, 228200]
frs_data = {'year': years,
        'FRS': known_frs
}

frs_df = pd.DataFrame(frs_data)

current_age=58
if current_age<=65:
    current_year = datetime.now().year
    my_bhs = bhs_df[bhs_df['year']==current_year]['BHS']
else: 
    current_year = datetime.now().year
    age_65_year = current_year - current_age + 65
    my_bhs = bhs_df[bhs_df['year']==age_65_year]['BHS']

if current_age<=55:
    current_year = datetime.now().year
    my_frs = frs_df[frs_df['year']==current_year]['FRS']
else: 
    current_year = datetime.now().year
    age_55_year = current_year - current_age + 55
    my_frs = frs_df[frs_df['year']==age_55_year]['FRS']

print(my_bhs)
print(my_frs)