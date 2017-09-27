
from formula import pattern_match_formula

def full_data_tab(fund_name, init_data, oil_patterns, coal_patterns):
    headers = ['Name of Local Authority Pension Fund'
              ,'Description of Holding'
              ,'Sub-category/Classification'
              ,'Oil/Gas Companies'
              ,'Coal Companies'
              ,'All Amounts']

    rowNo = 2
    rows = []

    for init_row in init_data:
        cellId = 'B'+str(rowNo)
        rowNo = rowNo + 1
        row = [fund_name
              ,init_row['Description of Holding']
              ,init_row['Sub-category/Classification']
              ,pattern_match_formula(cellId, oil_patterns)
              ,pattern_match_formula(cellId, coal_patterns)
              ,init_row['Amount']]
        rows.append(row)

    return [headers] + rows
