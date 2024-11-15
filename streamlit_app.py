import streamlit as st
import pandas as pd
import numpy as np
from sot import bhs_df, frs_df, cpf_allocation_by_age_df
from datetime import datetime

st.title("Project 0️⃣")
st.write(
    """
    The goal is to help with the accumulation and decumulation of your portfolio.
    This tool helps to estimate the earliest age you could retire based on your expenses, income and portfolio size.
    """
)

st.header("My basic info")
col1, col2 = st.columns(2)

# Taking range input from the user
with col1:
    current_age = st.number_input("Current Age", min_value=0, value=30)
    current_income = st.number_input("Annual Take-home Income", value=100000, help="include base, bonus and exclude employer+employee CPF contribution")

with col2:
    future_age = st.number_input("Mortality Age", min_value=current_age + 1, value=95,help="when you expect to stop planning")
    cpf_contribution = st.number_input("Annual CPF Employer+Employee Contribution", min_value=0, value = 2516*12)

fire_age = st.number_input("Check if I can retire at age...", min_value=0, value=40, help="what retirement means differ for everyone. you may not stop work completely but this checks if you will need to work for money ever again")

# generate bhs, frs table based on current age
# projected bhs 5%, frs 3.5%
if current_age<65:
    current_year = datetime.now().year
    my_bhs = int(bhs_df[bhs_df['year']==current_year]['BHS'])
else: 
    current_year = datetime.now().year
    age_65_year = current_year - current_age + 65
    my_bhs = int(bhs_df[bhs_df['year']==age_65_year]['BHS'])

if current_age<55:
    current_year = datetime.now().year
    my_frs = int(frs_df[frs_df['year']==current_year]['FRS'])
else: 
    current_year = datetime.now().year
    age_55_year = current_year - current_age + 55
    my_frs = int(frs_df[frs_df['year']==age_55_year]['FRS'])

st.header("How much do I spend on the following mandatory expenses")
col3, col4 = st.columns(2)
# Taking range input from the user
with col3:
    living_expenses = st.number_input("Living expenses", min_value=0, value=12000)
    insurance = st.number_input("Insurance", min_value=0,value=6000)
    other_expenses = st.number_input("Other mandatory expenses", min_value=0, value=0, help="include any mortgage or debts you are currently making repayments for")
    
with col4:
    taxes = st.number_input("Taxes", min_value=0,value=5000)
    allowances = st.number_input("Allowances", min_value=0, value=4800)

total_mandatory_expenses = living_expenses+insurance+taxes+allowances+other_expenses
st.write(f"Your mandatory expenses amounts to ${total_mandatory_expenses}.")
st.write(f"You have ${current_income-total_mandatory_expenses} remaining.")
st.write(f"Based on these inputs, your investment/saving rate is {(1-total_mandatory_expenses/current_income)*100}%.")

# st.header("Optional: What are some personal goals and plans I have made for my future?")
# # to do: change to use LLM smart reading
# col5, col6, col11 = st.columns(3)
# with col5:
#     travel = st.number_input("Travel budget", value=0)

# with col6:
#     from_age_cpf = st.number_input("From age", min_value=0,key="from_age_1")
#     from_age_srs = st.number_input("From age", min_value=0,key="from_age_2")
#     from_age_travel = st.number_input("From age", min_value=0,key="from_age_3")
# with col11:
#     to_age_cpf = st.number_input("To age", min_value=0,key="to_age_1")    
#     to_age_srs = st.number_input("To age", min_value=0,key="to_age_2")
#     to_age_travel = st.number_input("To age", min_value=0,key="to_age_3")
    
# total_goals_expenses = srs+cpf_top_up+travel
# st.write(f"Your goals and plans amount to ${total_goals_expenses}.")
# st.write(f"You have ${current_income-total_mandatory_expenses-total_goals_expenses} remaining.")

# Constants
inflation_rate = 0.03
income_rate = 0.03

# Calculate number of years to project
years = future_age - current_age + 1
ages = list(range(current_age, future_age + 1))

# Calculate expenses adjusted for inflation each year
total_inflow = [current_income * ((1 + income_rate) ** i) if i <= fire_age-current_age else 0 for i in range(years)]
total_outflow = [total_mandatory_expenses * ((1 + inflation_rate) ** i) for i in range(years)]
net_inflow = [a - b for a, b in zip(total_inflow, total_outflow)]
adj_living_expenses = [living_expenses * ((1 + inflation_rate) ** i) for i in range(years)]
adj_insurance = [insurance * ((1 + inflation_rate) ** i) for i in range(years)]
adj_taxes = [taxes * ((1 + inflation_rate) ** i) for i in range(years)]
adj_allowances = [allowances * ((1 + inflation_rate) ** i) for i in range(years)]
adj_other_expenses = [other_expenses * ((1 + inflation_rate) ** i) for i in range(years)]


# Create a DataFrame to display the results
data = {'Age': ages, 'Total Inflow': total_inflow,
        'Living Expenses': adj_living_expenses,
        'Taxes': adj_taxes,
        'Insurance': adj_insurance,
        'Allowances': adj_allowances,
        'Other Expenses': adj_other_expenses,
        'Total Outflow': total_outflow,
        'Net Inflow': net_inflow}
df = pd.DataFrame(data)
df = df.set_index("Age")

# Button to generate the table
if st.button("Generate Cashflow Summary"):
    # Display the table
    st.write("""
                Projected Cashflows with assumptions:
                1. Annual income inflates at 3% p.a.
                2. Inflation also increases at 3% p.a. for all expenses.
                3. Assumes no drastic changes in expenses.
                Note: -ve net inflow means that it needs to be compensated by portfolio returns/interests/drawdown.
             """)
    pd.set_option('display.precision', 0)
    df = df.round(0)
    st.dataframe(df)

st.header("How will I be putting this net inflow to work while I'm working?")
col7, col8 = st.columns(2)
with col7:
    cpf_sa_top_up = st.number_input("CPF Cash Top Up", min_value=0, value=8000)    
    long_term_inv = st.number_input("Long-term Investments", min_value=0, value=current_income-total_mandatory_expenses-8000-15300,help="assumed to be broad based index yielding 8% p.a.")
with col8:
    srs_top_up = st.number_input("SRS Top up", min_value=0, value=15300, help="assumed to be broad based index yielding 8% p.a.")
    short_term_inv = st.number_input("Short-term Investments", min_value=0, value=0,help="HYSA, bonds, T-bills")

total_expenses = total_mandatory_expenses+cpf_sa_top_up+long_term_inv+srs_top_up+short_term_inv
st.write(f"You have ${current_income-total_expenses} remaining.")
st.write("Please make sure this is $0.")


st.header("My current portfolio")
col9, col10 = st.columns(2)

# Taking range input from the user
with col9:
    current_cash = st.number_input("Cash", min_value=0, value=150000)
    current_equities_in_srs = st.number_input("Equities in SRS", min_value=0, value=50000)
    current_cpf_sa = st.number_input("CPF SA", min_value=0, value=100000)
    current_others = st.number_input("Others", min_value=0, value=100000) 
with col10:
    current_equities_in_cash = st.number_input("Equities in Cash", min_value=0,value=30000)
    current_cpf_oa = st.number_input("CPF OA", min_value=0,value=70000)
    current_cpf_ma = st.number_input("CPF MA", min_value=0,value=70000)

long_term_rate = 1.06
short_term_rate = 1.02
cpf_oa_rate = 1.025
cpf_sa_rate = 1.04
cpf_ma_rate = 1.04

# Button to generate the table
if st.button("Generate Portfolio Summary"):
    contribute_cpf_oa_emp, contribute_cpf_sa_emp, contribute_cpf_ma_emp = [], [], []
    contribute_cpf_sa_top_up, contribute_srs_top_up = [], []
    contribute_st_inv, contribute_lt_inv = [], []

    returns_cash, returns_equities_cash, returns_equities_srs = [], [], []
    returns_cpf_oa, returns_cpf_sa, returns_cpf_ma = [], [], []
    returns_total = []

    ending_cash, ending_equities_cash, ending_equities_srs = [], [], []
    ending_cpf_oa, ending_cpf_sa, ending_cpf_ma = [], [], []
    ending_total = []

    withdrawals, withdrawn_from, withdrawal_rate = [], [], []
    max_bhs = []
    max_frs = []
    first_bhs_age,first_frs_age = [], []

    for age in range(current_age, future_age + 1):
        # generate beginning balances
        if current_age == age:
            ages = [current_age]
            years = [current_year]
            beginning_cash = [current_cash]
            beginning_equities_cash = [current_equities_in_cash]
            beginning_equities_srs = [current_equities_in_srs]
            beginning_cpf_oa = [current_cpf_oa]
            beginning_cpf_sa = [current_cpf_sa]
            beginning_cpf_ma = [current_cpf_ma]
            beginning_total = [current_cash+current_equities_in_cash+current_equities_in_srs+current_cpf_oa+current_cpf_sa+current_cpf_ma]
            max_bhs = [my_bhs]
            max_frs = [my_frs]
        else:
            ages.append(age)
            years.append(current_year+(age-current_age))
            beginning_cash.append(ending_cash[-1])
            beginning_equities_cash.append(ending_equities_cash[-1])
            beginning_equities_srs.append(ending_equities_srs[-1])
            beginning_cpf_oa.append(ending_cpf_oa[-1])
            beginning_cpf_sa.append(ending_cpf_sa[-1])
            beginning_cpf_ma.append(ending_cpf_ma[-1])
            beginning_total.append(ending_total[-1])
            if age <= 65 : 
                max_bhs.append(round(my_bhs*pow(1.05,age-current_age),-2))
            else:
                max_bhs.append(max_bhs[-1])
            if age <= 55:                
                max_frs.append(round(my_frs*pow(1.035,age-current_age),-2))
            else:
                max_frs.append(max_frs[-1])

        
        # generate top up amounts based on age and working years
        if current_age <= age <= fire_age:
            cpf_oa_emp = cpf_contribution*float(cpf_allocation_by_age_df[(cpf_allocation_by_age_df['Start Age']<=age)&(cpf_allocation_by_age_df['End Age']>=age)]['OA %'])
            cpf_sa_emp = cpf_contribution*float(cpf_allocation_by_age_df[(cpf_allocation_by_age_df['Start Age']<=age)&(cpf_allocation_by_age_df['End Age']>=age)]['SA %'])
            cpf_ma_emp = cpf_contribution*float(cpf_allocation_by_age_df[(cpf_allocation_by_age_df['Start Age']<=age)&(cpf_allocation_by_age_df['End Age']>=age)]['MA %'])
            srs_top_up = srs_top_up
            long_term_inv = long_term_inv
            short_term_inv = short_term_inv
        else: 
            cpf_oa_emp = 0
            cpf_sa_emp = 0
            cpf_ma_emp = 0
            srs_top_up = 0
            long_term_inv = 0
            short_term_inv = 0
        
        if age <= 35:
            cpf_sa_top_up = cpf_sa_top_up
        else: 
            cpf_sa_top_up = 0

        contribute_cpf_oa_emp.append(cpf_oa_emp)
        contribute_cpf_sa_emp.append(cpf_sa_emp)
        contribute_cpf_ma_emp.append(cpf_ma_emp)
        contribute_srs_top_up.append(srs_top_up)
        contribute_cpf_sa_top_up.append(cpf_sa_top_up)
        contribute_st_inv.append(short_term_inv)
        # contribute_lt_inv.append(long_term_inv)
        
        # all goes to lt for now. TODO: customise based on % of remaining
        contribute_lt_inv = [a - b - c if a-b-c>0 else 0 for a, b, c in zip(net_inflow, contribute_srs_top_up, contribute_cpf_sa_top_up)]
        
        # Generate withdrawals, with sequence
        if net_inflow[age-30]<0:
            withdrawals.append(-net_inflow[age-30])
            # 1. CPF OA after age 55 and sufficient amount
            if age>=55 and beginning_cpf_oa[age-30]>withdrawals[age-30]:
                beginning_cpf_oa[age-30] = beginning_cpf_oa[age-30]-withdrawals[age-30]
                withdrawn_from.append(f'CPF OA')
            # 2. SRS after age 62
            elif age>=62 and beginning_equities_srs[age-30]>withdrawals[age-30]:
                beginning_equities_srs[age-30] = beginning_equities_srs[age-30]-withdrawals[age-30]
                withdrawn_from.append('SRS')
            # 3. Cash otherwise
            elif beginning_equities_cash[age-30]>withdrawals[age-30]:
                beginning_equities_cash[age-30] = beginning_equities_cash[age-30]-withdrawals[age-30]
                withdrawn_from.append('Cash Equities')
            else:
                withdrawn_from.append('INSUFFICIENT')

        else: 
            withdrawals.append(0)
            withdrawn_from.append('-')

        # Generate portfolio returns
        returns_cash.append(beginning_cash[-1]*short_term_rate-beginning_cash[-1])
        returns_equities_cash.append(beginning_equities_cash[-1]*long_term_rate-beginning_equities_cash[-1])
        returns_equities_srs.append(beginning_equities_srs[-1]*long_term_rate-beginning_equities_srs[-1])
        returns_cpf_oa.append(beginning_cpf_oa[-1]*cpf_oa_rate-beginning_cpf_oa[-1])
        returns_cpf_sa.append(beginning_cpf_sa[-1]*cpf_sa_rate-beginning_cpf_sa[-1])
        returns_cpf_ma.append(beginning_cpf_ma[-1]*cpf_ma_rate-beginning_cpf_ma[-1])
        returns_total.append(returns_cash[-1]+returns_equities_cash[-1]+returns_equities_srs[-1]+returns_cpf_oa[-1]+returns_cpf_sa[-1]+returns_cpf_ma[-1])
    
        # Generate ending balances
        ending_cash.append(beginning_cash[-1]*short_term_rate+contribute_st_inv[-1])
        ending_equities_cash.append(beginning_equities_cash[-1]*long_term_rate+contribute_lt_inv[-1])
        ending_equities_srs.append(beginning_equities_srs[-1]*long_term_rate+contribute_srs_top_up[-1])
        
        # base case: MA limit overflow to SA then OA, regardless of SA limit before age 55
        if beginning_cpf_ma[-1]*cpf_ma_rate+contribute_cpf_ma_emp[-1]<max_bhs[-1]: # less than bhs
            ending_cpf_ma.append(beginning_cpf_ma[-1]*cpf_ma_rate+contribute_cpf_ma_emp[-1])
            if age<55 or beginning_cpf_sa[-1]*cpf_sa_rate+contribute_cpf_sa_emp[-1]+contribute_cpf_sa_top_up[-1]<max_frs[-1]: # below 55 or below frs, continue as usual
                ending_cpf_sa.append(beginning_cpf_sa[-1]*cpf_sa_rate+contribute_cpf_sa_emp[-1]+contribute_cpf_sa_top_up[-1])
                ending_cpf_oa.append(beginning_cpf_oa[-1]*cpf_oa_rate+contribute_cpf_oa_emp[-1])
            else: # above 55 and frs hit, ma not hit yet
                ending_cpf_sa.append(max_frs[-1]) # takes frs value at 55, transferred to oa
                transfer_sa_to_oa = beginning_cpf_sa[-1]*cpf_sa_rate+contribute_cpf_sa_emp[-1]+contribute_cpf_sa_top_up[-1]-max_frs[-1]
                ending_cpf_oa.append(transfer_sa_to_oa+beginning_cpf_oa[-1]*cpf_oa_rate+contribute_cpf_oa_emp[-1])
        else: # exceeds bhs
            ending_cpf_ma.append(max_bhs[-1])
            first_bhs_age.append(age+1)
            if age<55 or beginning_cpf_sa[-1]*cpf_sa_rate+contribute_cpf_sa_emp[-1]+contribute_cpf_sa_top_up[-1]<max_frs[-1]: # below 55 or below frs, ma will contribute to sa
                ending_cpf_sa.append((beginning_cpf_ma[-1]*cpf_ma_rate+contribute_cpf_ma_emp[-1]-max_bhs[-1])+beginning_cpf_sa[-1]*cpf_sa_rate+contribute_cpf_sa_emp[-1]+contribute_cpf_sa_top_up[-1])
                ending_cpf_oa.append(beginning_cpf_oa[-1]*cpf_oa_rate+contribute_cpf_oa_emp[-1])
            else: # above 55 and frs hit, ma contribute to oa
                ending_cpf_sa.append(max_frs[-1]) # takes frs value at 55, transferred to oa
                transfer_sa_to_oa = beginning_cpf_sa[-1]*cpf_sa_rate+contribute_cpf_sa_emp[-1]+contribute_cpf_sa_top_up[-1]-max_frs[-1]
                transfer_ma_to_oa = beginning_cpf_ma[-1]*cpf_ma_rate+contribute_cpf_ma_emp[-1]-max_bhs[-1]
                ending_cpf_oa.append(transfer_sa_to_oa+transfer_ma_to_oa+beginning_cpf_oa[-1]*cpf_oa_rate+contribute_cpf_oa_emp[-1])
        if beginning_cpf_sa[-1]*cpf_sa_rate+contribute_cpf_sa_emp[-1]+contribute_cpf_sa_top_up[-1]>=max_frs[-1]: # max frs for the year
            first_frs_age.append(age+1)
        ending_total.append(ending_cash[-1]+ending_equities_cash[-1]+ending_equities_srs[-1]+ending_cpf_oa[-1]+ending_cpf_sa[-1]+ending_cpf_ma[-1])
    
    
    # Create a DataFrame to display the results
    withdrawal_data = {'Age': ages,
                        'Withdrawals': withdrawals,
                        'Withdrawn from': withdrawn_from,
                        'Withdrawal Rate': [a/b for a, b in zip(withdrawals, ending_total)],
                       }
    withdrawal_df = pd.DataFrame(withdrawal_data)

    max_cpf = {'Age': ages, 
               'BHS': max_bhs,
               'FRS': max_frs,
    }
    max_cpf_df = pd.DataFrame(max_cpf)
    
    data = {'Year/Age': [str(a)+'/'+str(b) for a, b in zip(years, ages)], 
            'Cash': beginning_cash,
            'Equities in Cash': beginning_equities_cash,
            'Equities in SRS': beginning_equities_srs,
            'CPF OA': beginning_cpf_oa,
            'CPF SA': beginning_cpf_sa,
            'CPF MA': beginning_cpf_ma,
            'Total Portfolio Value': beginning_total,
            'Withdrawals': withdrawals,
            'Withdrawn from': withdrawn_from,
            'E/E CPF OA': contribute_cpf_oa_emp,
            'E/E CPF SA': contribute_cpf_sa_emp,
            'E/E CPF MA': contribute_cpf_ma_emp,
            'Top up CPF SA': contribute_cpf_sa_top_up,
            'Top up SRS': contribute_srs_top_up,
            'LT Cash Investments ': contribute_lt_inv,
            'ST Cash Investments': contribute_st_inv,
            'Total Net Inflow': net_inflow,
            'Returns Cash': returns_cash,
            'Returns Equities in Cash': returns_equities_cash,
            'Returns Equities in SRS': returns_equities_srs,
            'Returns CPF OA': returns_cpf_oa,
            'Returns CPF SA': returns_cpf_sa,
            'Returns CPF MA': returns_cpf_ma,
            'Total Portfolio Returns': returns_total,
            'Ending Cash': ending_cash,
            'Ending Equities in Cash': ending_equities_cash,
            'Ending Equities in SRS': ending_equities_srs,
            'Ending CPF OA': ending_cpf_oa,
            'Ending CPF SA': ending_cpf_sa,
            'Ending CPF MA': ending_cpf_ma,
            'Ending Total Portfolio Value': ending_total,
            }
    df = pd.DataFrame(data)

    columns_with_beginning = pd.MultiIndex.from_product([["Beginning Balances"], df.columns[1:8]])
    columns_with_mandatory = pd.MultiIndex.from_product([["Mandatory Contributions"], df.columns[10:13]])
    columns_with_contributions = pd.MultiIndex.from_product([["Planned Contributions"], df.columns[13:18]])
    columns_with_returns = pd.MultiIndex.from_product([["Portfolio Returns"], df.columns[18:25]])
    columns_with_ending = pd.MultiIndex.from_product([["Ending Balances"], df.columns[25:]])
    df.columns = pd.MultiIndex.from_tuples([("","Year/Age")] + list(columns_with_beginning)+[("","Withdrawals"),("","Withdrawn from")]+list(columns_with_mandatory)+list(columns_with_contributions)+list(columns_with_returns)+list(columns_with_ending))
    
    # Remove Ending string from columns
    fixed_string = "Ending "
    columns_to_remove = [col for col in df.columns.get_level_values(1) if fixed_string in str(col)]
    new_column_names = [col.replace(fixed_string, '') if fixed_string in str(col) else col for col in df.columns.get_level_values(1)]
    new_columns = list(zip(df.columns.get_level_values(0), new_column_names))
    df.columns = pd.MultiIndex.from_tuples(new_columns)

    # Remove Returns string from columns
    fixed_string = "Returns "
    columns_to_remove = [col for col in df.columns.get_level_values(1) if fixed_string in str(col)]
    new_column_names = [col.replace(fixed_string, '') if fixed_string in str(col) else col for col in df.columns.get_level_values(1)]
    new_columns = list(zip(df.columns.get_level_values(0), new_column_names))
    df.columns = pd.MultiIndex.from_tuples(new_columns)
    
    # Display the table
    st.write("""
                Projected Portfolio Value with assumptions:
                1. Annual income inflates at 3% p.a.
                2. Inflation also increases at 3% p.a. for all expenses.
                3. Total Net Inflow is after Expenses and does not include E/E CPF contribution.
                4. Planned contributions assumed to be invested at the end of the year.
             """)
    
    pd.set_option('display.precision', 0)
    df = df.round(0)
    df = df.set_index([("","Year/Age")])
    df.index.name = "Year/Age"

    tab1, tab2, tab3 = st.tabs(["Table", "Chart", "Appendix"])
    with tab1:
        st.dataframe(df)
    with tab2:
        # Plot chart
        df_selected = df.loc[:, [("Ending Balances", "Total Portfolio Value")]]
        df_selected.columns = df_selected.columns.droplevel()
        st.bar_chart(df_selected)

        st.bar_chart(withdrawal_df, x="Age",y="Withdrawals")
        st.bar_chart(withdrawal_df, x="Age",y="Withdrawal Rate")
    with tab3:
        st.subheader("Your Projected BHS/FRS")
        st.write("Future BHS amount are projected at 5%. Future FRS amount are projected at 3.5%.")
        max_cpf_df = max_cpf_df.set_index("Age")
        st.dataframe(max_cpf_df)

        st.subheader("[Reference] Past Basic Healthcare Sum (BHS)")
        st.write("BHS is fixed at age 65. Future BHS amount are projected at 5%.")
        st.dataframe(bhs_df)

        st.subheader("[Reference] Past Full Retirement Sum (FRS)")
        st.write("FRS is fixed at age 55. Note: 2016 FRS takes 2015 numbers. Future FRS amount are projected at 3.5%.")
        st.dataframe(frs_df)

        st.subheader("[Reference] CPF Allocation Rates by Age")
        st.dataframe(cpf_allocation_by_age_df.drop(columns=['Start Age','End Age']))
        
    # todo: improve insights here. unlike to retire, to say at what age it will run out
    # todo: suggest increasing the age? or just run with other ages to see what is the suitable fire age.
    try:
        index = beginning_cpf_ma.index(int(max_cpf_df.loc[65]['BHS']))
        first_bhs_message = f'You will first achieve the Basic Healthcare Sum (BHS) at the beginning of age {min(first_bhs_age)}.'
        if min(first_bhs_age)<65:
            bhs_info_message = 'Note: Without additional cash top up, your MA will fall behind BHS in subsequent years as BHS is projected to increase at 5% p.a. while the interests from MA is only 4%. '
            final_bhs_message = f'You will later achieve the final BHS amount at age {str(index+30)}.'
        else:
            bhs_info_message = ''
            final_bhs_message = f'Since BHS is fixed after age 65, you will continue to meet the BHS amount after.'
    except ValueError:
        first_bhs_message = ''
        final_bhs_message = f'You will not achieve the Basic Healthcare Sum (BHS) (age 65 amount) if you retire at {fire_age}. Consider topping up to your MA with Cash or working longer.'
    
    try:
        # index = beginning_cpf_ma.index(int(max_cpf_df.loc[55]['FRS']))
        first_frs_message = f'You will first achieve the Full Retirement Sum (FRS) at the beginning of age {min(first_frs_age)}.'
        if min(first_frs_age)<55:
            frs_info_message = f'Note: You do not need to do additional top up after you have first achieved FRS as FRS is projected to increase at 3.5% p.a. and interests from SA is at 4%, sufficient to cover for the increasing FRS.'
        else:
            frs_info_message = ''
    except ValueError:
        first_frs_message = f'You will not achieve the Full Retirement Sum (FRS) (age 55 amount) if you retire at {fire_age}. Consider topping up to your SA with Cash or working longer.'
    
    if 'INSUFFICIENT' not in withdrawn_from: # can fire
        insights = f"""
                    What this means...
                    1. Congrats! 🎉 You have enough to drawdown on your portfolio and returns. At age {fire_age}, you will have ${beginning_total[fire_age-current_age]:,.0f} in portfolio value. 
                    2. At age {future_age}, you will have ${ending_total[-1]:,.0f} remaining. {'This far exceeds the desired near-zero portfolio value. You could increase your expenses and enjoy more!' if ending_total[-1]>500000 else ''}
                    3. {first_bhs_message} {bhs_info_message} {final_bhs_message}
                    4. {first_frs_message} {frs_info_message}
                    """
        st.success(insights, icon="🔥")
    else: 
        insights = f"""
                    What this means...
                    1. You do not have enough to drawdown on your portfolio/returns until age {future_age} or the withdrawal rules of CPF OA and/or SRS does not permit. At age {fire_age}, you will have ${beginning_total[fire_age-current_age]:,.0f} in portfolio value. Try increasing your income, lowering your expenses or work for longer. 
                    2. At age {future_age}, you will have ${ending_total[-1]:,.0f} remaining.
                    3. {first_bhs_message} {bhs_info_message} {final_bhs_message}
                    4. {first_frs_message} {frs_info_message}
                    """
        st.warning(insights, icon="⚠️")