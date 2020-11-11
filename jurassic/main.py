from spreadsheet import Spreadsheet
from progress import FileList, FileCheckList
import stage5
import json
import argparse
import time
import shutil
import os

# Pull these into separate files
email_group = ['john.a.cowie@gmail.com',
               'anna@platformlondon.org',
               'anna.galkina.tation@gmail.com',
               'sarahshoraka77@gmail.com',
               'mika@platformlondon.org',
               'sakina@platformlondon.org'
]

email_me = ['john.a.cowie@gmail.com']

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
        self._stage5_progress = path + '/stage5/progress.json'
        self._stage5_metadata = path + '/stage5/matches.json'

        self._summary_dir = path + '/summary'
        self._summary_data = path + '/summary/data'
        self._summary_progress = path + '/summary/progress.json'
        self._summary_output = path + '/summary/summary.json'
    
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
            
    def transform(self, for_fracking):

        # Read formula spreadsheets
        oil = self._api.get_records('Categories', 'Oil')
        coal = self._api.get_records('Categories', 'Coal')
        fracking = self._api.get_records('Categories', 'Fracking')
        
        # Wipe existing stage 5 directory
        shutil.rmtree(self._stage5_data, True)
                                         
        # Create stage5 directory
        os.mkdir(self._stage5_data)
    
        # get list of files in stage 3 directory
        files = os.listdir(self._stage3_data)

        investments = set()
        
        # For each file in directory
        for f in files:
            # Transform data
            print('Transforming ' + f)
            fund_name = f.replace('.json', '')
            input_data = None
            output_data = None
            
            with open(self._stage3_data + '/' + f) as fl:
                input_data = json.loads(fl.read())

            investments.update(stage5.investments_from_input_data(input_data))
                
            if for_fracking:
                output_data = stage5.fracking_gen_spreadsheet(fund_name, input_data, fracking)
            else:
                output_data = stage5.gen_spreadsheet(fund_name, input_data, oil, coal)
            with open(self._stage5_data + '/' + f, 'w+') as fl:
                fl.write(json.dumps(output_data))

        investments = list(investments)
        investments.sort()
        if for_fracking:
            metadata = stage5.fracking_gen_metadata(investments, fracking)
        else:
            metadata = stage5.gen_metadata(investments, fracking, oil, coal)
        with open(self._stage5_metadata, 'w+') as fl:
            fl.write(json.dumps(metadata))
        

    def matches(self, spreadsheet_dir):
        folder_id = stage5.prepare_folder(self._api, spreadsheet_dir, False)
        with open(self._stage5_metadata) as fl:
            data = json.loads(fl.read())
            sid = stage5.create_spreadsheet(self._api, folder_id, 'MATCHES', data, ['john.a.cowie@gmail.com'], True)
        self._api.transfer_ownership(sid, 'john.a.cowie@gmail.com')
        

    def write(self, spreadsheet_dir, can_edit, reset):

        folder_name = spreadsheet_dir # 'JCFRACKTEST'

        fcl = FileCheckList(self._stage5_progress)

        if reset:
            fcl.clear_todos()

        emails = email_group
            
        folder_id = stage5.prepare_folder(self._api, folder_name, reset)

        for email in emails:
            self._api.add_permission(folder_id, email, False, True)
            
        # for each file in files
        files = os.listdir(self._stage5_data)

        if not fcl.has_todos():
            fcl.set_todos(files)
        
        while fcl.get_next_todo() != None:
            f = fcl.get_next_todo()
            
            fund_name = f.replace('.json', '')
            data = None
            with open(self._stage5_data + '/' + f) as fl:
                data = json.loads(fl.read())
            stage5.create_spreadsheet(self._api, folder_id, fund_name, data, emails, can_edit)
            fcl.mark_as_done(f)
            time.sleep(3)
        #     # call create spreadsheet with data

    def summary_read(self, spreadsheet_dir, reset):
        if not os.path.exists(self._summary_dir) or reset:
            shutil.rmtree(self._summary_dir, True)
            os.mkdir(self._summary_dir)
            os.mkdir(self._summary_data)

        fcl = FileCheckList(self._summary_progress)
        if not fcl.has_todos():
            files = self._api.find_files_in_folder(spreadsheet_dir)
            fcl.set_todos(files)

        while fcl.get_next_todo() != None:
            todo = fcl.get_next_todo()
            name = todo['name']

            print('Reading ' + name + ' sheet')

            ss_id = todo['id']
            ss = self._api.open_by_id(ss_id)
            data = {}
            data['overview'] = ss.worksheet('Overview figures').get_all_records()
            data['url'] = 'https://docs.google.com/spreadsheets/d/' + ss_id
            print('Writing ' + name + '.json')
            with open(self._summary_data + '/' + name + '.json', 'w') as f:
                f.write(json.dumps(data))
            fcl.mark_as_done(todo)
            time.sleep(3)
            
        return None

    def summary_transform(self, for_fracking):
        # [ ] read all files into data structure
        files = os.listdir(self._summary_data)
        input_data = {}
        output_data = None
        
        for f in files:
            print('Transforming ' + f)
            fund_name = f.replace('.json', '')

            with open(self._summary_data + '/' + f) as fl:
                input_data[fund_name] = json.loads(fl.read())

        if for_fracking:
            output_data = [('summary', stage5.fracking_summary_tab(input_data))]
        else:
            raise ValueError('Summary transform for non-fracking is unsupported')
        with open(self._summary_output, 'w+') as fl:
            fl.write(json.dumps(output_data))
        
        # [ ] save file to summary.json
        
        return None

    def summary_write(self, spreadsheet_dir):
        folder_id = stage5.prepare_folder(self._api, spreadsheet_dir, False)
        with open(self._summary_output) as fl:
            data = json.loads(fl.read())
            sid = stage5.create_spreadsheet(self._api, folder_id, 'Overview', data, ['john.a.cowie@gmail.com'], True)
        self._api.transfer_ownership(sid, 'john.a.cowie@gmail.com')


def cli_read(args):
    api = Spreadsheet(args.creds)
    cli = CLI(api, args.path)
    cli.read(args.reset)

def cli_transform(args):
    api = Spreadsheet(args.creds)
    cli = CLI(api, args.path)
    cli.transform(args.fracking)

def cli_write(args):
    api = Spreadsheet(args.creds)
    cli = CLI(api, args.path)
    cli.write(args.spreadsheet_dir, args.editable, args.reset)

def cli_matches(args):
    api = Spreadsheet(args.creds)
    cli = CLI(api, args.path)
    cli.matches(args.spreadsheet_dir)

def cli_summary_read(args):
    api = Spreadsheet(args.creds)
    cli = CLI(api, args.path)
    cli.summary_read(args.spreadsheet_dir, args.reset)

def cli_summary_transform(args):
    api = Spreadsheet(args.creds)
    cli = CLI(api, args.path)
    cli.summary_transform(args.fracking)

def cli_summary_write(args):
    api = Spreadsheet(args.creds)
    cli = CLI(api, args.path)
    cli.summary_write(args.spreadsheet_dir)
    
def cli():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--creds", default='creds/stage5_3.json', help='defaults to creds/stage5_3.json')
    parser.add_argument("--path", default='testingDataDirec', help='defaults to testingDataDirec')
    subparsers = parser.add_subparsers()

    read_p = subparsers.add_parser('read')
    read_p.add_argument("--reset", action='store_true', help='removes any existing files')
    read_p.set_defaults(exec = cli_read)

    transform_p = subparsers.add_parser('transform')
    transform_p.add_argument("--fracking", action='store_true')
    transform_p.set_defaults(exec = cli_transform)

    matches_p = subparsers.add_parser('matches')
    matches_p.add_argument("--spreadsheet_dir", default="JCFRACKTEST", help='defaults to JCFRACKTEST')
    matches_p.set_defaults(exec = cli_matches)
    
    write_p = subparsers.add_parser('write')
    write_p.add_argument("--reset", action='store_true')
    write_p.add_argument("--editable", action='store_true')
    write_p.add_argument("--spreadsheet_dir", default='JCFRACKTEST', help='defaults to JCFRACKTEST')
    write_p.set_defaults(exec = cli_write)

    summary_read_p = subparsers.add_parser('summary-read')
    summary_read_p.add_argument("--reset", action='store_true', help='removes any existing files')
    summary_read_p.add_argument("--spreadsheet_dir", default='JCFRACKTEST', help='stage 5 directory to read data from - defaults to JCFRACKTEST')
    summary_read_p.set_defaults(exec = cli_summary_read)

    summary_transform_p = subparsers.add_parser('summary-transform')
    summary_transform_p.add_argument("--fracking", action='store_true')
    summary_transform_p.set_defaults(exec = cli_summary_transform)

    summary_write_p = subparsers.add_parser('summary-write')
    summary_write_p.add_argument("--spreadsheet_dir", default='JCFRACKTEST', help='stage 5 directory to write overview to - defaults to JCFRACKTEST')
    summary_write_p.set_defaults(exec = cli_summary_write)
    
    args = parser.parse_args()
    args.exec(args)
    
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
