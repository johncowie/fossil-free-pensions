import spreadsheet as s
import formula as f
import time as t

def addPooledTab():
    headers = ["Rank", "Name", "Category", "Amount", "Is Pooled? (Y/N)"]
    rows = []
    rankCol = 'A' # in this sheet
    nameCol = 'A'
    categoryCol = 'B'
    amount = 'C'
    for i in range(1, 16):
        rankCell = 'A'+str(i+1)
        row = [ s.number_cell(i)
              , f.largest_value_name('Full Data', 'C', 'A', rankCell)
              , f.largest_value_name('Full Data', 'C', 'B', rankCell)
              , f.largest_value('Full Data', 'C', rankCell)]
        rows.append(row)
    return [headers] + rows

def fullDataTab():
    headers = ["Description of Holding", "Sub-category/Classification", "Amount"]
    rows = [[]] * 100
    return [headers] + rows


def createPooledTab(api):
    files = api.find_files_in_folder("Stage 3 JC created sheets")
    cells = addPooledTab()
    err = 0
    succ = 0
    for f in files:
        print("Errors: {0}, Success: {1}".format(err, succ))
        print(f['name'])
        # print(f['id'])
        sid = f['id']
        try:
            wid = api.create_worksheet(sid, 'Pooled', cells)
            api.set_cells(sid, wid, cells)
            t.sleep(30)
            succ = succ+1
        except Exception as e:
            print(e)
            print("### Skipping as worksheet creation failed..")
            err = err+1
    print("Errors: {0}, Success: {1}".format(err, succ))

def create_new_stage3(api, name):
    fullDataCells = fullDataTab()
    pooledCells = addPooledTab()
    fid = api.find_folder("Stage 3 JC created sheets")['id']
    sh = api.create_spreadsheet(name, fid)
    sid = sh.id
    api.add_permission(sid, "john.a.cowie@gmail.com", False, True)
    api.add_permission(sid, "sarahshoraka77@gmail.com", False, True)

    w1id = api.create_worksheet(sid, 'Full Data', fullDataCells)
    api.set_cells(sid, w1id, fullDataCells)

    w2id = api.create_worksheet(sid, 'Pooled', pooledCells)
    api.set_cells(sid, w2id, pooledCells)



# api = s.Spreadsheet('creds/creds.json')
# create_new_stage3(api, "Northern Ireland Pension Fund")
# createPooledTab(api)
