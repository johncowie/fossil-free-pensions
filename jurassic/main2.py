from spreadsheet import Spreadsheet
from progress import FileList
from stage5 import create_all_spreadsheets_sf, read_stage3, write_stage5, process_stage3
import json

emails = ['john.a.cowie@gmail.com',
          'anna@platformlondon.org',
          'anna.galkina.tation@gmail.com',
          "sarahshoraka77@gmail.com"]
#
# emails = ['john.a.cowie@gmail.com']

def write_data_to_file(file_name, data):
    with open(file_name, 'w') as outfile:
        json.dump(data, outfile)

def load_data_from_file(file_name):
    with open(file_name, 'r') as infile:
        return json.loads(infile.read())

def generate_url(folder_id, file_id):
    # https://docs.google.com/spreadsheets/d/1syJoVb9KOrATW0ttw4cpEf0y9ee1Zx6fm1Q-F9pt4Rw/
    return "https://docs.google.com/spreadsheets/d/{1}/".format(folder_id, file_id)

def get_urls(api, folder_name):
    folder_id = api.find_folder(folder_name)['id']
    files = api.find_files_in_folder(folder_name)
    lines = []
    for f in files:
        lines.append(f['name'] + " - " + generate_url(folder_id, f['id']))
    return lines

api = Spreadsheet('creds/stage5_3.json')
progress = FileList('progress.txt')
# api.delete_files_in_folder('Stage 5 test')
# api.delete_files_in_folder('Stage 5')
# create_all_spreadsheets_sf(api, 'Stage 3 JC created sheets', 'Stage 5', emails, False, ['Avon Pension Fund'])
# create_all_spreadsheets_sf(api, 'Stage 3 JC created sheets', 'Stage 5', emails, False)

stage3_file = 'stage3_data/2017-10-30.json'

# data = read_stage3(api, 'Stage 3 JC created sheets')
# write_data_to_file(stage3_file, data)


# data = process_stage3(load_data_from_file(stage3_file))
# retry = True
# write_stage5(api, progress, data, 'Stage 5', emails, retry)

# fid = api.find_folder('Stage 5')['id']
# api.delete_spreadsheet(fid, 'LB Richmond Upon Thames Pension Fund')
# api.delete_spreadsheet(fid, 'NILGOSC')
# api.delete_spreadsheet(fid, 'LB Sutton Pension Fund')

with open('urls.txt', 'w') as f:
    f.write("\n".join(sorted(get_urls(api, 'Stage 5'))))


# fid = api.find_folder('Stage 5')['id']
# api.transfer_ownership(fid, "john.a.cowie@gmail.com")
