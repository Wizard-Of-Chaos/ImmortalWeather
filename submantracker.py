import pickle
import discord as dc

class SubmanTracker(object):
    def __init__(self, bot, fname):
        self.bot = bot
        self.fname = fname
        self.user_ids = [161444478, 106159118]
        self.load()

    def load(self):
        try:
            with open(self.fname, 'rb') as config_file:
                self.user_ids = pickle.load(config_file)
        except (OSError, EOFError):
            self.user_ids = [161444478, 106159118]
            self.save()
    
    def save(self):
        with open(self.fname, 'wb') as config_file:
            pickle.dump(self.user_ids, config_file)
            
    def add_subman(self, id):
        self.user_ids.append(id)
        self.save()
    
    def remove_subman(self, id):
        self.user_ids.remove(id)
        self.save()

    def clear_submen(self):
        self.user_ids.clear()
        self.save()

    def tracked_list(self):
        return self.user_ids