import streamlit as st
import pandas as pd
import numpy as np
from sot import bhs_df, frs_df, cpf_allocation_by_age_df
from datetime import datetime
import streamlit as st
from simulation import simulate_age
import altair as alt


st.title("Project 0️⃣")
st.write(
    """
    The tool aims to help with the accumulation and decumulation of your portfolio.
    Step 1: By providing your current age, estimated mortality age, current income and expenses, it will generate a cashflow summary for every year from now to your mortality age including years where you have stopped working.
    Step 2: By providing your current portfolio size, this projects if you could retire based on your current income and expenses, factoring in a fixed growth rate for your assets.
    - If you are able to retire at the age you have specified, this would inform you of how much you would have at your mortality age. This aims to encourage you to spend more and die with zero.
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
    current_age = st.number_input("Current Age", min_value=0, value=0,on_change=lambda: reset_buttons_cashflow())
    current_income = st.number_input("Annual Take-home Income", value=0, help="include base, bonus and exclude employer+employee CPF contribution",on_change=lambda: reset_buttons_cashflow())

with col2:
    future_age = st.number_input("Mortality Age", min_value=current_age + 1, value=95,help="when you expect to stop planning",on_change=lambda: reset_buttons_cashflow())
    cpf_contribution = st.number_input("Annual CPF Employer+Employee Contribution", min_value=0, value = 0,on_change=lambda: reset_buttons_cashflow())

fire_age = st.number_input("I want to retire (FIRE) at age...", min_value=0, value=40, help="what retirement means differ for everyone. you may not stop work completely but this checks if you will need to work for money ever again",on_change=lambda: reset_buttons_cashflow())

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
    living_expenses = st.number_input("Living expenses", min_value=0, value=0,on_change=lambda: reset_buttons_cashflow())
    insurance = st.number_input("Insurance", min_value=0,value=0,on_change=lambda: reset_buttons_cashflow())
    # other_expenses = st.number_input("Other mandatory expenses", min_value=0, value=0, help="include any mortgage or debts you are currently making repayments for")
with col4:
    taxes = st.number_input("Taxes", min_value=0,value=0,on_change=lambda: reset_buttons_cashflow())
    allowances = st.number_input("Allowances", min_value=0, value=0,on_change=lambda: reset_buttons_cashflow())

custom_expenses_dict = {}
custom_expenses_years_dict = {}

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

# Display dynamic components with remove buttons
for i in range(st.session_state.custom_expense_count):
    with st.expander(f"Custom Expense {i}", expanded=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            key = st.text_input("Custom Expense Name",key=f"expense_name_{i}",on_change=lambda: reset_buttons_cashflow())
            amount = st.number_input("Annual Expense Amount",min_value = 0,key=f"expense_amt_{i}",on_change=lambda: reset_buttons_cashflow())
            years = st.number_input("Number of Years",min_value = 0,key=f"expense_years_{i}",on_change=lambda: reset_buttons_cashflow())
            custom_expenses_dict[key] = amount
            custom_expenses_years_dict[key] = years-1
        with col2:
            # Each component gets its own "Remove" button
            st.button("Remove", key=f"remove_expense_{i}",on_click=remove_expenses)

total_mandatory_expenses = living_expenses+insurance+taxes+allowances+sum(custom_expenses_dict.values())
st.write(f"Your mandatory expenses amounts to ${total_mandatory_expenses}.")
st.write(f"You have ${current_income-total_mandatory_expenses} remaining.")
try:
    st.write(f"Based on these inputs, your investment/saving rate is {(1-total_mandatory_expenses/current_income)*100:.0f}%.")
except ZeroDivisionError:
    st.write("")


# st.header("Optional: What are some personal goals and plans I have made for my future?")
# # to do: change to use LLM smart reading
# col5, col6, col11 = st.columns(3)
# with col5:
#     travel = st.number_input("Travel budget", value=0)
# with col6:
#     from_age_travel = st.number_input("From age", min_value=0,key="from_age_3")
# with col11:
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
adj_taxes = [taxes * ((1 + inflation_rate) ** i) if i <= fire_age-current_age else 0 for i in range(years)]
adj_allowances = [allowances * ((1 + inflation_rate) ** i) for i in range(years)]

def generate_inflation_dataframe(amount_dict, years_dict, num_rows, inflation_rate=inflation_rate):
    """
    Generate a DataFrame with amounts compounded by inflation over the years for each key.

    Parameters:
    amount_dict (dict): Dictionary with keys as item names and values as initial amounts.
    years_dict (dict): Dictionary with keys as item names and values as years to apply inflation.
    num_rows (int): Number of rows (years) to generate in the DataFrame.
    inflation_rate (float): Annual inflation rate (default is 3%).

    Returns:
    pd.DataFrame: DataFrame with keys as columns, showing compounded amounts per year.
    """
    data = {}
    
    for key in amount_dict:
        amounts = []
        for year in range(num_rows):
            if year <= years_dict[key]:  # Apply inflation within the specified number of years.
                amount = amount_dict[key] * ((1 + inflation_rate) ** year)
            else:  # Set to 0 after the specified years.
                amount = 0
            amounts.append(round(amount, 2))
        data[key] = amounts

    # Create DataFrame with only the item columns.
    df = pd.DataFrame(data)
    return df

# Create a DataFrame to display the results
fixed_data = {'Age': ages, 'Total Inflow': total_inflow,
                'Living Expenses': adj_living_expenses,
                'Taxes': adj_taxes,
                'Insurance': adj_insurance,
                'Allowances': adj_allowances}
custom_data = generate_inflation_dataframe(custom_expenses_dict, custom_expenses_years_dict, years)

total_data = {
        'Total Outflow': total_outflow,
        'Net Inflow': net_inflow}
fixed_df = pd.DataFrame(fixed_data)
total_df = pd.DataFrame(total_data)

combined_df = pd.concat([fixed_df, custom_data, total_df], axis=1)
combined_df = combined_df.set_index("Age")

if st.button("Generate Cashflow Summary"):
    st.session_state['show_cashflow'] = True
if st.session_state['show_cashflow']:
    # Display the table
    st.write("""
                Projected Cashflows with assumptions:
                1. Annual income inflates at 3% p.a.
                2. All expenses inflates at the same 3% p.a.
                3. Expense for taxes stops after you stop working.
                Note: -ve net inflow means that it needs to be compensated by portfolio returns/interests/drawdown.
             """)
    pd.set_option('display.precision', 0)
    combined_df = combined_df.round(0)
    st.dataframe(combined_df)

st.header("How will I be putting this net inflow to work while I'm working?")
col7, col8 = st.columns(2)
with col7:
    cpf_sa_top_up = st.number_input("CPF Cash Top Up", min_value=0, value=0,on_change=lambda: reset_buttons_projection())    
    # current_income-total_mandatory_expenses-8000-15300
    long_term_inv = st.number_input("Long-term Investments", min_value=0, value=0,help="assumed to be broad based index yielding 8% p.a.",on_change=lambda: reset_buttons_projection())
with col8:
    srs_top_up = st.number_input("SRS Top up", min_value=0, value=0, help="assumed to be broad based index yielding 8% p.a.",on_change=lambda: reset_buttons_projection())
    short_term_inv = st.number_input("Short-term Investments", min_value=0, value=0,help="HYSA, bonds, T-bills",on_change=lambda: reset_buttons_projection())

total_expenses = total_mandatory_expenses+cpf_sa_top_up+long_term_inv+srs_top_up+short_term_inv
st.write(f"You have ${current_income-total_expenses} remaining.")
st.write("Please make sure this is $0.")


st.header("My current portfolio")
col9, col10 = st.columns(2)

# Taking range input from the user
with col9:
    with st.expander(f"Cash (uninvested)", expanded=True): 
        current_cash = st.number_input("Amount", min_value=0, value=0, key='cash',on_change=lambda: reset_buttons_projection())
        cash_growth_rate = st.number_input("Growth Rate (%)",value=2.00, key='cash_gr',on_change=lambda: reset_buttons_projection())/100+1
    with st.expander(f"Equities in SRS", expanded=True): 
        current_equities_in_srs = st.number_input("Amount", min_value=0, value=0, key='srs_equities',on_change=lambda: reset_buttons_projection())
        srs_equities_growth_rate = st.number_input("Growth Rate (%)",value=6.00, key='srs_equities_gr',on_change=lambda: reset_buttons_projection())/100+1
    with st.expander(f"CPF SA", expanded=True): 
        current_cpf_sa = st.number_input("Amount", min_value=0, value=0, key='cpf_sa',on_change=lambda: reset_buttons_projection())
        cpf_sa_growth_rate = st.number_input("Growth Rate (%)",value=4.00, key='cpf_sa_gr',on_change=lambda: reset_buttons_projection())/100+1
with col10:
    with st.expander(f"Equities in Cash", expanded=True): 
        current_equities_in_cash = st.number_input("Amount", min_value=0,value=0, key='cash_equities',on_change=lambda: reset_buttons_projection())
        cash_equities_growth_rate = st.number_input("Growth Rate (%)",value=6.00, key='cash_equities_gr',on_change=lambda: reset_buttons_projection())/100+1
    with st.expander(f"CPF OA", expanded=True): 
        current_cpf_oa = st.number_input("Amount", min_value=0,value=0, key='cpf_oa',on_change=lambda: reset_buttons_projection())
        cpf_oa_growth_rate = st.number_input("Growth Rate (%)",value=2.50, key='cpf_oa_gr',on_change=lambda: reset_buttons_projection())/100+1
    with st.expander(f"CPF MA", expanded=True): 
        current_cpf_ma = st.number_input("Amount", min_value=0,value=0, key='cpf_ma',on_change=lambda: reset_buttons_projection())
        cpf_ma_growth_rate = st.number_input("Growth Rate (%)",value=4.00, key='cpf_ma_gr',on_change=lambda: reset_buttons_projection())/100+1


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
        col1, col2 = st.columns([4, 1])
        with col1:
            key = st.text_input(f"Custom Asset Name {i}",on_change=lambda: reset_buttons_projection())
            amount = st.number_input(f"Asset Amount {i}",min_value = 0,on_change=lambda: reset_buttons_projection())
            growth_rate = st.number_input(f"Growth Rate (%) {i}",value=0.00,on_change=lambda: reset_buttons_projection())/100+1
            custom_assets_amt_dict[key] = [amount,growth_rate]
        with col2:
            # Each component gets its own "Remove" button
            st.button("Remove", key=f"remove_assets_{i}",on_click=remove_assets)

# Button to generate the table
if st.button("Generate Portfolio Summary"):
    st.session_state['show_projection'] = True

if st.session_state['show_projection']:
    # Display the table
    st.write("""
                Projected Portfolio Value with assumptions:
                1. Annual income inflates at 3% p.a.
                2. Inflation increases at 3% p.a. for all expenses.
                3. Total Net Inflow is after Expenses and does not include E/E CPF contribution.
                4. Planned contributions assumed to be invested at the end of the year and do not qualify for interests within the same year.
                5. Withdrawal rules are in this order: first, CPF OA if after age 55 and sufficient amount, second, SRS if after age 62 and for 10 consecutive years (transferred to Cash Equities for unused amount), Cash Equities otherwise.
                6. Custom assets are not added into total portfolio value because I'm not sure how it would affect the withdrawal rules... it is only indicated in the last columns.
             """)
    withdrawn_from, df, withdrawal_df, max_cpf_df, beginning_cpf_ma, first_bhs_age, first_frs_age, beginning_total, ending_total = simulate_age(current_age,fire_age,future_age,years,custom_assets_amt_dict,current_year,current_cash,current_equities_in_cash,
                 current_equities_in_srs,current_cpf_oa,current_cpf_sa,current_cpf_ma,my_bhs,my_frs,cpf_contribution,
                 cpf_allocation_by_age_df,cash_growth_rate,cash_equities_growth_rate,srs_equities_growth_rate,
                 cpf_oa_growth_rate,cpf_sa_growth_rate,cpf_ma_growth_rate,srs_top_up,long_term_inv,short_term_inv,cpf_sa_top_up,
                 current_income,income_rate,total_mandatory_expenses,inflation_rate)

    tab1, tab2, tab3 = st.tabs(["Table", "Chart", "Appendix"])
    with tab1:
        st.dataframe(df)
    with tab2:
        # Plot chart
        df_selected = df.loc[:, [("Ending Balances", "Total Portfolio Value")]]
        df_selected.columns = df_selected.columns.droplevel()
        st.bar_chart(df_selected)

        st.bar_chart(withdrawal_df, x="Age",y="For Expenses")
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
        st.line_chart(df_selected)
    else: 
        insights = f"""
                    What this means...
                    1. You do not have enough to drawdown on your portfolio/returns until age {future_age} or the withdrawal rules of CPF OA and/or SRS does not permit. You will face insufficient funds from age {withdrawn_from.index('INSUFFICIENT')+30}. At age {fire_age}, you will have ${beginning_total[fire_age-current_age]:,.0f} in portfolio value.
                    2. At age {future_age}, you will have ${ending_total[-1]:,.0f} remaining.
                    3. {first_bhs_message} {bhs_info_message} {final_bhs_message}
                    4. {first_frs_message} {frs_info_message}
                    """
        st.warning(insights, icon="⚠️")
        
        for age in range(fire_age,future_age):
            ideal_age = 0
            ideal_age_withdrawn_from, ideal_age_df, ideal_age_withdrawal_df, ideal_age_max_cpf_df, ideal_age_beginning_cpf_ma, ideal_age_first_bhs_age, ideal_age_first_frs_age, ideal_age_beginning_total, ideal_age_ending_total = simulate_age(current_age,age,future_age,years,custom_assets_amt_dict,current_year,current_cash,current_equities_in_cash,
                 current_equities_in_srs,current_cpf_oa,current_cpf_sa,current_cpf_ma,my_bhs,my_frs,cpf_contribution,
                 cpf_allocation_by_age_df,cash_growth_rate,cash_equities_growth_rate,srs_equities_growth_rate,
                 cpf_oa_growth_rate,cpf_sa_growth_rate,cpf_ma_growth_rate,srs_top_up,long_term_inv,short_term_inv,cpf_sa_top_up,
                 current_income,income_rate,total_mandatory_expenses,inflation_rate)

            if 'INSUFFICIENT' not in ideal_age_withdrawn_from: # means can fire!
                ideal_age = age
                break
        for expense in range(total_mandatory_expenses,0,-1000):
            ideal_expense = 0
            ideal_expense_withdrawn_from, ideal_expense_df, ideal_expense_withdrawal_df, ideal_expense_max_cpf_df, ideal_expense_beginning_cpf_ma, ideal_expense_first_bhs_age, ideal_expense_first_frs_age, ideal_expense_beginning_total, ideal_expense_ending_total = simulate_age(current_age,fire_age,future_age,years,custom_assets_amt_dict,current_year,current_cash,current_equities_in_cash,
                 current_equities_in_srs,current_cpf_oa,current_cpf_sa,current_cpf_ma,my_bhs,my_frs,cpf_contribution,
                 cpf_allocation_by_age_df,cash_growth_rate,cash_equities_growth_rate,srs_equities_growth_rate,
                 cpf_oa_growth_rate,cpf_sa_growth_rate,cpf_ma_growth_rate,srs_top_up,long_term_inv,short_term_inv,cpf_sa_top_up,
                 current_income,income_rate,expense,inflation_rate)

            if 'INSUFFICIENT' not in ideal_expense_withdrawn_from: # means can fire!
                ideal_expense = expense
                break
        for income in range(current_income,9999999999, 1000):
            ideal_income = 0
            ideal_income_withdrawn_from, ideal_income_df, ideal_income_withdrawal_df, ideal_income_max_cpf_df, ideal_income_beginning_cpf_ma, ideal_income_first_bhs_age, ideal_income_first_frs_age, ideal_income_beginning_total, ideal_income_ending_total = simulate_age(current_age,fire_age,future_age,years,custom_assets_amt_dict,current_year,current_cash,current_equities_in_cash,
                 current_equities_in_srs,current_cpf_oa,current_cpf_sa,current_cpf_ma,my_bhs,my_frs,cpf_contribution,
                 cpf_allocation_by_age_df,cash_growth_rate,cash_equities_growth_rate,srs_equities_growth_rate,
                 cpf_oa_growth_rate,cpf_sa_growth_rate,cpf_ma_growth_rate,srs_top_up,long_term_inv,short_term_inv,cpf_sa_top_up,
                 income,income_rate,total_mandatory_expenses,inflation_rate)

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
        combined_df = pd.concat(
            [withdrawal_df_selected, ideal_age_df_selected, ideal_expense_df_selected, ideal_income_df_selected],
            axis=0
        ).reset_index()
        color_scale = alt.Scale(
                domain=['Original', '1. Increasing Retirement Age', '2. Reducing Expenses', '3. Increasing Income'],
                range=['#EEE3CB', '#00A19D', '#FFB344', '#E05D5D']  # Custom color codes
                    )
        # Base line chart with color-encoded legend
        line_chart = alt.Chart(combined_df).mark_line().encode(
            x='Year/Age',
            y='Total Portfolio Value',
            color=alt.Color('Projection Type:N', scale=color_scale), # Legend will be based on this column
            tooltip=['Year/Age', 'Total Portfolio Value', 'Projection Type']
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