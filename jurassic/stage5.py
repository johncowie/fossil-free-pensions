
import formula

# Figure out column letters from headers?

def full_data_tab(fund_name, init_data, oil_patterns, coal_patterns):
    headers = ['Name of Local Authority Pension Fund'
              ,'Description of Holding'
              ,'Sub-category/Classification'
              ,'Oil/Gas Companies'
              ,'Coal Companies'
              ,'Verification'
              ,'Fossil Fuel Amounts'
              ,'All Amounts']

    rows = [headers]

    for init_row in init_data:
        rowNo = len(rows) + 1
        cellId = 'B'+str(rowNo)
        row = [fund_name
              ,init_row['Description of Holding']
              ,init_row['Sub-category/Classification']
              ,formula.pattern_match(cellId, oil_patterns)
              ,formula.pattern_match(cellId, coal_patterns)
              ,formula.verification(rowNo, 'D', 'E', 'B')
              ,formula.fossil_amount(rowNo, 'F', 'H')
              ,init_row['Amount']]
        rows.append(row)

    return rows
