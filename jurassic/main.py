from spreadsheet import Spreadsheet
from progress import FileList, FileCheckList
import stage5
import json
import argparse
import time
import shutil
import os

# Pull these into separate files
# emails = ['john.a.cowie@gmail.com',
#            'anna@platformlondon.org',
#           'anna.galkina.tation@gmail.com',
#           "sarahshoraka77@gmail.com"
# ]
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

# TODO add this to CLI methods
def get_urls(api, folder_name):
    folder_id = api.find_folder(folder_name)['id']
    files = api.find_files_in_folder(folder_name)
    lines = []
    for f in files:
        lines.append(f['name'] + " - " + generate_url(folder_id, f['id']))
    return lines

class CLI:
    
    def __init__(self, api, path):
        self._api = api
        self._path = path
        self._stage3_dir = path + '/stage3'
        self._stage3_data = path + '/stage3/data'
        self._stage3_progress = path + '/stage3/progress.json'
        self._stage5_data = path + '/stage5/data'
    
    def read(self, reset):
    
        if not os.path.exists(self._stage3_dir) or reset:
            shutil.rmtree(self._stage3_dir, True)
            os.mkdir(self._stage3_dir)
            os.mkdir(self._stage3_data)
    
        fcl = FileCheckList(self._stage3_progress)
        if not fcl.has_todos():
            files = self._api.find_files_in_folder('Stage 3 JC created sheets')
            fcl.set_todos(files)

        while (fcl.get_next_todo() != None):
            todo = fcl.get_next_todo()
            name = todo['name']
            ss_id = todo['id']
            ss = self._api.open_by_id(ss_id)
            data = {}
            data['data'] = ss.worksheet('Full Data').get_all_records()
            data['pooled'] = ss.worksheet('Pooled').get_all_records()
            print('Writing ' + name + '.json')
            with open(self._stage3_data + '/' + name + '.json', 'w') as f:
                f.write(json.dumps(data))
            fcl.mark_as_done(todo)
            time.sleep(3)
        

    def transform(self):

        # Read formula spreadsheets
        oil = self._api.get_records('Categories', 'Oil')
        coal = self._api.get_records('Categories', 'Coal')

        # Wipe existing stage 5 directory
        shutil.rmtree(self._stage5_data, True)
    
        # Create stage5 directory
        os.mkdir(self._stage5_data)
    
        # get list of files in stage 3 directory
        files = os.listdir(self._stage3_data)
    
        # For each file in directory
        for f in files:
            # Transform data
            print('Transforming ' + f)
            fund_name = f.replace('.json', '')
            input_data = None
            with open(self._stage3_data + '/' + f) as fl:
                input_data = json.loads(fl.read())
      
            output_data = stage5.gen_spreadsheet(fund_name, input_data, oil, coal)
            with open(self._stage5_data + '/' + f, 'w+') as fl:
                fl.write(json.dumps(output_data))

    def write(self):

        folder_name = 'JCFRACKTEST'

        folder_id = stage5.prepare_folder(self._api, folder_name, False) 
        # for each file in files
        files = os.listdir(self._stage5_data)

        can_edit = True

        emails = ['john.a.cowie@gmail.com']
        
        for f in files:
            fund_name = f.replace('.json', '')
            data = None
            with open(self._stage5_data + '/' + f) as fl:
                data = json.loads(fl.read())
            stage5.create_spreadsheet(self._api, folder_id, fund_name, data, emails, can_edit)
            # call create spreadsheet with data
            

def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", help="read/transform/write")
    parser.add_argument("--reset", action='store_true')
    parser.add_argument("--path", default='testingDataDirec')
    parser.add_argument("--creds", default='creds/stage5_3.json')
    args = parser.parse_args()
    
    api = Spreadsheet(args.creds)
    cli = CLI(api, args.path)

    if args.command == 'read':
        cli.read(args.reset)
    elif args.command == 'transform':
        cli.transform()
    elif args.command == 'write':
        cli.write()
    else:
        print ('Unrecognised command')

cli()

# api = Spreadsheet('creds/stage5_3.json')
# progress = FileList('progress.txt')
# api.delete_files_in_folder('Stage 5 test')
# api.delete_files_in_folder('Stage 5')
# create_all_spreadsheets_sf(api, 'Stage 3 JC created sheets', 'Stage 5', emails, False, ['Avon Pension Fund'])
# create_all_spreadsheets_sf(api, 'Stage 3 JC created sheets', 'Stage 5', emails, False)

# stage3_file = 'stage3_data/2017-10-30.json'

# data = read_stage3(api, 'Stage 3 JC created sheets')
# write_data_to_file(stage3_file, data)


# data = process_stage3(load_data_from_file(stage3_file))
# retry = True
# write_stage5(api, progress, data, 'Stage 5', emails, retry)

# fid = api.find_folder('Stage 5')['id']
# api.delete_spreadsheet(fid, 'LB Richmond Upon Thames Pension Fund')
# api.delete_spreadsheet(fid, 'NILGOSC')
# api.delete_spreadsheet(fid, 'LB Sutton Pension Fund')

# with open('urls.txt', 'w') as f:
  #   f.write("\n".join(sorted(get_urls(api, 'Stage 5'))))

# api = Spreadsheet('creds/stage5_3.json')
# fid = api.find_folder('JCFRACKTEST')['id']
# api.transfer_ownership(fid, "john.a.cowie@gmail.com")
