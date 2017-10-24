from spreadsheet import Spreadsheet
from stage5 import create_all_spreadsheets_sf, read_stage3, write_stage5
import json

emails = ['john.a.cowie@gmail.com']

def write_data_to_file(file_name, data):
    with open(file_name, 'w') as outfile:
        json.dump(data, outfile)

def load_data_from_file(file_name):
    with open(file_name, 'r') as infile:
        return json.loads(infile.read())


api = Spreadsheet('creds/stage5_3.json')
# api.delete_files_in_folder('Stage 5 test')
# api.delete_files_in_folder('Stage 5')
# create_all_spreadsheets_sf(api, 'Stage 3 JC created sheets', 'Stage 5', emails, False, ['Avon Pension Fund'])
# create_all_spreadsheets_sf(api, 'Stage 3 JC created sheets', 'Stage 5', emails, False)
# data = read_stage3(api, 'Stage 3 JC created sheets')
# write_data_to_file('data.json', data)
data = load_data_from_file('data.json')
write_stage5(api, data, 'Stage 5', emails, False)
