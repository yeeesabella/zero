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

st.header("Your basic info")
col1, col2 = st.columns(2)

# Taking range input from the user
with col1:
    current_age = st.number_input("Current Age", min_value=0, value=30)
    current_expenses = st.number_input("Annual Expenses", value=48000)
    
with col2:
    future_age = st.number_input("Mortality Age", min_value=current_age + 1, value=95)
    current_income = st.number_input("Annual Income", value=100000)

st.header("Your current portfolio")
col3, col4 = st.columns(2)

# Taking range input from the user
with col3:
    current_cash = st.number_input("Cash", min_value=0)
    current_equities_in_srs = st.number_input("Equities in SRS", value=0)
    current_cpf_sa = st.number_input("CPF SA", value=0)
    current_others = st.number_input("Others", value=0)
    
with col4:
    current_equities_in_cash = st.number_input("Equities in Cash", min_value=0)
    current_cpf_oa = st.number_input("CPF OA", value=0)
    current_cpf_ma = st.number_input("CPF MA", value=0)

# Inflation rate
inflation_rate = 0.03
income_rate = 0.03

# Button to generate the table
if st.button("Calculate Future Summary"):
    # Calculate number of years to project
    years = future_age - current_age + 1
    ages = list(range(current_age, future_age + 1))
    
    # Calculate expenses adjusted for inflation each year
    income = [current_income * ((1 + income_rate) ** i) for i in range(years)]
    expenses = [current_expenses * ((1 + inflation_rate) ** i) for i in range(years)]

    # Create a DataFrame to display the results
    data = {'Age': ages, 'Expenses': expenses,'Income': income}
    df = pd.DataFrame(data)
    
    # Display the table
    st.write("Projected Cash flows and Portfolio value (with assumptions)")
    st.dataframe(df.style.format({"Income": "${:,.2f}","Expenses": "${:,.2f}"}))
