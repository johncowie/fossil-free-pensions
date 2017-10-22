from spreadsheet import Spreadsheet
from functools import reduce

# FIXME use batch updating to make this faster (e.g. update_cells)
# https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/batchUpdate
def replace_worksheet(worksheet, title, grid, num_rows):
    max_width = reduce(max, map(len, grid))
    worksheet.resize(max(len(grid), num_rows), max_width)
    worksheet.update_title(title)

    for y in range(0, len(grid)):
        row = grid[y]
        for x in range(0, len(row)):
            v = row[x]
            worksheet.update_cell(y+1, x+1, v)

# FIXME use batch updating to make this faster (e.g. update_cells)
def grid_to_worksheet(spreadsheet, title, grid, num_rows=0):
    max_width = reduce(max, map(len, grid))
    w = spreadsheet.add_worksheet(title, max(len(grid), num_rows), max_width)

    for y in range(0, len(grid)):
        row = grid[y]
        for x in range(0, len(row)):
            v = row[x]
            w.update_cell(y+1, x+1, v)

def make_spreadsheet(api, title):
    sh = api.create_spreadsheet(title)
    print("Populating spreadsheet: " + title)
    # grid_to_worksheet(sh, 'Explanation', [['Hello World!']])
    grid_to_worksheet(sh, 'Full Data', full_data_tab)
    # grid_to_worksheet(sh, 'Fossil Fuel Direct Investments', [['Hello World!']])
    # grid_to_worksheet(sh, 'Pooled Funds & Total Fossil Fuels', [['Hello World!']])

def make_sheets(api):
    with open('local_authorities.txt', 'r') as f:
        for l in f.readlines():
            make_spreadsheet(api, l.strip())

def delete_sheets(api):
    lines = []
    with open('local_authorities.txt', 'r') as f:
        lines = f.readlines()
    for l in lines:
        try:
            api.delete_spreadsheet(l.strip())
        except Exception as e:
            print(str(e))

def make_initial_data(api):
    directory_name = 'Go Fossil Free - Pension Funds 2017 - Initial Data'
    folder_id = api.create_directory(directory_name)
    data = [['Description of Holding', 'Sub-category/Classification', 'Amount']]
    lines = []
    with open('la_output.txt', 'r') as f:
        lines = f.readlines()
    for l in lines:
        while True:
            spreadsheet_id = None
            try:
                if spreadsheet_id:
                    api.delete_spreadsheet(l.strip())
                print("Creating spreadsheet: " + l)
                sh = api.create_spreadsheet(l.strip(), folder_id)
                spreadsheet_id = sh.id
                # Replace sheet1
                replace_worksheet(sh.sheet1, 'Full Data', data, 101)

                api.add_permission(sh.id, 'john.a.cowie@gmail.com', False, True)
                api.add_permission(sh.id, 'sarahs@platformlondon.org', False, True)
                break
            except Exception as e:
                print(e)
                print("RETRYING FOR " + l + " ...")
    api.add_permission(folder_id, 'john.a.cowie@gmail.com', True, True)
    api.add_permission(folder_id, 'sarahs@platformlondon.org', True, True)


# api.delete_all_created_files()
# make_initial_data(api)
def share_all_files(api, email):
    count = 0
    for f in api.all_files():
        count = count + 1
        if f['mimeType'] == 'application/vnd.google-apps.folder':
            api.add_permission(f['id'], email, False, True)
        else:
            api.add_permission(f['id'], email, False, True)
    print("Count: " + str(count))

# api = Spreadsheet('creds/creds.json')
# share_all_files(api, 'jura-720@jurassic-stage5-2.iam.gserviceaccount.com')

# api.create_spreadsheet_v2('Blobby')
# api.delete_all()
# delete_sheets(api)
# make_sheets(api)
