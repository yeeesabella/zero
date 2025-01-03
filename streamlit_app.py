import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import altair as alt

from sot import bhs_df, frs_df, cpf_allocation_by_age_df
from cashflow import project_cashflow, income_rate, inflation_rate, current_year,generate_my_bhs_frs
from simulation import simulate_age

st.set_page_config(page_title="Die with Zero in SG")

st.title("Project 0️⃣")
st.write(
    """
    This is a Singapore-based tool that aims to help with the accumulation and decumulation of your portfolio, by considering Singapore-specific aspect of your financially planning such as CPF and SRS.\n
    Step 1: By providing your current age, estimated mortality age, current income and expenses, it will generate a cashflow summary for every year from now to your mortality age including years where you have stopped working. This highlights the shortfall you need to make up for in your portfolio returns when you retire.\n
    Step 2: By providing your current portfolio size and planned contributions, it projects if you could retire based on your current income and expenses, factoring in a fixed growth rate for your assets and withdrawal rules associated with CPF and SRS.\n
    - A full year by year breakdown of beginning and ending portfolio value, withdrawals, returns will be provided. \n
    Step 3: Take action! 
    - If you are able to retire at the age you have specified, this tool would inform you of how much you would have at your mortality age.
        - [WIP] Suggested plans of increasing your expenses during early years will help you achieve the goal of building more memories and ultimately, die with zero.
    - If you are unable to retire at the age you have specified, this tool would inform you of the changes you would need to make such as increasing your FIRE age, spending less or earning more.

    Hope this helps! ♡
    """
)

# Initialize session state for the buttons
if 'show_cashflow' not in st.session_state:
    st.session_state['show_cashflow'] = False
if 'show_projection' not in st.session_state:
    st.session_state['show_projection'] = False

# Function to reset button states (forces refresh when input changes)
def reset_buttons_cashflow():
    st.session_state['show_cashflow'] = False
    st.session_state['show_projection'] = False
def reset_buttons_projection():
    st.session_state['show_projection'] = False

st.header("My basic info")
col1, col2 = st.columns(2)

# Taking range input from the user
with col1:
    current_age = st.number_input("Current Age", min_value=0, value=30,on_change=lambda: reset_buttons_cashflow())
with col2:
    future_age = st.number_input("Mortality Age", min_value=current_age + 1, value=95,help="when you expect to stop planning",on_change=lambda: reset_buttons_cashflow())

is_monthly_income = st.toggle("Enter monthly amount",key="income_toggle")
col5, col6 = st.columns(2)
with col5:
    current_income = st.number_input("Take-home Income", value=0, help="include base, bonus and exclude employer+employee CPF contribution",on_change=lambda: reset_buttons_cashflow())
    if is_monthly_income:
        current_income = current_income*12
with col6:
    cpf_contribution = st.number_input("CPF Employer+Employee Contribution", min_value=0, value = 0, on_change=lambda: reset_buttons_cashflow())
    if is_monthly_income:
        cpf_contribution = cpf_contribution*12

fire_age = st.number_input("I aim to retire (FIRE) at age...", min_value=0, value=40, help="what retirement means differ for everyone. you may not stop work completely but this checks if you will need to work for money ever again",on_change=lambda: reset_buttons_cashflow())

st.header("Step 1: How much do I spend on the following mandatory expenses annually?")
is_monthly = st.toggle("Enter monthly amount",key="expense_toggle")

col3, col4 = st.columns(2)
with col3:
    living_expenses = st.number_input("Living expenses", min_value=0, value=0,on_change=lambda: reset_buttons_cashflow())
    insurance = st.number_input("Insurance", min_value=0,value=0,on_change=lambda: reset_buttons_cashflow())
with col4:
    taxes = st.number_input("Taxes", min_value=0,value=0,help="applicable only during working years",on_change=lambda: reset_buttons_cashflow())
    allowances = st.number_input("Allowances", min_value=0, value=0,on_change=lambda: reset_buttons_cashflow())

with st.container(border=True):
    m1, m2 = st.columns(2)
    with m1:
        mortgage = st.number_input("Mortgage", min_value=0, value=0,on_change=lambda: reset_buttons_cashflow())
    with m2:
        mortgage_years = st.number_input("Remaining Repayment Years",min_value = 0,on_change=lambda: reset_buttons_cashflow())


if "custom_expense_count" not in st.session_state:
    st.session_state.custom_expense_count = 0

def add_expenses():
    # st.session_state.custom_expense_count.append(len(st.session_state.custom_expense_count) + 1)
    st.session_state.custom_expense_count += 1
def remove_expenses():
    # st.session_state.custom_expense_count.pop(index)
    st.session_state.custom_expense_count -= 1

# Button to add a new component
st.button("Add custom expenses", on_click=add_expenses)

custom_expenses_dict = {}
custom_expenses_years_dict = {}

# Display dynamic components with remove buttons
for i in range(st.session_state.custom_expense_count):
    with st.expander(f"Custom Expense {i}", expanded=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            key = st.text_input("Custom Expense Name",key=f"expense_name_{i}",on_change=lambda: reset_buttons_cashflow())
            amount = st.number_input("Expense Amount",min_value = 0,key=f"expense_amt_{i}",on_change=lambda: reset_buttons_cashflow())
            years = st.number_input("Number of Years",min_value = 0,key=f"expense_years_{i}",on_change=lambda: reset_buttons_cashflow())

            if is_monthly:
                amount = amount*12
            custom_expenses_dict[key] = amount
            custom_expenses_years_dict[key] = years-1
        with col2:
            # Each component gets its own "Remove" button
            st.button("Remove", key=f"remove_expense_{i}",on_click=remove_expenses)

years = future_age - current_age + 1
ages = list(range(current_age, future_age + 1))
total_mandatory_expenses, cashflow_df = project_cashflow(current_age,future_age, current_income, fire_age, is_monthly,living_expenses,insurance,taxes,allowances,mortgage,mortgage_years,custom_expenses_dict,custom_expenses_years_dict)
my_bhs, my_brs, my_brs_payout, my_frs, my_frs_payout, my_ers, my_ers_payout = generate_my_bhs_frs(current_age)

st.write(f"Your mandatory expenses amounts to `${total_mandatory_expenses:,.0f}` annually.")
st.write(f"You have `${(current_income-total_mandatory_expenses):,.0f}` remaining.")
try:
    st.write(f"Based on these inputs, your investment/saving rate is `{(1-total_mandatory_expenses/current_income)*100:.0f}%`.")
except ZeroDivisionError:
    st.write("")

if st.button("Generate Cashflow Summary"):
    st.session_state['show_cashflow'] = True
if st.session_state['show_cashflow']:
    # Display the table
    with st.expander(f"Projected Cashflows Assumptions", expanded=False): 
        st.write("""
                    1. Annual income inflates at 3% p.a.
                    2. All expenses inflates at the same 3% p.a.
                    3. Expense for taxes stops after you stop working.

                    Note: -ve net inflow means that it needs to be compensated by portfolio returns/interests/drawdown.
                """)
    pd.set_option('display.precision', 0)
    cashflow_df = cashflow_df.round(0)
    st.dataframe(cashflow_df)

st.header("Step 2: My current portfolio and how much do I plan to contribute to each bucket while I am working?")
st.write(f"Remember: after your expenses indicated above, you have `${(current_income-total_mandatory_expenses):,.0f}` remaining. You should plan to allocate them into one or more of these buckets.")

with st.expander(f"Cash (uninvested in savings account)", expanded=True): 
    cash1, cash2, cash3 = st.columns(3)
    with cash1:
        current_cash = st.number_input("Current Amount", min_value=0, value=0, key='cash',on_change=lambda: reset_buttons_projection())
    with cash2:
        cash_growth_rate = st.number_input("Growth Rate (%)",value=2.00, key='cash_gr',on_change=lambda: reset_buttons_projection())/100+1
    with cash3:
        cash_top_up = st.number_input("Savings Account Contribution", min_value=0, value=0,on_change=lambda: reset_buttons_projection())
        st.write("*Fixed every year*")
with st.expander(f"Short-term Investments in Cash (e.g. bonds, T-bills)", expanded=True): 
    st1, st2, st3 = st.columns(3)
    with st1:
        current_short_term_in_cash = st.number_input("Current Amount", min_value=0,value=0, key='cash_short_term',on_change=lambda: reset_buttons_projection())
    with st2:
        cash_short_term_growth_rate = st.number_input("Growth Rate (%)",value=3.00, key='cash_short_term_gr',on_change=lambda: reset_buttons_projection())/100+1
    with st3:
        short_term_inv = st.number_input("Short-term Contribution", min_value=0, value=0,on_change=lambda: reset_buttons_projection())
        st.write("*Allocated in proportion to the short-term and long-term amounts every year*")
with st.expander(f"Long-term Equities in Cash (e.g. stocks, ETFs)", expanded=True): 
    lt1, lt2, lt3 = st.columns(3)
    with lt1:
        current_equities_in_cash = st.number_input("Current Amount", min_value=0,value=0, key='cash_equities',on_change=lambda: reset_buttons_projection())
    with lt2:
        cash_equities_growth_rate = st.number_input("Growth Rate (%)",value=6.00, key='cash_equities_gr',on_change=lambda: reset_buttons_projection())/100+1
    with lt3:
        long_term_inv = st.number_input("Long-term Contribution", min_value=0, value=0,on_change=lambda: reset_buttons_projection())
        st.write("*Allocated in proportion to the short-term and long-term amounts every year*")
with st.expander(f"Equities in SRS", expanded=True): 
    srs1,srs2,srs3 = st.columns(3)
    with srs1:
        current_equities_in_srs = st.number_input("Current Amount", min_value=0, value=0, key='srs_equities',on_change=lambda: reset_buttons_projection())
    with srs2:
        srs_equities_growth_rate = st.number_input("Growth Rate (%)",value=6.00, key='srs_equities_gr',on_change=lambda: reset_buttons_projection())/100+1
    with srs3:
        srs_top_up = st.number_input("SRS Top Up", min_value=0, value=0,on_change=lambda: reset_buttons_projection())
        st.write("*Fixed every year*")
with st.expander(f"CPF MA", expanded=True): 
    ma1,ma2,ma3 = st.columns(3)
    with ma1:
        current_cpf_ma = st.number_input("Current Amount", min_value=0,value=0, key='cpf_ma',on_change=lambda: reset_buttons_projection())
    with ma2:
        cpf_ma_growth_rate = st.number_input("Growth Rate (%)",value=4.00, key='cpf_ma_gr',on_change=lambda: reset_buttons_projection())/100+1
    with ma3:
        cpf_ma_top_up = st.number_input("CPF MA Cash Top Up", min_value=0, value=0,on_change=lambda: reset_buttons_projection())
        st.write("*Fixed every year*")
    st.write("Note: Any top up will happen until BHS is met for the year. Thereafter, money will be allocated to ST/LT investments based on proportion indicated above.")
with st.expander(f"CPF SA", expanded=True): 
    sa1,sa2,sa3 = st.columns(3)
    with sa1:
        current_cpf_sa = st.number_input("Current Amount", min_value=0, value=0, key='cpf_sa',on_change=lambda: reset_buttons_projection())
    with sa2:
        cpf_sa_growth_rate = st.number_input("Growth Rate (%)",value=4.00, key='cpf_sa_gr',on_change=lambda: reset_buttons_projection())/100+1
    with sa3:
        cpf_sa_top_up = st.number_input("CPF SA Cash Top Up", min_value=0, value=0,on_change=lambda: reset_buttons_projection())
        st.write("*Fixed every year*")
    st.write("Note: Any top up up will happen until FRS is met for the year. Thereafter, money will be allocated to ST/LT investments based on proportion indicated above.")
with st.expander(f"CPF OA", expanded=True): 
    oa1,oa2,oa3 = st.columns(3)
    with oa1:
        current_cpf_oa = st.number_input("Current Amount", min_value=0,value=0, key='cpf_oa',on_change=lambda: reset_buttons_projection())
    with oa2:
        cpf_oa_growth_rate = st.number_input("Growth Rate (%)",value=2.50, key='cpf_oa_gr',on_change=lambda: reset_buttons_projection())/100+1
    with oa3:
        st.write("No option to top up to OA directly.")


custom_assets_amt_dict = {}

if "custom_asset_count" not in st.session_state:
    st.session_state.custom_asset_count = 0

def add_assets():
    st.session_state.custom_asset_count += 1
    # st.session_state.custom_asset_count.append(len(st.session_state.custom_asset_count) + 1)
def remove_assets():
    st.session_state.custom_asset_count -= 1
    # st.session_state.custom_asset_count.pop(index)

# Button to add a new component
st.button("Add custom assets", on_click=add_assets)

# Display dynamic components with remove buttons
for i in range(st.session_state.custom_asset_count):
    with st.expander(f"Custom Assets {i}", expanded=True):
        col1, col2, col9, col10 = st.columns(4)
        with col1:
            key = st.text_input(f"Custom Asset Name {i}",on_change=lambda: reset_buttons_projection())
        with col2:
            amount = st.number_input(f"Asset Amount {i}",min_value = 0,on_change=lambda: reset_buttons_projection())
        with col9:
            growth_rate = st.number_input(f"Growth Rate (%) {i}",value=0.00,on_change=lambda: reset_buttons_projection())/100+1
            custom_assets_amt_dict[key] = [amount,growth_rate]
        with col10:
            # Each component gets its own "Remove" button
            st.button("Remove", key=f"remove_assets_{i}",on_click=remove_assets)

total_contribution = cash_top_up+long_term_inv+cpf_ma_top_up+short_term_inv+srs_top_up+cpf_sa_top_up
st.write(f"""You have utilised `${(cash_top_up+long_term_inv+cpf_ma_top_up+short_term_inv+srs_top_up+cpf_sa_top_up):,.0f}`.
         Amount remaining: `${(current_income-total_contribution-total_mandatory_expenses):,.0f}`.
         """)


# Button to generate the table
is_disabled = (current_income-total_contribution-total_mandatory_expenses) != 0 or (cash_top_up+long_term_inv+cpf_ma_top_up+short_term_inv+srs_top_up+cpf_sa_top_up) ==0

if st.button("Generate Portfolio Summary",disabled=is_disabled):
    st.session_state['show_projection'] = True
if is_disabled:
    st.write("Please make sure you have allocated some contributions into the buckets and the amount remaining is `$0`.")
if st.session_state['show_projection']:
    # Display the table
    with st.expander(f"Projected Portfolio Assumptions", expanded=False): 
        st.write("""
                    1. Annual income inflates at 3% p.a.
                    2. Inflation increases at 3% p.a. for all expenses.
                    3. Total Net Inflow is after Expenses and does not include E/E CPF contribution.
                    4. Planned contributions assumed to be invested at the end of the year and do not qualify for interests within the same year.
                    5. CPF Life is assumed to be under Standard Plan, starting payout at age 65, estimated for a male member. 
                    6. Withdrawal amount is after CPF life is taken into account. Withdrawal rules are in this order: 
                        - First, CPF OA if after age 55 and sufficient amount
                        - Second, SRS if after age 62 and for 10 consecutive years (transferred to Short-term Cash for unused amount), 
                        - Third, by Cash Equities
                        - Lastly, Short-term Cash and Savings
                    7. Custom assets are not added into total portfolio value because I'm not sure how it would affect the withdrawal rules... it is only indicated in the last columns for reference.
                """)
    withdrawn_from, df, withdrawal_df, max_cpf_df, first_bhs_age, first_frs_age, beginning_total, beginning_cpf_sa, beginning_cpf_ma = simulate_age(current_age,fire_age,future_age,years,custom_assets_amt_dict,current_year,current_cash,current_short_term_in_cash,current_equities_in_cash,
                 current_equities_in_srs,current_cpf_oa,current_cpf_sa,current_cpf_ma,cpf_contribution,
                 cpf_allocation_by_age_df,cash_growth_rate,cash_short_term_growth_rate,cash_equities_growth_rate,srs_equities_growth_rate,
                 cpf_oa_growth_rate,cpf_sa_growth_rate,cpf_ma_growth_rate,
                 srs_top_up,long_term_inv,short_term_inv,cpf_sa_top_up,cash_top_up,cpf_ma_top_up,
                 current_income,income_rate,list(cashflow_df["Total Outflow"]),inflation_rate,
                 my_bhs, my_brs, my_brs_payout, my_frs, my_frs_payout, my_ers, my_ers_payout)

    tab1, tab2, tab3 = st.tabs(["Table", "Chart", "References"])
    with tab1:
        st.dataframe(df)
    with tab2:
        # Plot chart
        df_selected = df.loc[:, [("Ending Balances", "Total Portfolio Value")]]
        df_selected.columns = df_selected.columns.droplevel()
        st.bar_chart(df_selected,y="Total Portfolio Value")

        st.bar_chart(withdrawal_df, x="Age",y="For Expenses")
        st.bar_chart(withdrawal_df, x="Age",y="Withdrawal Rate")
    with tab3:
        st.subheader("Your Projected BHS/FRS")
        st.write("Future BHS amount are projected at 5%. Future FRS amount are projected at 3.5%.")
        max_cpf_df = max_cpf_df.set_index("Age")
        st.dataframe(max_cpf_df)

        st.subheader("Past Basic Healthcare Sum (BHS)")
        st.write("BHS is fixed at age 65. Future BHS amount are projected at 5%.")
        st.dataframe(bhs_df)

        st.subheader("Past Full Retirement Sum (FRS)")
        st.write("FRS is fixed at age 55. Note: 2016 FRS takes 2015 numbers. Future FRS amount are projected at 3.5%, which increases payouts by 2.9% to 3.2% based on historical records.")
        st.link_button("Source of CPF Life Payouts", "https://www.mof.gov.sg/docs/librariesprovider3/budget2022/download/pdf/annexe3.pdf")
        st.dataframe(frs_df)

        st.subheader("CPF Allocation Rates by Age")
        st.dataframe(cpf_allocation_by_age_df.drop(columns=['Start Age','End Age']))
        
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
                    1. Congrats! 🎉 You have enough to drawdown on your portfolio and returns. 
                        - At age {fire_age}, you will have ${beginning_total[fire_age-current_age]:,.0f} in portfolio value. 
                        - Excluding MA and SA, you will have ${beginning_total[fire_age-current_age]-beginning_cpf_ma[fire_age-current_age]-beginning_cpf_sa[fire_age-current_age]:,.0f}.
                    2. At age {future_age}, you will have ${beginning_total[-1]:,.0f} remaining. 
                        - Excluding MA and SA, you will have ${beginning_total[-1]-beginning_cpf_ma[-1]-beginning_cpf_sa[-1]:,.0f}.
                        - {'This far exceeds the desired near-zero portfolio value. You could increase your expenses and enjoy more!' if beginning_total[-1]>500000 else ''}
                    3. {first_bhs_message} 
                        - {bhs_info_message} 
                        - {final_bhs_message}
                    4. {first_frs_message} 
                        - {frs_info_message}
                    """
        st.success(insights, icon="🔥")
        st.line_chart(df_selected)
    else: 
        insights = f"""
                    What this means...
                    1. You do not have enough to drawdown on your portfolio/returns until age {future_age} or the withdrawal rules of CPF OA and/or SRS does not permit. 
                        - At age {fire_age}, you will have ${beginning_total[fire_age-current_age]:,.0f} in portfolio value but you will face insufficient funds from age {withdrawn_from.index('INSUFFICIENT')+30}.
                        - Excluding MA and SA, you will have ${beginning_total[fire_age-current_age]-beginning_cpf_ma[fire_age-current_age]-beginning_cpf_sa[fire_age-current_age]:,.0f}.
                    2. At age {future_age}, you will have ${beginning_total[-1]:,.0f} remaining. 
                        - Excluding MA and SA, you will have ${beginning_total[-1]-beginning_cpf_ma[-1]-beginning_cpf_sa[-1]:,.0f}.
                    3. {first_bhs_message} 
                        - {bhs_info_message} 
                        - {final_bhs_message}
                    4. {first_frs_message} 
                        - {frs_info_message}
                    """
        st.warning(insights, icon="⚠️")

        
        for age in range(fire_age,future_age):
            ideal_age = 0
            ideal_age_withdrawn_from, ideal_age_df, ideal_age_withdrawal_df, ideal_age_max_cpf_df, ideal_age_first_bhs_age, ideal_age_first_frs_age, ideal_age_beginning_total, ideal_age_beginning_cpf_sa, ideal_age_beginning_cpf_ma = simulate_age(current_age,age,future_age,years,custom_assets_amt_dict,current_year,current_cash,current_short_term_in_cash,current_equities_in_cash,
                 current_equities_in_srs,current_cpf_oa,current_cpf_sa,current_cpf_ma,cpf_contribution,
                 cpf_allocation_by_age_df,cash_growth_rate,cash_short_term_growth_rate,cash_equities_growth_rate,srs_equities_growth_rate,
                 cpf_oa_growth_rate,cpf_sa_growth_rate,cpf_ma_growth_rate,srs_top_up,long_term_inv,short_term_inv,cpf_sa_top_up,cash_top_up,cpf_ma_top_up,
                 current_income,income_rate,list(cashflow_df["Total Outflow"]),inflation_rate,
                 my_bhs, my_brs, my_brs_payout, my_frs, my_frs_payout, my_ers, my_ers_payout)

            if 'INSUFFICIENT' not in ideal_age_withdrawn_from: # means can fire!
                ideal_age = age
                break
        for expense in range(total_mandatory_expenses,0,-1000):
            ideal_expense = 0
            ideal_list_expense = [expense * ((1 + inflation_rate) ** i) for i in range(years)]
            ideal_expense_withdrawn_from, ideal_expense_df, ideal_expense_withdrawal_df, ideal_expense_max_cpf_df, ideal_expense_first_bhs_age, ideal_expense_first_frs_age, ideal_expense_beginning_total, ideal_expense_beginning_cpf_sa, ideal_expense_beginning_cpf_ma = simulate_age(current_age,fire_age,future_age,years,custom_assets_amt_dict,current_year,current_cash,current_short_term_in_cash,current_equities_in_cash,
                 current_equities_in_srs,current_cpf_oa,current_cpf_sa,current_cpf_ma,cpf_contribution,
                 cpf_allocation_by_age_df,cash_growth_rate,cash_short_term_growth_rate,cash_equities_growth_rate,srs_equities_growth_rate,
                 cpf_oa_growth_rate,cpf_sa_growth_rate,cpf_ma_growth_rate,srs_top_up,long_term_inv,short_term_inv,cpf_sa_top_up,cash_top_up,cpf_ma_top_up,
                 current_income,income_rate,ideal_list_expense,inflation_rate,
                 my_bhs, my_brs, my_brs_payout, my_frs, my_frs_payout, my_ers, my_ers_payout)

            if 'INSUFFICIENT' not in ideal_expense_withdrawn_from: # means can fire!
                ideal_expense = expense
                break
        for income in range(current_income,9999999999, 1000):
            ideal_income = 0
            ideal_income_withdrawn_from, ideal_income_df, ideal_income_withdrawal_df, ideal_income_max_cpf_df, ideal_income_first_bhs_age, ideal_income_first_frs_age, ideal_income_beginning_total, ideal_income_beginning_cpf_sa, ideal_income_beginning_cpf_ma = simulate_age(current_age,fire_age,future_age,years,custom_assets_amt_dict,current_year,current_cash,current_short_term_in_cash,current_equities_in_cash,
                 current_equities_in_srs,current_cpf_oa,current_cpf_sa,current_cpf_ma,cpf_contribution,
                 cpf_allocation_by_age_df,cash_growth_rate,cash_short_term_growth_rate,cash_equities_growth_rate,srs_equities_growth_rate,
                 cpf_oa_growth_rate,cpf_sa_growth_rate,cpf_ma_growth_rate,srs_top_up,long_term_inv,short_term_inv,cpf_sa_top_up,cash_top_up,cpf_ma_top_up,
                 income,income_rate,list(cashflow_df["Total Outflow"]),inflation_rate,
                 my_bhs, my_brs, my_brs_payout, my_frs, my_frs_payout, my_ers, my_ers_payout)

            if 'INSUFFICIENT' not in ideal_income_withdrawn_from: # means can fire!
                ideal_income = income
                break
        suggestions = f"""
                        You may consider...
                        1. Increasing your retirement age from {fire_age} to age {ideal_age} (keeping your expenses and income constant) OR
                        2. Lowering your expenses from `${total_mandatory_expenses:,.0f}` now to `${ideal_expense:,.0f}` (keeping your retirement age and income constant) OR
                        3. Increasing your income from `${current_income:,.0f}` now to `${ideal_income:,.0f}` (keeping your retirement age and expenses constant). \n
                        You may find the projection figures for each of these 3 options below. 
                        """

        st.header("Step 3: How can I improve my plan?")
        st.info(suggestions, icon="💡")
        tab4, tab5, tab6 = st.tabs(["Option 1", "Option 2", "Option 3"])
        with tab4:
            st.write(f"This increases your retirement age from {fire_age} to age {ideal_age}. At age {ideal_age}, you will have ${ideal_age_beginning_total[ideal_age-current_age]:,.0f} in portfolio value. ")
            st.dataframe(ideal_age_df)
        with tab5:
            st.write(f"This reduces your expenses from `${total_mandatory_expenses:,.0f}` now to `${ideal_expense:,.0f}`, which is a reduction of {(1-ideal_expense/total_mandatory_expenses)*100:.0f}%. The reduced expenses is assumed to be allocated towards long term investments.")
            st.dataframe(ideal_expense_df)
        with tab6:
            st.write(f"This increases your income from `${current_income:,.0f}` now to `${ideal_income:,.0f}`, which is a {(ideal_income/current_income-1)*100:.0f}% increase. It is important to maintain your current level of expenses as you earn more and avoid lifestyle inflation.")
            st.dataframe(ideal_expense_df)

        df_selected = df_selected.rename(columns={'Total Portfolio Value': 'Original Projection'})

        ideal_age_df_selected = ideal_age_df.loc[:, [("Withdrawals", "Withdrawn from"),("Ending Balances", "Total Portfolio Value")]]
        ideal_age_df_selected.columns = ideal_age_df_selected.columns.droplevel()
        ideal_age_df_selected.reset_index(inplace=True)

        ideal_expense_df_selected = ideal_expense_df.loc[:, [("Withdrawals", "Withdrawn from"),("Ending Balances", "Total Portfolio Value")]]
        ideal_expense_df_selected.columns = ideal_expense_df_selected.columns.droplevel()
        ideal_expense_df_selected.reset_index(inplace=True)

        ideal_income_df_selected = ideal_income_df.loc[:, [("Withdrawals", "Withdrawn from"),("Ending Balances", "Total Portfolio Value")]]
        ideal_income_df_selected.columns = ideal_income_df_selected.columns.droplevel()
        ideal_income_df_selected.reset_index(inplace=True)

        withdrawal_df_selected = df.loc[:, [("Withdrawals", "Withdrawn from"),("Ending Balances", "Total Portfolio Value")]]
        withdrawal_df_selected.columns = withdrawal_df_selected.columns.droplevel()
        withdrawal_df_selected.reset_index(inplace=True)

        withdrawal_df_selected['Projection Type'] = 'Original'
        ideal_age_df_selected['Projection Type'] = '1. Increasing Retirement Age'
        ideal_expense_df_selected['Projection Type'] = '2. Reducing Expenses'
        ideal_income_df_selected['Projection Type'] = '3. Increasing Income'

        # Concatenate DataFrames
        cashflow_df = pd.concat(
            [withdrawal_df_selected, ideal_age_df_selected, ideal_expense_df_selected, ideal_income_df_selected],
            axis=0
        ).reset_index()
        color_scale = alt.Scale(
                domain=['Original', '1. Increasing Retirement Age', '2. Reducing Expenses', '3. Increasing Income'],
                range=['#EEE3CB', '#00A19D', '#FFB344', '#E05D5D']  # Custom color codes
                    )
        # Base line chart with color-encoded legend
        line_chart = alt.Chart(cashflow_df).mark_line().encode(
            x='Year/Age',
            y='Total Portfolio Value',
            color=alt.Color('Projection Type:N', scale=color_scale), # Legend will be based on this column
            tooltip=['Year/Age', 'Total Portfolio Value', 'Projection Type', 'Withdrawn from']
        )
        
        # Create the highlight chart for "INSUFFICIENT" points
        highlight_chart = alt.Chart(withdrawal_df_selected).mark_circle(size=100).encode(
            x='Year/Age',
            y='Total Portfolio Value',
            color=alt.condition(
                alt.datum['Withdrawn from'] == 'INSUFFICIENT',
                alt.value('red'),  # INS circles in red
                alt.value('transparent')
            ),
            tooltip=['Year/Age', 'Total Portfolio Value', 'Withdrawn from']
        )

        # Overlay the charts using alt.layer()
        combined_chart = alt.layer(line_chart, highlight_chart).properties(
            width=800,
            height=400,
            title='Comparison between Simulated Projections vs Original Projection'
        )

        # Display the combined chart
        st.altair_chart(combined_chart, use_container_width=True)