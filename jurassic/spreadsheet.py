import gspread
import re
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build

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


class Spreadsheet:

    def __init__(self, creds_file):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
        self.gc = gspread.authorize(credentials)
        self.drive = build('drive', 'v3', credentials=credentials)
        self.sheets = build('sheets', 'v4', credentials=credentials)

    def get_records(self, spreadsheet_name):
        return self.gc.open(spreadsheet_name).sheet1.get_all_records()

    # Old version
    # def create_spreadsheet(self, title):
    #     print("Creating spreadsheet: " + title)
    #     sh = self.gc.create(title)
    #     sh.share('john.a.cowie@gmail.com', perm_type='user', role='owner', notify=False)
    #     return sh

    def delete_all_created_files(self):
        r = self.drive.files().list().execute()
        for f in r['files']:
            print("Attempting to delete: " + f['name'])
            try:
                self.drive.files().delete(fileId=f['id']).execute()
            except Exception as e:
                print("Failed to delete: " + f['name'])

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
