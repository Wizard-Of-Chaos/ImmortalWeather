import pickle
import gargoyle_consts

class UserReg(object):
    def __init__(self, regfile):
        self.regfile = regfile
        self.registered_ids = gargoyle_consts.CARDINAL_MAP
        self.load()

    def load(self):
        try:
            with open(self.regfile, 'rb') as config_file:
                self.registered_ids = pickle.load(config_file)
        except (OSError, EOFError):
            self.registered_ids = gargoyle_consts.CARDINAL_MAP
            self.save()
    def save(self):
        with open(self.regfile, 'wb') as config_file:
            pickle.dump(self.registered_ids, config_file)
    
    def register(self, userid: int, steamid: int):
        print(f"registering id {userid} to {steamid}")
        self.registered_ids[userid] = steamid
        self.save()
    
    def unregister(self, userid: int):
        self.registered_ids.pop(userid)
        self.save()
    
    def registered(self, userid: int) -> bool:
        if userid in self.registered_ids.keys():
            return True
        return False
    
    def discord_registered_as(self, steamid: int) -> int:
        for key, val in self.registered_ids.items():
            if val == steamid:
                return key
        return None
    
    def steam_registered_as(self, discordid: int) -> int:
        for key, val in self.registered_ids.items():
            if key == discordid:
                return val
        return None

REGISTRY = UserReg("id_reg.pkl")