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

long_term_rate = 0.08
short_term_rate = 0.02
cpf_oa_rate = 0.025
cpf_sa_rate = 0.04
cpf_ma_rate = 0.04

# Button to generate the table
if st.button("Generate Portfolio Summary"):
    # Calculate number of years to project
    years = future_age - current_age + 1
    ages = list(range(current_age, future_age + 1))
    
    # Calculate portfolio value adjusted for growth each year
    adj_cash = [current_cash * ((1 + short_term_rate) ** i) for i in range(years)]
    adj_cash_eq = [current_equities_in_cash * ((1 + long_term_rate) ** i) for i in range(years)]
    adj_srs_eq = [current_equities_in_srs * ((1 + long_term_rate) ** i) for i in range(years)]
    adj_oa = [current_cpf_oa * ((1 + cpf_oa_rate) ** i) for i in range(years)]
    adj_sa = [current_cpf_sa * ((1 + cpf_sa_rate) ** i) for i in range(years)]
    adj_ma = [current_cpf_ma * ((1 + cpf_ma_rate) ** i) for i in range(years)]
    adj_total = [a+b+c+d+e+f for a,b,c,d,e,f in zip(adj_cash,adj_cash_eq,adj_srs_eq,adj_oa,adj_sa,adj_ma)]

    # Calculate planned contributions each year
    add_cpf_sa_top_up = [cpf_sa_top_up if current_age <= i+current_age <= 35 else 0 for i in range(years)] # hardcode to 35 for now
    add_srs = [srs_top_up if current_age <= i+current_age <= fire_age else 0 for i in range(years)] # until stop working
    add_cpf_oa = [1564 if current_age <= i+current_age <= fire_age else 0 for i in range(years)] # hardcode for now
    add_cpf_sa = [408 if current_age <= i+current_age <= fire_age else 0 for i in range(years)] # hardcode for now
    add_cpf_ma = [544 if current_age <= i+current_age <= fire_age else 0 for i in range(years)] # hardcode for now
    add_long_term_cash = [long_term_inv if current_age <= i+current_age <= fire_age else 0 for i in range(years)] # remaining after expenses
    add_short_term_cash = [short_term_inv if current_age <= i+current_age <= fire_age else 0 for i in range(years)] # remaining after expenses

    # Calculate ending balances for each year

    # Create a DataFrame to display the results
    data = {'Age': ages, 
            'Cash': adj_cash,
            'Equities in Cash': adj_cash_eq,
            'Equities in SRS': adj_srs_eq,
            'CPF OA': adj_oa,
            'CPF SA': adj_sa,
            'CPF MA': adj_ma,
            'Total Portfolio Value': adj_total,
            'E/E CPF OA': add_cpf_oa,
            'E/E CPF SA': add_cpf_sa,
            'E/E CPF MA': add_cpf_ma,
            'Top up CPF SA': add_cpf_sa_top_up,
            'Top up SRS': add_srs,
            'LT Cash Investments ': add_long_term_cash,
            'ST Cash Investments': add_short_term_cash,
            }
    df = pd.DataFrame(data)
    columns_with_beginning = pd.MultiIndex.from_product([["Beginning Balances"], df.columns[1:8]])
    columns_with_contributions = pd.MultiIndex.from_product([["Planned Contributions"], df.columns[8:]])
    df.columns = pd.MultiIndex.from_tuples([("","Age")] + list(columns_with_beginning)+list(columns_with_contributions))
    
    # Display the table
    st.write("Projected Portfolio value (with assumptions)")
    pd.set_option('display.precision', 0)
    df = df.round(0)

    st.dataframe(df,use_container_width=False)