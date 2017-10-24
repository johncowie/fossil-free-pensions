import gspread
import re
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
import utils

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

def _gfloat(s):
    return float(re.sub(',', '', s))

def local_authority(record):
    return record['Local Authority']

def amount(record):
    return _gfloat(record['Amount'])

def holding(record):
    return record['Description of Holding']

percentagef = {'numberFormat':{'type': 'PERCENT'}}

def string_cell(v):
    return {'userEnteredValue': {'stringValue': v}}

def formula_cell(v):
    return {'userEnteredValue': {'formulaValue': v}}

def number_cell(v):
    n = v
    try:
        if isinstance(v, str):
            n = float(v.replace(',', ''))
        else:
            n = float(v)
        return {'userEnteredValue': {'numberValue': n}}
    except:
        return {}

def cell(v):
    if isinstance(v, str):
        if len(v) > 0 and v[0] == '=':
            return formula_cell(v)
        else:
            return string_cell(v)
    elif isinstance(v, (int, float, complex)):
        return number_cell(v)
    elif v is None:
        return {}
    else:
        return v

def formatted(c, format):
    c['userEnteredFormat'] = format
    return c

def percentage(v):
    return formatted(cell(v), percentagef)

def cells_request(sheet_id, grid):
    new_rows = []
    for r in grid:
        vs = []
        for v in r:
            vs.append(cell(v))
        new_rows.append({'values':vs})
    return {'updateCells':{
        'rows': new_rows
       ,'fields':'*'
       ,'start':{'sheetId':sheet_id, 'rowIndex':0, 'columnIndex':0}}}

class Spreadsheet:

    def __init__(self, creds_file):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
        self.gc = gspread.authorize(credentials)
        self.drive = build('drive', 'v3', credentials=credentials)
        self.sheets = build('sheets', 'v4', credentials=credentials)

    def get_records(self, spreadsheet_name, worksheet_name='Sheet1'):
        return self.gc.open(spreadsheet_name).worksheet(worksheet_name).get_all_records()

    # Old version
    # def create_spreadsheet(self, title):
    #     print("Creating spreadsheet: " + title)
    #     sh = self.gc.create(title)
    #     sh.share('john.a.cowie@gmail.com', perm_type='user', role='owner', notify=False)
    #     return sh

    def create_worksheet(self, spreadsheet_id, sheet_name, cells):
        rows = utils.grid_rows(cells)
        cols = utils.grid_cols(cells)
        # print("ROWS: " + str(rows))
        # print("COLS: " + str(cols))

        create_req = {'addSheet':{'properties':{'title':sheet_name, 'gridProperties':{'rowCount':rows, 'columnCount':cols}}}}
        body = {'requests':[create_req]}
        # print(body)
        resp = self.sheets.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
        print(resp)
        return resp['replies'][0]['addSheet']['properties']['sheetId']

    def set_cells(self, spreadsheet_id, sheet_id, cells):
        body = {'requests':[cells_request(sheet_id, cells)]}
        return self.sheets.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

    def delete_all_created_files(self):
        r = self.drive.files().list().execute()
        for f in r['files']:
            print("Attempting to delete: " + f['name'])
            try:
                self.drive.files().delete(fileId=f['id']).execute()
            except Exception as e:
                print("Failed to delete: " + f['name'])

    def all_files(self):
        r = self.drive.files().list().execute()
        return r['files']

    # returns dict -> {'id':<id>}
    def find_folder(self, folder_name):
        folder_query="mimeType='application/vnd.google-apps.folder' and name='" + folder_name + "'"
        r = self.drive.files().list(q=folder_query).execute()
        files = r['files']
        if len(files) > 0:
            return r['files'][0]
        return None

    # returns list of dicts -> {'id':<id>, 'name':<name>}
    def find_files_in_folder_by_id(self, folder_id):
        file_query = "'{0}' in parents".format(folder_id)
        r = self.drive.files().list(q=file_query, fields='files(id, name)').execute()
        return r['files']

    def find_files_in_folder(self, folder_name):
        folder = self.find_folder(folder_name)
        if folder:
            return self.find_files_in_folder_by_id(folder['id'])
        else:
            print("Folder not found: " + folder_name)
            return []

    def delete_files_in_folder(self, folder_name, delete_folder=True):
        folder = self.find_folder(folder_name)
        if folder:
            files = self.find_files_in_folder_by_id(folder['id'])
            for f in files:
                self.gc.del_spreadsheet(f['id'])
            if delete_folder:
                self.drive.files().delete(fileId=folder['id']).execute()
        else:
            print("Folder not found: " + folder_name)

    def add_permission(self, file_id, email, notify, can_edit):
        role = 'writer' if can_edit else 'reader'
        perm = {'emailAddress':email, 'type':'user', 'role':role}
        return self.drive.permissions().create(fileId=file_id, body=perm, sendNotificationEmail=notify).execute()

    def transfer_ownership(self, file_id, email):
        perm = {'emailAddress':email,'type':'user','role':'owner'}
        return self.drive.permissions().create(fileId=file_id, body=perm, transferOwnership=True).execute()

    def create_directory(self, title):
        print("Creating directory: " + title)
        folder = {'name': title,
                  'mimeType': 'application/vnd.google-apps.folder'}
        folder_res = self.drive.files().create(body=folder, fields='id, parents').execute()
        folder_id = folder_res['id']
        return folder_id

    def create_spreadsheet(self, title, folder_id=None):
        body = {'properties': {'title': title}}
        sp_res = self.sheets.spreadsheets().create(body=body).execute()
        file_id = sp_res['spreadsheetId']

        # Add to directory
        if folder_id:
            self.drive.files().update(fileId=file_id,addParents=folder_id,fields='id, parents').execute()

        sh = self.gc.open_by_key(file_id)
        return sh

    def open_by_id(self, id):
        return self.gc.open_by_key(id)

    def open(self, name):
        return self.gc.open(name)

    def delete_all_sheets(self):
        sheets = self.gc.openall()
        for s in sheets:
            print(s.id)
            # print(s.list_permissions())
            print(s.title)
            self.gc.del_spreadsheet(s.id)

    def delete_spreadsheet(self, title):
        print("Deleting spreadsheet: " + title)
        sh = self.gc.open(title)
        print("ID: " + sh.id)
        self.gc.del_spreadsheet(sh.id)
