
import formula


def all_spreadsheets(init_data, oil_patterns, coal_patterns):
    output_sheets = {}
    investments = set()
    for key in init_data:
        output_sheets[key] = gen_spreadsheet(key, init_data[key], oil_patterns, coal_patterns)
        for row in init_data[key]:
            investments.add(row['Description of Holding'])
    investments = list(investments)
    investments.sort()
    return {'sheets':output_sheets, 'metadata':gen_metadata(investments, oil_patterns, coal_patterns)}

def gen_spreadsheet(fund_name, init_data, oil_patterns, coal_patterns):
    return {'Full Data':full_data_tab(fund_name, init_data, oil_patterns, coal_patterns)}

def gen_metadata(investments, oil_patterns, coal_patterns):
    headers = ['Holding', 'Oil Match', 'Coal Match']
    rows = []
    for investment in investments:
        cell_id = 'A' + str(len(rows) + 2)
        row = [investment
              ,formula.pattern_match(cell_id, oil_patterns)
              ,formula.pattern_match(cell_id, coal_patterns)]
        rows.append(row)
    return [headers] + rows


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
