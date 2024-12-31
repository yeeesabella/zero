import pandas as pd
import numpy as np
from datetime import datetime


from sot import bhs_df, frs_df

# Constants
inflation_rate = 0.03
income_rate = 0.03
current_year = datetime.now().year


def generate_my_bhs_frs(current_age):
    # generate bhs, frs table based on current age
    # projected bhs 5%, frs 3.5%
    if current_age<65:
        my_bhs = int(bhs_df[bhs_df['year']==current_year]['BHS'])
    else: 
        age_65_year = current_year - current_age + 65
        my_bhs = int(bhs_df[bhs_df['year']==age_65_year]['BHS'])

    if current_age<55:
        my_brs = int(frs_df[frs_df['year']==current_year]['BRS'])
        my_brs_payout = int(frs_df[frs_df['year']==current_year]['BRS Payout'])
        my_frs = int(frs_df[frs_df['year']==current_year]['FRS'])
        my_frs_payout = int(frs_df[frs_df['year']==current_year]['FRS Payout'])
        my_ers = int(frs_df[frs_df['year']==current_year]['ERS'])
        my_ers_payout = int(frs_df[frs_df['year']==current_year]['ERS Payout'])
    else: 
        age_55_year = current_year - current_age + 55
        my_brs = int(frs_df[frs_df['year']==age_55_year]['BRS'])
        my_brs_payout = int(frs_df[frs_df['year']==age_55_year]['BRS Payout'])
        my_frs = int(frs_df[frs_df['year']==age_55_year]['FRS'])
        my_frs_payout = int(frs_df[frs_df['year']==age_55_year]['FRS Payout'])
        my_ers = int(frs_df[frs_df['year']==age_55_year]['ERS'])
        my_ers_payout = int(frs_df[frs_df['year']==age_55_year]['ERS Payout'])

    return my_bhs, my_brs, my_brs_payout, my_frs, my_frs_payout, my_ers, my_ers_payout


def project_cashflow(current_age,future_age, current_income, fire_age, is_monthly,living_expenses,insurance,taxes,allowances,mortgage,mortgage_years,custom_expenses_dict,custom_expenses_years_dict):

    if is_monthly:
        living_expenses = living_expenses*12
        insurance = insurance*12
        taxes = taxes*12
        allowances = allowances*12
        mortgage = mortgage*12

    total_mandatory_expenses = living_expenses+insurance+taxes+allowances+mortgage+sum(custom_expenses_dict.values())
        
    # Calculate number of years to project
    years = future_age - current_age + 1
    ages = list(range(current_age, future_age + 1))

    # Calculate expenses adjusted for inflation each year
    total_inflow = [current_income * ((1 + income_rate) ** i) if i <= fire_age-current_age else 0 for i in range(years)]
    adj_living_expenses = [living_expenses * ((1 + inflation_rate) ** i) for i in range(years)]
    adj_insurance = [insurance * ((1 + inflation_rate) ** i) for i in range(years)]
    adj_taxes = [taxes * ((1 + inflation_rate) ** i) if i <= fire_age-current_age else 0 for i in range(years)]
    adj_allowances = [allowances * ((1 + inflation_rate) ** i) for i in range(years)]
    adj_mortgage = [mortgage if i <= mortgage_years-1 else 0 for i in range(years)]

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
    fixed_data = {'Age': ages, 
                'Total Inflow': total_inflow,
                    'Living Expenses': adj_living_expenses,
                    'Taxes': adj_taxes,
                    'Insurance': adj_insurance,
                    'Allowances': adj_allowances,
                    'Mortgage': adj_mortgage}
    custom_data = generate_inflation_dataframe(custom_expenses_dict, custom_expenses_years_dict, years)

    fixed_df = pd.DataFrame(fixed_data)
    cashflow_df = pd.concat([fixed_df, custom_data], axis=1)
    cashflow_df["Total Outflow"] = cashflow_df.drop(columns=['Age','Total Inflow']).sum(axis=1)
    cashflow_df["Net Inflow"] = cashflow_df["Total Inflow"] - cashflow_df["Total Outflow"]
    cashflow_df = cashflow_df.set_index("Age")

    return total_mandatory_expenses, cashflow_df