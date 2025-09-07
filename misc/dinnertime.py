import pickle

class DinnerStorage(object):
    def __init__(self, dinner_file):
        self.file = dinner_file
        self.dinners: list[str] = []
        self.load()
    def load(self):
        try:
            with open(self.file, 'rb') as f:
                self.dinners = pickle.load(f)
        except (OSError, EOFError):
            self.dinners = []
            self.save()
    def save(self):
        with open(self.file, 'wb') as f:
            pickle.dump(self.dinners, f)
