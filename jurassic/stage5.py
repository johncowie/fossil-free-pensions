
import formula
import spreadsheet
import utils
import json

def load_oil_categories(ss_api):
    return ss_api.get_records('Categories', 'Oil')

def load_coal_categories(ss_api):
    return ss_api.get_records('Categories', 'Coal')

# files => list of dicts with <id> and <name> keys
# output => dict of <name>:<records>
def gather_input_data(api, folder, inclusion_list=None):
    d = {}
    for f in api.find_files_in_folder(folder):
        if (inclusion_list==None or f['name'] in inclusion_list):
            print('gathering data for: ' + f['name'])
            ss = api.open_by_id(f['id'])
            d[f['name']] = ss.worksheet('Full Data').get_all_records()
            print("Current size: " + str(len(d)))
    return d

def worksheet_index(ss, worksheet_name):
    ws = ss.worksheets()
    for i in range(0, len(ws)):
        print(ws[i].id)
        print(ws[i].title)
        if ws[i].title == worksheet_name:
            return i
    return -1

def create_spreadsheet(api, parent_folder_id, name, tabs, emails, can_edit=False):
    print("Creating spreadsheet for: " + name + "...")
    ss = api.create_spreadsheet(name, parent_folder_id)
    for email in emails:
        api.add_permission(ss.id, email, False, can_edit)
    for tab in tabs:
        tab_data = tabs[tab]
        wsi = api.create_worksheet(ss.id, tab, tab_data)
        api.set_cells(ss.id, wsi, tab_data)
    print("Created spreadsheet for: " + name + "")

def prepare_folder(api, folder_name, retry):
    if retry:
        return api.find_folder(folder_name)['id']
    else:
        api.delete_files_in_folder(folder_name)
        return api.create_directory(folder_name)

def read_stage3(api, input_folder_name, inclusion_list=None):
    oil = load_oil_categories(api)
    coal = load_coal_categories(api)
    input_data = gather_input_data(api, input_folder_name, inclusion_list)
    return all_spreadsheets(input_data, oil, coal)

def write_stage5(api, output_data, folder_name, emails, retry):
    folder_id = prepare_folder(api, folder_name, retry)

    for email in emails:
        api.add_permission(folder_id, email, False, False)

    output_sheets = output_data['sheets']
    output_metadata = output_data['metadata']
    for mkey in output_metadata:
        tabs = output_metadata[mkey]
        create_spreadsheet(api, folder_id, mkey, tabs, emails, True)
    for skey in output_sheets:
        tabs = output_sheets[skey]
        create_spreadsheet(api, folder_id, skey, tabs, emails, True)


def create_all_spreadsheets_sf(api, input_folder_name, folder_name, emails, retry, inclusion_list=None):
    output = read_stage3(api, input_folder_name, inclusion_list)
    write_stage5(api, output, folder_name, emails, retry)

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
    return { 'Full Data':full_data_tab(fund_name, init_data, oil_patterns, coal_patterns)
            ,'Fossil Fuel Direct Investments':direct_investments_tab()}

def gen_metadata(investments, oil_patterns, coal_patterns):
    headers = ['Holding', 'Oil Match', 'Coal Match']
    rows = []
    for investment in investments:
        cell_id = 'A' + str(len(rows) + 2)
        row = [investment
              ,formula.pattern_match(cell_id, oil_patterns)
              ,formula.pattern_match(cell_id, coal_patterns)]
        rows.append(row)
    return {'METADATA-MATCHES':{'Matches': [headers] + rows}}


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
        oil_formula = ""
        coal_formula = ""
        if(cellId == 'B2'):
            oil_formula=formula.pattern_match('B2:B', oil_patterns)
            coal_formula=formula.pattern_match('B2:B', coal_patterns)
        row = [fund_name
              ,init_row['Description of Holding']
              ,init_row['Sub-category/Classification']
              ,oil_formula
              ,coal_formula
              ,formula.verification(rowNo, 'D', 'E', 'B')
              ,formula.fossil_amount(rowNo, 'F', 'H')
              ,spreadsheet.number_cell(init_row['Amount'])
              ]
        rows.append(row)

    return rows

def direct_investments_tab():
    return [ ['Name', "='Full Data'!A2"]
            ,['Total holdings', "=SUM('Full Data'!H1:H)"]
            ,['Total fossil fuel holdings', "=SUM('Full Data'!G2:G)"]
            ,['Percentage in fossil fuels', spreadsheet.percentage("=B3/B2")]
            ,[]
            ,[]
            ,['Top 10 Fossil Fuel Holdings', '', '', '', 'This excludes holdings through pooled funds - see next sheet']
            ,['Amount', 'Percentage', 'Name']
            ,[formula.largest_value('Full Data', 'G', 1), spreadsheet.percentage("=A9/$B$2"), formula.largest_value_name('Full Data', 'G', 'F', 1)]
            ,[formula.largest_value('Full Data', 'G', 2), spreadsheet.percentage("=A10/$B$2"), formula.largest_value_name('Full Data', 'G', 'F', 2)]
            ,[formula.largest_value('Full Data', 'G', 3), spreadsheet.percentage("=A11/$B$2"), formula.largest_value_name('Full Data', 'G', 'F', 3)]
            ,[formula.largest_value('Full Data', 'G', 4), spreadsheet.percentage("=A12/$B$2"), formula.largest_value_name('Full Data', 'G', 'F', 4)]
            ,[formula.largest_value('Full Data', 'G', 5), spreadsheet.percentage("=A13/$B$2"), formula.largest_value_name('Full Data', 'G', 'F', 5)]
            ,[formula.largest_value('Full Data', 'G', 6), spreadsheet.percentage("=A14/$B$2"), formula.largest_value_name('Full Data', 'G', 'F', 6)]
            ,[formula.largest_value('Full Data', 'G', 7), spreadsheet.percentage("=A15/$B$2"), formula.largest_value_name('Full Data', 'G', 'F', 7)]
            ,[formula.largest_value('Full Data', 'G', 8), spreadsheet.percentage("=A16/$B$2"), formula.largest_value_name('Full Data', 'G', 'F', 8)]
            ,[formula.largest_value('Full Data', 'G', 9), spreadsheet.percentage("=A17/$B$2"), formula.largest_value_name('Full Data', 'G', 'F', 9)]
            ,[formula.largest_value('Full Data', 'G', 10), spreadsheet.percentage("=A18/$B$2"), formula.largest_value_name('Full Data', 'G', 'F', 10)]
            ]

# test_batch_update()

## EXECUTION

# emails = ['john.a.cowie@gmail.com']
#
# api = spreadsheet.Spreadsheet('creds/stage5_3.json')
# # api.delete_files_in_folder('Stage 5 test')
# # api.delete_files_in_folder('Stage 5')
# # create_all_spreadsheets_sf(api, 'Stage 3 JC created sheets', 'Stage 5', emails, False, ['Avon Pension Fund'])
# create_all_spreadsheets_sf(api, 'Stage 3 JC created sheets', 'Stage 5', emails, False)

# share all existing spreadsheets with new creds in hack.py
# use new creds to call create_all_spreadsheets_sf
