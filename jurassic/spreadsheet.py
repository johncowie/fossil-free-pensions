import gspread
import re
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds']

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

    def get_records(self, spreadsheet_name):
        return self.gc.open(spreadsheet_name).sheet1.get_all_records()

    

