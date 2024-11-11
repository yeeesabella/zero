import streamlit as st
import pandas as pd
import numpy as np

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
    cpf_contribution = st.number_input("CPF Employer+Employee Contribution", value=0)

fire_age = st.number_input("Check if I can stop work at Age...", min_value=0, value=40)

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

# st.header("What are some personal goals and plans I have made for your future?")
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

# Inflation rate
inflation_rate = 0.03
income_rate = 0.03

# Button to generate the table
if st.button("Generate Cashflow Summary"):
    # Calculate number of years to project
    years = future_age - current_age + 1
    ages = list(range(current_age, future_age + 1))
    
    # Calculate expenses adjusted for inflation each year
    total_inflow = [current_income * ((1 + income_rate) ** i) for i in range(years)]
    total_outflow = [total_mandatory_expenses * ((1 + inflation_rate) ** i) for i in range(years)]
    adj_living_expenses = [living_expenses * ((1 + inflation_rate) ** i) for i in range(years)]
    adj_insurance = [insurance * ((1 + inflation_rate) ** i) for i in range(years)]
    adj_taxes = [taxes * ((1 + inflation_rate) ** i) for i in range(years)]
    adj_allowances = [allowances * ((1 + inflation_rate) ** i) for i in range(years)]
    adj_other_expenses = [other_expenses * ((1 + inflation_rate) ** i) for i in range(years)]
    net_inflow = [a - b for a, b in zip(total_inflow, total_outflow)]

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
    # Display the table
    st.write("Projected Cash flows (with assumptions)")
    st.dataframe(df.style.format({"Total Inflow": "${:,.2f}",
                                  "Living Expenses": "${:,.2f}",
                                  "Taxes": "${:,.2f}",
                                  "Insurance": "${:,.2f}",
                                  "Allowances": "${:,.2f}",
                                  "Other Expenses": "${:,.2f}",
                                  "Total Outflow": "${:,.2f}",
                                  "Net Inflow": "${:,.2f}"}))

st.header("How will I be putting this net inflow to work?")
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

long_term_rate = 1.08
short_term_rate = 1.02
cpf_oa_rate = 1.025
cpf_sa_rate = 1.04
cpf_ma_rate = 1.04

# Button to generate the table
if st.button("Generate Portfolio Summary"):
    # Calculate number of years to project
    years = future_age - current_age + 1
    ages = list(range(current_age, future_age + 1))
    
    contribute_cpf_oa_emp = []
    contribute_cpf_sa_emp = []
    contribute_cpf_ma_emp = []
    contribute_cpf_sa_top_up = []
    contribute_srs_top_up = []
    contribute_st_inv = []
    contribute_lt_inv = []

    ending_cash = []
    ending_equities_cash = []
    ending_equities_srs = []
    ending_cpf_oa = []
    ending_cpf_sa = []
    ending_cpf_ma = []
    ending_total = []

    for age in range(current_age, future_age + 1):
        # generate beginning balances
        if current_age == age:
            ages = [current_age]
            beginning_cash = [current_cash]
            beginning_equities_cash = [current_equities_in_cash]
            beginning_equities_srs = [current_equities_in_srs]
            beginning_cpf_oa = [current_cpf_oa]
            beginning_cpf_sa = [current_cpf_sa]
            beginning_cpf_ma = [current_cpf_ma]
            beginning_total = [current_cash+current_equities_in_cash+current_equities_in_srs+current_cpf_oa+current_cpf_sa+current_cpf_ma]
            
        else:
            ages.append(age)
            beginning_cash.append(ending_cash[-1])
            beginning_equities_cash.append(ending_equities_cash[-1])
            beginning_equities_srs.append(ending_equities_srs[-1])
            beginning_cpf_oa.append(ending_cpf_oa[-1])
            beginning_cpf_sa.append(ending_cpf_sa[-1])
            beginning_cpf_ma.append(ending_cpf_ma[-1])
            beginning_total.append(ending_total[-1])
        
        # generate top up amounts based on age and working years
        if current_age <= age <= fire_age:
            cpf_oa_emp = 1564
            cpf_sa_emp = 408
            cpf_ma_emp = 544
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
        contribute_lt_inv.append(long_term_inv)

        # Generate ending balances
        ending_cash.append(beginning_cash[-1]*short_term_rate+contribute_st_inv[-1])
        ending_equities_cash.append(beginning_equities_cash[-1]*long_term_rate+contribute_lt_inv[-1])
        ending_equities_srs.append(beginning_equities_srs[-1]*long_term_rate+contribute_srs_top_up[-1])
        ending_cpf_oa.append(beginning_cpf_oa[-1]*cpf_oa_rate+contribute_cpf_oa_emp[-1])
        ending_cpf_sa.append(beginning_cpf_sa[-1]*cpf_sa_rate+contribute_cpf_sa_emp[-1]+contribute_cpf_sa_top_up[-1])
        ending_cpf_ma.append(beginning_cpf_ma[-1]*cpf_ma_rate+contribute_cpf_ma_emp[-1])
        ending_total.append(ending_cash[-1]+ending_equities_cash[-1]+ending_equities_srs[-1]+ending_cpf_oa[-1]+ending_cpf_sa[-1]+ending_cpf_ma[-1])
    
    # Create a DataFrame to display the results
    data = {'Age': ages, 
            'Cash': beginning_cash,
            'Equities in Cash': beginning_equities_cash,
            'Equities in SRS': beginning_equities_srs,
            'CPF OA': beginning_cpf_oa,
            'CPF SA': beginning_cpf_sa,
            'CPF MA': beginning_cpf_ma,
            'Total Portfolio Value': beginning_total,
            'E/E CPF OA': contribute_cpf_oa_emp,
            'E/E CPF SA': contribute_cpf_sa_emp,
            'E/E CPF MA': contribute_cpf_ma_emp,
            'Top up CPF SA': contribute_cpf_sa_top_up,
            'Top up SRS': contribute_srs_top_up,
            'LT Cash Investments ': contribute_lt_inv,
            'ST Cash Investments': contribute_st_inv,
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
    columns_with_contributions = pd.MultiIndex.from_product([["Planned Contributions"], df.columns[8:15]])
    columns_with_ending = pd.MultiIndex.from_product([["Ending Balances"], df.columns[15:]])
    df.columns = pd.MultiIndex.from_tuples([("","Age")] + list(columns_with_beginning)+list(columns_with_contributions)+list(columns_with_ending))
    
    # Remove Ending string from columns
    fixed_string = "Ending "
    columns_to_remove = [col for col in df.columns.get_level_values(1) if fixed_string in str(col)]
    new_column_names = [col.replace(fixed_string, '') if fixed_string in str(col) else col for col in df.columns.get_level_values(1)]
    new_columns = list(zip(df.columns.get_level_values(0), new_column_names))
    df.columns = pd.MultiIndex.from_tuples(new_columns)

    # Display the table
    st.write("Projected Portfolio value (with assumptions)")
    pd.set_option('display.precision', 0)
    df = df.round(0)
    df = df.set_index([("","Age")])
    df.index.name = "Age"

    st.dataframe(df)