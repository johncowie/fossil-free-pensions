import json
import os.path
import os

class FileList:
    _filename = None

    def __init__(self, file_name):
        self._filename = file_name

    def get_list(self):
        try:
            with open(self._filename) as f:
                return f.read().splitlines()
        except:
            return []

    def add_to_list(self, item):
        try:
            with open(self._filename, 'a') as f:
                f.write(item + '\n')
        except:
            with open(self._filename, 'w+') as f:
                f.write(item + '\n')
        return self.get_list()

# fl = FileList('progress.txt')
# print(fl.get_list())
# print(fl.add_to_list("abc"))
# print(fl.add_to_list("def"))


class FileCheckList:
    _filename = None

    def __init__(self, file_name):
        self._filename = file_name

    def has_todos(self):
        return os.path.isfile(self._filename)
    
    def set_todos(self, item_list):
        data = {'done':[], 'todo':item_list}
        with open(self._filename, 'w+') as f:
            f.write(json.dumps(data))

    def clear_todos(self):
        os.remove(self._filename)
            
    def get_data(self):
        with open(self._filename) as f:
            return json.loads(f.read())

    def get_done(self):
        return self.get_data()['done']

    def get_not_done(self):
        return self.get_data()['todo']
        
    def mark_as_done(self, item):
        data = self.get_data()
        done = data['done']
        todo = data['todo']
        if item in todo:
            done.append(item)
            todo = list(filter(lambda x: x != item, todo))
            new_data = {'done':done, 'todo':todo}
            with open(self._filename, 'w+') as f:
                f.write(json.dumps(new_data))

    def get_next_todo(self):
        todo = self.get_not_done()
        if len(todo) == 0:
            return None
        else:
            return todo[0]
