import pandas as pd
import numpy as np

def simulate_age(current_age,fire_age,future_age,years,custom_assets_amt_dict,current_year,current_cash,current_equities_in_cash,
                 current_equities_in_srs,current_cpf_oa,current_cpf_sa,current_cpf_ma,my_bhs,my_frs,cpf_contribution,
                 cpf_allocation_by_age_df,cash_growth_rate,cash_equities_growth_rate,srs_equities_growth_rate,
                 cpf_oa_growth_rate,cpf_sa_growth_rate,cpf_ma_growth_rate,srs_top_up,long_term_inv,short_term_inv,cpf_sa_top_up,
                 current_income,income_rate,total_mandatory_expenses,inflation_rate):
    
    total_inflow = [current_income * ((1 + income_rate) ** i) if i <= fire_age-current_age else 0 for i in range(years)]
    total_outflow = [total_mandatory_expenses * ((1 + inflation_rate) ** i) for i in range(years)]
    net_inflow = [a - b for a, b in zip(total_inflow, total_outflow)]
    contribute_cpf_oa_emp, contribute_cpf_sa_emp, contribute_cpf_ma_emp = [], [], []
    contribute_cpf_sa_top_up, contribute_srs_top_up = [], []
    contribute_st_inv, contribute_lt_inv = [], []

    returns_cash, returns_equities_cash, returns_equities_srs = [], [], []
    returns_cpf_oa, returns_cpf_sa, returns_cpf_ma = [], [], []
    returns_total = []

    ending_cash, ending_equities_cash, ending_equities_srs = [], [], []
    ending_cpf_oa, ending_cpf_sa, ending_cpf_ma = [], [], []
    ending_total = []
    if len(custom_assets_amt_dict)>0:
        for key, value in custom_assets_amt_dict.items():
            globals()['ending_'+key] = []

    withdrawals_for_expense, withdrawals_to_cash_eq, withdrawn_from, withdrawal_rate = [], [], [], []
    max_bhs = []
    max_frs = []
    first_bhs_age,first_frs_age = [], []

    srs_withdrawal_count = 10

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
            if len(custom_assets_amt_dict)>0:
                for key, value in custom_assets_amt_dict.items():
                    globals()['beginning_'+key] = [value[0]]
                    globals()['growth_rate_'+key] = [value[1]]
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
            if len(custom_assets_amt_dict)>0:
                for key, value in custom_assets_amt_dict.items():
                    globals()['beginning_'+key].append(globals()['ending_'+key][-1])

        
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

        # Generate portfolio returns
        returns_cash.append(beginning_cash[-1]*cash_growth_rate-beginning_cash[-1])
        returns_equities_cash.append(beginning_equities_cash[-1]*cash_equities_growth_rate-beginning_equities_cash[-1])
        returns_equities_srs.append(beginning_equities_srs[-1]*srs_equities_growth_rate-beginning_equities_srs[-1])
        returns_cpf_oa.append(beginning_cpf_oa[-1]*cpf_oa_growth_rate-beginning_cpf_oa[-1])
        returns_cpf_sa.append(beginning_cpf_sa[-1]*cpf_sa_growth_rate-beginning_cpf_sa[-1])
        returns_cpf_ma.append(beginning_cpf_ma[-1]*cpf_ma_growth_rate-beginning_cpf_ma[-1])
        returns_total.append(returns_cash[-1]+returns_equities_cash[-1]+returns_equities_srs[-1]+returns_cpf_oa[-1]+returns_cpf_sa[-1]+returns_cpf_ma[-1])
        
        # Generate withdrawals, with rules
        if net_inflow[age-current_age]<0:
            withdrawals_for_expense.append(-net_inflow[age-current_age])
            # 1. CPF OA after age 55 and sufficient amount
            if age>=55 and beginning_cpf_oa[age-current_age]>2*withdrawals_for_expense[age-current_age] and withdrawn_from[-1]!='SRS':
                beginning_cpf_oa[age-current_age] = beginning_cpf_oa[age-current_age]-withdrawals_for_expense[age-current_age]
                withdrawn_from.append(f'CPF OA')
                withdrawals_to_cash_eq.append(0)
            # 3. SRS after age 62, withdraw for 10 times only, what's unused goes into cash equities
            elif age>=62 and beginning_equities_srs[age-current_age]>withdrawals_for_expense[age-current_age] and beginning_equities_srs[age-current_age]/srs_withdrawal_count>withdrawals_for_expense[age-current_age]:
                # withdraw proportionate to the number of times left
                withdrawals_to_cash_eq.append((beginning_equities_srs[age-current_age]/srs_withdrawal_count-withdrawals_for_expense[age-current_age]))
                beginning_equities_cash[age-current_age] = beginning_equities_cash[age-current_age]+(beginning_equities_srs[age-current_age]/srs_withdrawal_count-withdrawals_for_expense[age-current_age])
                beginning_equities_srs[age-current_age] = beginning_equities_srs[age-current_age]-beginning_equities_srs[age-current_age]/srs_withdrawal_count
                srs_withdrawal_count -= 1
                withdrawn_from.append('SRS')
            # 4. last srs withdrawal -> withdraw all
            elif age>=62 and beginning_equities_srs[age-current_age]<2*withdrawals_for_expense[age-current_age] and srs_withdrawal_count>0 and beginning_equities_srs[age-current_age]>0:
                beginning_equities_cash[age-current_age] = beginning_equities_cash[age-current_age]+(beginning_equities_srs[age-current_age]-withdrawals_for_expense[age-current_age])
                srs_withdrawal_count-=1
                withdrawals_to_cash_eq.append(beginning_equities_srs[age-current_age]-withdrawals_for_expense[age-current_age])
                beginning_equities_srs[age-current_age] = 0
                withdrawn_from.append('SRS')
            # 5. SRS enough for withdrawal but insufficient to divide proportionally
            elif age>=62 and beginning_equities_srs[age-current_age]>withdrawals_for_expense[age-current_age]:
                beginning_equities_srs[age-current_age] = beginning_equities_srs[age-current_age]-withdrawals_for_expense[age-current_age]
                srs_withdrawal_count-=1
                withdrawals_to_cash_eq.append(0)
                withdrawn_from.append('SRS')
            # 6. Cash otherwise
            elif beginning_equities_cash[age-current_age]>withdrawals_for_expense[age-current_age]:
                beginning_equities_cash[age-current_age] = beginning_equities_cash[age-current_age]-withdrawals_for_expense[age-current_age]
                withdrawn_from.append('Cash Equities')
                withdrawals_to_cash_eq.append(0)
            else:
                withdrawn_from.append('INSUFFICIENT')
                withdrawals_to_cash_eq.append(0)

        else: 
            withdrawals_for_expense.append(0)
            withdrawals_to_cash_eq.append(0)
            withdrawn_from.append('-')
        
        # Generate ending balances
        ending_cash.append(beginning_cash[-1]*cash_growth_rate+contribute_st_inv[-1])
        ending_equities_cash.append(beginning_equities_cash[-1]*cash_equities_growth_rate+contribute_lt_inv[-1])
        ending_equities_srs.append(beginning_equities_srs[-1]*srs_equities_growth_rate+contribute_srs_top_up[-1])

        if len(custom_assets_amt_dict)>0:
            for key, value in custom_assets_amt_dict.items():
                globals()['ending_'+key].append(globals()['beginning_'+key][-1]*globals()['growth_rate_'+key][0])
        
        # base case: MA limit overflow to SA then OA, regardless of SA limit before age 55
        if beginning_cpf_ma[-1]*cpf_ma_growth_rate+contribute_cpf_ma_emp[-1]<max_bhs[-1]: # less than bhs
            ending_cpf_ma.append(beginning_cpf_ma[-1]*cpf_ma_growth_rate+contribute_cpf_ma_emp[-1])
            if age<55 or beginning_cpf_sa[-1]*cpf_sa_growth_rate+contribute_cpf_sa_emp[-1]+contribute_cpf_sa_top_up[-1]<max_frs[-1]: # below 55 or below frs, continue as usual
                ending_cpf_sa.append(beginning_cpf_sa[-1]*cpf_sa_growth_rate+contribute_cpf_sa_emp[-1]+contribute_cpf_sa_top_up[-1])
                ending_cpf_oa.append(beginning_cpf_oa[-1]*cpf_oa_growth_rate+contribute_cpf_oa_emp[-1])
            else: # above 55 and frs hit, ma not hit yet
                ending_cpf_sa.append(max_frs[-1]) # takes frs value at 55, transferred to oa
                transfer_sa_to_oa = beginning_cpf_sa[-1]*cpf_sa_growth_rate+contribute_cpf_sa_emp[-1]+contribute_cpf_sa_top_up[-1]-max_frs[-1]
                ending_cpf_oa.append(transfer_sa_to_oa+beginning_cpf_oa[-1]*cpf_oa_growth_rate+contribute_cpf_oa_emp[-1])
        else: # exceeds bhs
            ending_cpf_ma.append(max_bhs[-1])
            first_bhs_age.append(age)
            if age<55 or beginning_cpf_sa[-1]*cpf_sa_growth_rate+contribute_cpf_sa_emp[-1]+contribute_cpf_sa_top_up[-1]<max_frs[-1]: # below 55 or below frs, ma will contribute to sa
                ending_cpf_sa.append((beginning_cpf_ma[-1]*cpf_ma_growth_rate+contribute_cpf_ma_emp[-1]-max_bhs[-1])+beginning_cpf_sa[-1]*cpf_sa_growth_rate+contribute_cpf_sa_emp[-1]+contribute_cpf_sa_top_up[-1])
                ending_cpf_oa.append(beginning_cpf_oa[-1]*cpf_oa_growth_rate+contribute_cpf_oa_emp[-1])
            else: # >=55 and frs hit, ma contribute to oa
                ending_cpf_sa.append(max_frs[-1]) # takes frs value at 55, transferred to oa
                transfer_sa_to_oa = beginning_cpf_sa[-1]*cpf_sa_growth_rate+contribute_cpf_sa_emp[-1]+contribute_cpf_sa_top_up[-1]-max_frs[-1]
                transfer_ma_to_oa = beginning_cpf_ma[-1]*cpf_ma_growth_rate+contribute_cpf_ma_emp[-1]-max_bhs[-1]
                ending_cpf_oa.append(transfer_sa_to_oa+transfer_ma_to_oa+beginning_cpf_oa[-1]*cpf_oa_growth_rate+contribute_cpf_oa_emp[-1])
        
        if beginning_cpf_sa[-1]*cpf_sa_growth_rate+contribute_cpf_sa_emp[-1]+contribute_cpf_sa_top_up[-1]>=max_frs[-1]: # max frs for the year
            first_frs_age.append(age)
        
        ending_total.append(ending_cash[-1]+ending_equities_cash[-1]+ending_equities_srs[-1]+ending_cpf_oa[-1]+ending_cpf_sa[-1]+ending_cpf_ma[-1])
    
    
    # Create a DataFrame to display the results
    withdrawal_data = {'Age': ages,
                        'For Expenses': withdrawals_for_expense,
                        'Add to Cash Equities': withdrawals_to_cash_eq,
                        'Withdrawn from': withdrawn_from,
                        'Withdrawal Rate': [a/b for a, b in zip(withdrawals_for_expense, ending_total)],
                       }
    withdrawal_df = pd.DataFrame(withdrawal_data)

    max_cpf = {'Age': ages, 
               'BHS': max_bhs,
               'FRS': max_frs,
    }
    max_cpf_df = pd.DataFrame(max_cpf)
    if len(custom_assets_amt_dict)>0:
        custom_beginning = pd.DataFrame()
        custom_ending = pd.DataFrame()
        for key, value in custom_assets_amt_dict.items():
            custom_beginning['Beginning '+key] = globals()['beginning_'+key]
            custom_ending['Ending '+key] = globals()['ending_'+key]
    data = {'Year/Age': [str(a)+'/'+str(b) for a, b in zip(years, ages)], 
            'Cash': beginning_cash,
            'Equities in Cash': beginning_equities_cash,
            'Equities in SRS': beginning_equities_srs,
            'CPF OA': beginning_cpf_oa,
            'CPF SA': beginning_cpf_sa,
            'CPF MA': beginning_cpf_ma,
            'Total Portfolio Value': beginning_total,
            'For Expenses': withdrawals_for_expense,
            'Add to Cash Eq': withdrawals_to_cash_eq,
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
            'Ending_ Cash': ending_cash,
            'Ending_ Equities in Cash': ending_equities_cash,
            'Ending_ Equities in SRS': ending_equities_srs,
            'Ending_ CPF OA': ending_cpf_oa,
            'Ending_ CPF SA': ending_cpf_sa,
            'Ending_ CPF MA': ending_cpf_ma,
            'Ending_ Total Portfolio Value': ending_total,
            }
    df = pd.DataFrame(data)
    if len(custom_assets_amt_dict)>0:
        df = pd.concat([df, custom_beginning, custom_ending], axis=1)

    columns_with_beginning = pd.MultiIndex.from_product([["Beginning Balances"], df.columns[1:8]])
    columns_with_withdrawals = pd.MultiIndex.from_product([["Withdrawals"], df.columns[8:11]])
    columns_with_mandatory = pd.MultiIndex.from_product([["Mandatory Contributions"], df.columns[11:14]])
    columns_with_contributions = pd.MultiIndex.from_product([["Planned Contributions"], df.columns[14:19]])
    columns_with_returns = pd.MultiIndex.from_product([["Portfolio Returns"], df.columns[19:26]])
    columns_with_ending = pd.MultiIndex.from_product([["Ending Balances"], df.columns[26:33]])
    if len(custom_assets_amt_dict)>0:
        columns_with_custom = pd.MultiIndex.from_product([["Custom Assets"], df.columns[33:]])
        df.columns = pd.MultiIndex.from_tuples([("","Year/Age")] + list(columns_with_beginning)+list(columns_with_withdrawals)+list(columns_with_mandatory)+list(columns_with_contributions)+list(columns_with_returns)+list(columns_with_ending)+list(columns_with_custom))
    else:
        df.columns = pd.MultiIndex.from_tuples([("","Year/Age")] + list(columns_with_beginning)+list(columns_with_withdrawals)+list(columns_with_mandatory)+list(columns_with_contributions)+list(columns_with_returns)+list(columns_with_ending))
    # Remove Ending string from columns
    fixed_string = "Ending_ "
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
    
    pd.set_option('display.precision', 0)
    df = df.round(0)
    df = df.set_index([("","Year/Age")])
    df.index.name = "Year/Age"

    return withdrawn_from, df, withdrawal_df, max_cpf_df, beginning_cpf_ma, first_bhs_age, first_frs_age, beginning_total, ending_total

