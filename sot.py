import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# BHS fixed at age 65
# generate BHS table
current_year = datetime.now().year
years = list(range(current_year-9, current_year + 1))
known_bhs = [49800, 52000, 54500, 57200, 60000, 63000, 66000, 68500, 71500, 75500]

data = {'year': years,
        'BHS': known_bhs
}

bhs_df = pd.DataFrame(data)

# FRS fixed at age 55. note: 2016 do not have frs, hence taking 2015 numbers instead
# generate FRS and payout
years = list(range(1995, 2027+1))
known_frs = [40000, 45000, 50000, 55000, 60000, 65000, 70000, 75000, 80000, 84500, 
             90000, 94600, 99600, 106000, 117000, 123000, 131000, 139000, 148000, 155000, 
             161000, 161000, 166000, 171000, 176000, 181000, 186000, 192000, 198800, 205800, 
             213000, 220400, 228200]
known_brs = [round(x / 2,-2) for x in known_frs]
known_ers = [round(x / 2 * 3,-2) for x in known_frs]
brs_payout = [400,410,420,430,440,450,460,470,480,490,
              500,520,540,560,580,600,620,640,660,680,
              700,720,740,760,780,800,820,850,870,900,
              930,950,980]
frs_payout = [700,720,740,760,780,800,820,850,880,910,
              940,970,1000,1030,1060,1090,1120,1150,1190,1230,
              1270,1310,1350,1390,1430,1470,1520,1570,1620,1670,
              1730,1780,1840]
ers_payout = [1020,1050,1080,1110,1140,1180,1220,1260,1300,1340,
              1380,1420,1460,1500,1550,1600,1650,1700,1750,1800,
              1860,1920,1980,2040,2100,2160,2230,2300,2370,2450,
              2530,2610,2690]
frs_data = {'year': years,
        'BRS': known_brs,
        'BRS Payout': brs_payout,
        'FRS': known_frs,
        'FRS Payout': frs_payout,
        'ERS': known_ers,
        'ERS Payout': ers_payout
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


# IRAS tax bracket for SRS Withdrawal
def calculate_tax(income):
    # Tax brackets and rates for Singapore (2023)
    tax_brackets = [
        (20000, 0),
        (30000, 0.02),  # 0-20,000
        (40000, 0.035),  # 20,001-30,000
        (80000, 0.07),  # 30,001-40,000
        (120000, 0.115),  # 40,001-80,000
        (160000, 0.15),  # 80,001-120,000
        (200000, 0.18),  # 120,001-160,000
        (240000, 0.19),  # 160,001-200,000
        (280000, 0.195),  # 200,001-240,000
        (320000, 0.20),  # 240,001-280,000
        (500000, 0.22),  # 280,001-320,000
        (1000000, 0.23),  # 320,001-500,000
        (float('inf'), 0.24)  # 1m and above
    ]

    income = income/2
    tax_payable = 0
    prev_limit = 0

    for limit, rate in tax_brackets:
        if income > limit:
            tax_payable += (limit - prev_limit) * rate
            prev_limit = limit
        else:
            tax_payable += (income - prev_limit) * rate
            break

    return tax_payable

def calculate_pre_tax(post_tax_amount, tolerance=1e-6):
    # Initial bounds for bisection
    low = post_tax_amount
    high = post_tax_amount * 2  # Start with an upper bound of 2 times y (adjust if necessary)

    while high - low > tolerance:
        mid = (low + high) / 2
        tax = calculate_tax(mid)
        post_tax_income = mid - tax

        if post_tax_income < post_tax_amount:
            low = mid
        else:
            high = mid

    return (low + high) / 2