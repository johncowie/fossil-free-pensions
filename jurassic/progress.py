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
