
import formula
import spreadsheet
import utils
import json
import time

def load_oil_categories(ss_api):
    return ss_api.get_records('Categories', 'Oil')

def load_coal_categories(ss_api):
    return ss_api.get_records('Categories', 'Coal')

def include_file(filename, inclusion_list, exclusion_list):
    return (inclusion_list==None and exclusion_list==None) or (inclusion_list==None and filename not in exclusion_list) or (not inclusion_list == None and filename in inclusion_list)

def validate_sheet(data):
    if len(data['data']) > 0:
        firstData = data['data'][0]
        if (not 'Description of Holding' in firstData or
            not 'Sub-category/Classification' in firstData or
            not 'Amount' in firstData):
            print("Invalid: " + str(firstData))
            return False
    if len(data['pooled']) > 0:
        firstPooled = data['pooled'][0]
        if (not 'Name' in firstPooled or
            not 'Is Pooled? (Y/N)' in firstPooled):
            print("Invalid: " + str(firstPooled))
            return False
    return True

# files => list of dicts with <id> and <name> keys
# output => dict of <name>:<records>
def gather_input_data(api, folder, inclusion_list, exclusion_list):
    d = {}
    for f in api.find_files_in_folder(folder):
        if include_file(f['name'], inclusion_list, exclusion_list):
            print('gathering data for: ' + f['name'])
            ss = api.open_by_id(f['id'])
            data = {}
            data['data'] = ss.worksheet('Full Data').get_all_records()
            data['pooled'] = ss.worksheet('Pooled').get_all_records()
            if validate_sheet(data):
                d[f['name']] = data
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
    api.delete_spreadsheet(parent_folder_id, name)
    ss = api.create_spreadsheet(name, parent_folder_id)
    for email in emails:
        api.add_permission(ss.id, email, False, can_edit)
    for tab in tabs:
        tab_data = tab[1]
        wsi = api.create_worksheet(ss.id, tab[0], tab_data)
        api.set_cells(ss.id, wsi, tab_data)
    print("Created spreadsheet for: " + name + "")
    return ss.id

def prepare_folder(api, folder_name, reset):
    if reset:
        api.delete_files_in_folder(folder_name)
        return api.create_directory(folder_name)
    else:
        folder = api.find_folder(folder_name)
        if folder == None:
            return api.create_directory(folder_name)
        else:
            return folder['id']
        

def read_stage3(api, input_folder_name, inclusion_list=None, exclusion_list=None):
    oil = load_oil_categories(api)
    coal = load_coal_categories(api)
    input_data = gather_input_data(api, input_folder_name, inclusion_list, exclusion_list)
    return (input_data, oil, coal)

# data = (input_data, oil, coal)
def process_stage3(data):
    return all_spreadsheets(data[0], data[1], data[2])

def write_stage5(api, progress, output_data, folder_name, emails, retry):
    folder_id = prepare_folder(api, folder_name, retry)

    for email in emails:
        api.add_permission(folder_id, email, False, True)

    output_sheets = output_data['sheets']
    output_metadata = output_data['metadata']
    # for mkey in output_metadata:
    #     tabs = output_metadata[mkey]
    #     sid = create_spreadsheet(api, folder_id, mkey, tabs, emails, True)
    #     api.transfer_ownership(sid, 'john.a.cowie@gmail.com')
    pro = progress.get_list()
    for skey in output_sheets:
        tabs = output_sheets[skey]
        if skey in pro:
            print("Skipping " + skey + " as it's already been done")
        else:
            try:
                create_spreadsheet(api, folder_id, skey, tabs, emails, True)
                pro = progress.add_to_list(skey)
            except Exception as e:
                print("Error creating: " + skey)
                print(e)
        # time.sleep(1)


def create_all_spreadsheets_sf(api, input_folder_name, folder_name, emails, retry, inclusion_list=None):
    output = read_stage3(api, input_folder_name, inclusion_list)
    write_stage5(api, output, folder_name, emails, retry)

def investments_from_input_data(data):
    investments = set()
    for row in data['data']:
      investments.add(row['Description of Holding'])
    return investments
    
def all_spreadsheets(init_data, oil_patterns, coal_patterns):
    output_sheets = {}
    investments = set()
    for key in init_data:
        print("Processing: " + key)
        output_sheets[key] = gen_spreadsheet(key, init_data[key], oil_patterns, coal_patterns)
        # keep running total of all names - FIXME maybe just have function that pulls this out of loaded data
        for row in init_data[key]['data']:
            investments.add(row['Description of Holding'])
    investments = list(investments)
    investments.sort()
    return {'sheets':output_sheets, 'metadata':gen_metadata(investments, oil_patterns, coal_patterns)}

def fracking_all_spreadsheets(init_data, fracking_patterns):
    output_sheets = {}
    investments = set()
    for key in init_data:
        print("Processing: " + key)
        output_sheets[key] = fracking_gen_spreadsheet(key, init_data[key], fracking_patterns)
        # keep running total of all names - FIXME maybe just have function that pulls this out of loaded data
        for row in init_data[key]['data']:
            investments.add(row['Description of Holding'])
    investments = list(investments)
    investments.sort()
    return {'sheets':output_sheets, 'metadata':fracking_gen_metadata(investments, fracking_patterns)}    

def gen_spreadsheet(fund_name, init_data, oil_patterns, coal_patterns):
    investments_length = len(list(filter(is_valid_input_row, init_data['data'])))
    return [ ('Full Data', full_data_tab(fund_name, init_data['data'], oil_patterns, coal_patterns))
            ,('Fossil Fuel Direct Investments', direct_investments_tab())
            ,('Pooled Funds & Total Fossil Fuels', pooled_data_tab(init_data['pooled'], investments_length))
            ,('Overview figures', overview_tab())]

def fracking_gen_spreadsheet(fund_name, init_data, fracking_patterns):
    investments_length = len(list(filter(is_valid_input_row, init_data['data'])))
    return [ ('Full Data', fracking_full_data_tab(fund_name, init_data['data'], fracking_patterns))
            ,('Fracking Direct Investments', fracking_direct_investments_tab())
            ,('Pooled Funds & Total Fracking', fracking_pooled_data_tab(init_data['pooled'], investments_length))
            ,('Overview figures', fracking_overview_tab())]    

def gen_metadata(investments, oil_patterns, coal_patterns):
    headers = ['Holding', 'Oil Match', 'Coal Match']
    rows = []
    for investment in investments:
        cell_id = 'A' + str(len(rows) + 2)
        row = [investment, None, None]
        if(cell_id == 'A2'):
            row = [investment
                  ,formula.pattern_match('A2:A', oil_patterns)
                  ,formula.pattern_match('A2:A', coal_patterns)]
        rows.append(row)
    return [('Matches', [headers] + rows)]

def fracking_gen_metadata(investments, fracking_patterns):
    headers = ['Holding', 'Fracking Match']
    rows = []
    for investment in investments:
        cell_id = 'A' + str(len(rows) + 2)
        row = [investment, None]
        if(cell_id == 'A2'):
            row = [investment
                  ,formula.pattern_match('A2:A', fracking_patterns)]
        rows.append(row)
    return [ ('Matches', [headers] + rows)
            ,('Matched', [['=FILTER(Matches!A2:B, Matches!B2:B <> "0")']])]


def overview_tab():
    row1 = ['Local Authority',
            'Pension Fund',
            'Total Fund Amount',
            'Fossil Fuel Investment',
            '% Fossil Fuels',
            'Direct Fossil Fuel Investment',
            'Indirect Fossil Fuel Investment',
            "companies[0]['name']",
            "companies[0]['value']",
            "companies[1]['name']",
            "companies[1]['value']",
            "companies[2]['name']",
            "companies[2]['value']",
            "companies[3]['name']",
            "companies[3]['value']",
            "companies[4]['name']",
            "companies[4]['value']",
            "post_content",
            "google_doc_url"
            ]
    row2 = [ ""
            ,""
            ,"='Pooled Funds & Total Fossil Fuels'!F24"
            ,"='Pooled Funds & Total Fossil Fuels'!F23"
            ,"='Pooled Funds & Total Fossil Fuels'!G23"
            ,"='Pooled Funds & Total Fossil Fuels'!F21"
            ,"='Pooled Funds & Total Fossil Fuels'!F20"
            ,"='Fossil Fuel Direct Investments'!C9"
            ,"='Fossil Fuel Direct Investments'!A9"
            ,"='Fossil Fuel Direct Investments'!C10"
            ,"='Fossil Fuel Direct Investments'!A10"
            ,"='Fossil Fuel Direct Investments'!C11"
            ,"='Fossil Fuel Direct Investments'!A11"
            ,"='Fossil Fuel Direct Investments'!C12"
            ,"='Fossil Fuel Direct Investments'!A12"
            ,"='Fossil Fuel Direct Investments'!C13"
            ,"='Fossil Fuel Direct Investments'!A13"
            ,""
            ,""]
    return [row1, row2]

def fracking_overview_tab():
    row1 = ['Local Authority',
            'Pension Fund',
            'Total Fund Amount',
            'Fracking Investment',
            '% Fracking',
            'Direct Fracking Investment',
            'Indirect Fracking Investment',
            "companies[0]['name']",
            "companies[0]['value']",
            "companies[1]['name']",
            "companies[1]['value']",
            "companies[2]['name']",
            "companies[2]['value']",
            "companies[3]['name']",
            "companies[3]['value']",
            "companies[4]['name']",
            "companies[4]['value']",
            "post_content",
            "google_doc_url"
            ]
    row2 = [ ""
            ,""
            ,"='Pooled Funds & Total Fracking'!F24"
            ,"='Pooled Funds & Total Fracking'!F23"
            ,"='Pooled Funds & Total Fracking'!G23"
            ,"='Pooled Funds & Total Fracking'!F21"
            ,"='Pooled Funds & Total Fracking'!F20"
            ,"='Fracking Direct Investments'!C9"
            ,"='Fracking Direct Investments'!A9"
            ,"='Fracking Direct Investments'!C10"
            ,"='Fracking Direct Investments'!A10"
            ,"='Fracking Direct Investments'!C11"
            ,"='Fracking Direct Investments'!A11"
            ,"='Fracking Direct Investments'!C12"
            ,"='Fracking Direct Investments'!A12"
            ,"='Fracking Direct Investments'!C13"
            ,"='Fracking Direct Investments'!A13"
            ,""
            ,""]
    return [row1, row2]



def pooled_data_tab(pooled_matches, investment_length):
    top_bit =  [['Pooled fund estimate', spreadsheet.percentage(0.1)]
               ,[None, 'Amount', 'Percentage', 'Name', 'Pooled fund', 'Estimated fossil fuel holdings', 'in % of total holdings']
               ,[]
               ,['Total', "='Fossil Fuel Direct Investments'!B2"]]
    pooled_rows = []
    for i in range(1, 16):
        pc_formula = lambda i:"=B{0}/$B$4".format(i)
        row = [i
               , formula.largest_value('Full Data', 'H', i) if investment_length >= i else 0
               , pc_formula(i+4)
               , formula.largest_value_name('Full Data', 'H', 'B', i) if investment_length >= i else 0
               , formula.pooled_match('D5:D19', pooled_matches) if i == 1 else None
               , '=IF(E{0}="yes",B{0}*$B$1,0)'.format(i+4)
               , '=F{0}/$B$4'.format(i+4)]
        pooled_rows.append(row)
    totals = [[None, None, None, None, 'Total estimated fossil fuels in largest pooled funds', '=SUM(F5:F19)', '=SUM(G5:G19)']
             ,[None, None, None, None, 'Total direct fossil fuels', "='Fossil Fuel Direct Investments'!B3", "='Fossil Fuel Direct Investments'!B4"]
             ,[]
             ,[None, None, None, None, 'Total fossil fuels', '=F20+F21', '=G20+G21']
             ,[None, None, None, None, 'Total holdings', "='Fossil Fuel Direct Investments'!B2"]]
    return top_bit + pooled_rows + totals

def fracking_pooled_data_tab(pooled_matches, investment_length):
    top_bit =  [['Pooled fund estimate', spreadsheet.percentage(0.055)]
               ,[None, 'Amount', 'Percentage', 'Name', 'Pooled fund', 'Estimated fracking holdings', 'in % of total holdings']
               ,[]
               ,['Total', "='Fracking Direct Investments'!B2"]]
    pooled_rows = []
    for i in range(1, 16):
        pc_formula = lambda i:"=B{0}/$B$4".format(i)
        row = [i
               , formula.largest_value('Full Data', 'G', i) if investment_length >= i else 0
               , pc_formula(i+4)
               , formula.largest_value_name('Full Data', 'G', 'B', i) if investment_length >= i else 0
               , formula.pooled_match('D5:D19', pooled_matches) if i == 1 else None
               , '=IF(E{0}="yes",B{0}*$B$1,0)'.format(i+4)
               , '=F{0}/$B$4'.format(i+4)]
        pooled_rows.append(row)
    totals = [[None, None, None, None, 'Total estimated fracking in largest pooled funds', '=SUM(F5:F19)', '=SUM(G5:G19)']
             ,[None, None, None, None, 'Total direct fracking', "='Fracking Direct Investments'!B3", "='Fracking Direct Investments'!B4"]
             ,[]
             ,[None, None, None, None, 'Total fracking', '=F20+F21', '=G20+G21']
             ,[None, None, None, None, 'Total holdings', "='Fracking Direct Investments'!B2"]]
    return top_bit + pooled_rows + totals
    

def is_valid_amount(amount):
    try:
        if(type(amount) is str):
            float(amount.replace(',', ''))
            return True
        else:
            return True
    except ValueError:
        return False

def is_valid_input_row(row):
    holding = row.get('Description of Holding', '')
    amount = row.get('Amount', '')
    return holding != '' and is_valid_amount(amount)

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
        if not is_valid_input_row(init_row):
            print('SKIPPING invalid row: ' + str(init_row))
            continue
        rowNo = len(rows) + 1
        cellId = 'B'+str(rowNo)
        oil_formula = None
        coal_formula = None
        if(cellId == 'B2'):
            oil_formula=formula.pattern_match('B2:B', oil_patterns)
            coal_formula=formula.pattern_match('B2:B', coal_patterns)
        row = [fund_name
              ,init_row.get('Description of Holding', '')
              ,init_row.get('Sub-category/Classification', '')
              ,oil_formula
              ,coal_formula
              ,formula.verification(rowNo, 'D', 'E', 'B')
              ,formula.fossil_amount(rowNo, 'F', 'H')
              ,spreadsheet.number_cell(init_row.get('Amount', ''))
              ]
        rows.append(row)

    return rows

def fracking_full_data_tab(fund_name, init_data, fracking_patterns):
    headers = ['Name of Local Authority Pension Fund'
              ,'Description of Holding'
              ,'Sub-category/Classification'
              ,'Fracking Companies'
              ,'Verification'
              ,'Fracking Amounts'
              ,'All Amounts']

    rows = [headers]

    for init_row in init_data:
        if not is_valid_input_row(init_row):
            print('SKIPPING INVALID ROW: ' + str(init_row))
            continue
        rowNo = len(rows) + 1
        cellId = 'B'+str(rowNo)
        fracking_formula = None
        if(cellId == 'B2'):
            fracking_formula=formula.pattern_match('B2:B', fracking_patterns)            
        row = [fund_name
              ,init_row.get('Description of Holding', '')
              ,init_row.get('Sub-category/Classification', '')
              ,fracking_formula
              ,formula.verification_1col(rowNo, 'D', 'B')
              ,formula.fossil_amount(rowNo, 'E', 'G')
              ,spreadsheet.number_cell(init_row.get('Amount', ''))
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


def fracking_direct_investments_tab():
    return [ ['Name', "='Full Data'!A2"]
            ,['Total holdings', "=SUM('Full Data'!G1:G)"]
            ,['Total fracking holdings', "=SUM('Full Data'!F2:F)"]
            ,['Percentage in fracking', spreadsheet.percentage("=B3/B2")]
            ,[]
            ,[]
            ,['Top 10 Fracking Holdings', '', '', '', 'This excludes holdings through pooled funds - see next sheet']
            ,['Amount', 'Percentage', 'Name']
            ,[formula.largest_value('Full Data', 'F', 1), spreadsheet.percentage("=A9/$B$2"), formula.largest_value_name('Full Data', 'F', 'E', 1)]
            ,[formula.largest_value('Full Data', 'F', 2), spreadsheet.percentage("=A10/$B$2"), formula.largest_value_name('Full Data', 'F', 'E', 2)]
            ,[formula.largest_value('Full Data', 'F', 3), spreadsheet.percentage("=A11/$B$2"), formula.largest_value_name('Full Data', 'F', 'E', 3)]
            ,[formula.largest_value('Full Data', 'F', 4), spreadsheet.percentage("=A12/$B$2"), formula.largest_value_name('Full Data', 'F', 'E', 4)]
            ,[formula.largest_value('Full Data', 'F', 5), spreadsheet.percentage("=A13/$B$2"), formula.largest_value_name('Full Data', 'F', 'E', 5)]
            ,[formula.largest_value('Full Data', 'F', 6), spreadsheet.percentage("=A14/$B$2"), formula.largest_value_name('Full Data', 'F', 'E', 6)]
            ,[formula.largest_value('Full Data', 'F', 7), spreadsheet.percentage("=A15/$B$2"), formula.largest_value_name('Full Data', 'F', 'E', 7)]
            ,[formula.largest_value('Full Data', 'F', 8), spreadsheet.percentage("=A16/$B$2"), formula.largest_value_name('Full Data', 'F', 'E', 8)]
            ,[formula.largest_value('Full Data', 'F', 9), spreadsheet.percentage("=A17/$B$2"), formula.largest_value_name('Full Data', 'F', 'E', 9)]
            ,[formula.largest_value('Full Data', 'F', 10), spreadsheet.percentage("=A18/$B$2"), formula.largest_value_name('Full Data', 'F', 'E', 10)]
            ]

def fracking_summary_tab(input):
    rows = []
    for authority in input:
        overview_row = input[authority]['overview'][0]
        row = [ authority
                , input[authority]['url']
                , overview_row['Total Fund Amount']
                , overview_row['Fracking Investment']
                , overview_row['% Fracking']
                , overview_row['Direct Fracking Investment']
                , overview_row['Indirect Fracking Investment']
                , overview_row.get("companies[0]['name']")
                , overview_row.get("companies[0]['value']")
                , overview_row.get("companies[1]['name']")
                , overview_row.get("companies[1]['value']")
                , overview_row.get("companies[2]['name']")
                , overview_row.get("companies[2]['value']")
                , overview_row.get("companies[3]['name']")
                , overview_row.get("companies[3]['value']")
                , overview_row.get("companies[4]['name']")
                , overview_row.get("companies[4]['value']")
        ]
        rows.append(row)
    rows.sort()
    
    return [[ 'Local Authority Pension Funds'
                  , 'google_doc_url'
                  , 'Total Fund Amount'
                  , 'Fracking Investment'
                  , '% Fracking'
                  , 'Direct Fracking Investment'
                  , 'Estimated Indirect Fossil Fuel Investment (through pooled funds)'
                  , "companies[0]['name']"
                  , "companies[0]['value']"
                  , "companies[1]['name']"
                  , "companies[1]['value']"
                  , "companies[2]['name']"
                  , "companies[2]['value']"
                  , "companies[3]['name']"
                  , "companies[3]['value]"
                  , "companies[4]['name']"
                  , "companies[4]['value']"]
               ,[ 'Totals'
                  , ''
                  , '=SUM(C3:C)'
                  , '=SUM(D3:D)'
                  , '=D2/C2'
                  , '=SUM(F3:F)'
                  , '=SUM(G3:G)']] + rows

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
