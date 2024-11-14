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

# CPF allocation rates by age
age_start = [0,36,46,51,56,61,66,71]
age_end = [35,45,50,55,60,65,70,100]
age_range = ['<=35','36-45','46-50','46-55','56-60','61-65','66-70','71-100']
oa_allocation = [0.6217,0.5677,0.5136,0.4055,0.3872,0.1592,0.0607,0.08]
sa_allocation = [0.1621,0.1891,0.2162,0.3108,0.2741,0.3636,0.303,0.08]
ma_allocation = [0.2162,0.2432,0.2702,0.2837,0.3387,0.4772,0.6363,0.08]
cpf_allocation_by_age = { 'Start Age': age_start,
                         'End Age': age_end,
                         'Age Range': age_range,
                         'OA %': oa_allocation,
                         'SA %': sa_allocation,
                         'MA %': ma_allocation,
                        }

cpf_allocation_by_age_df = pd.DataFrame(cpf_allocation_by_age)