import pickle
import discord as dc

CARDINAL_DIRECTIONS = [75688374, 107944284, 62681700, 173836647]
CARDINAL_IDS = [125433170047795200, 144608604610232320, 130569142863396865, 252257562710245376]
CARDINAL_MAP = {
    125433170047795200 : 75688374,
    144608604610232320 : 107944284,
    130569142863396865 : 62681700,
    252257562710245376 : 173836647
}

class PlayerData(object):
    def __init__(self):
        self.dota_id = int(0)
        self.tracked_submen = list[int]

        self.last_forecast_timestamp = int(0)
        self.last_forecast_confidence = float(1.0)

        self.good_forecast_games = int(0)
        self.good_forecast_wins = int(0)
        self.bad_forecast_games = int(0)
        self.bad_forecast_wins = int(0)
        
    def add_subman(self, id:int):
        self.tracked_submen.append(id)

    def remove_subman(self, id:int):
        self.tracked_submen.remove(id)
    
    def good_game_winrate(self) -> float:
        return float(self.good_forecast_wins / self.good_forecast_wins)
    
    def bad_game_winrate(self) -> float:
        return float(self.bad_forecast_wins / self.bad_forecast_games)

class SubmanTracker(object):
    def __init__(self, globalfile, personalfile, regfile):
        self.globalfile = globalfile
        self.personalfile = personalfile
        self.regfile = regfile
        self.global_subman_ids = [161444478, 106159118]
        self.users = {125433170047795200 : [161444478, 106159118]}
        self.registered_ids = CARDINAL_MAP
        self.load()

    def load(self):
        try:
            with open(self.globalfile, 'rb') as config_file:
                self.global_subman_ids = pickle.load(config_file)
        except (OSError, EOFError):
            self.global_subman_ids = [161444478, 106159118]
            self.save()
        try:
            with open(self.personalfile, 'rb') as config_file:
                self.users = pickle.load(config_file)
        except (OSError, EOFError):
            #i hate draskyl so much man
            self.users = {125433170047795200 : [161444478, 106159118]}
            self.save()
        try:
            with open(self.regfile, 'rb') as config_file:
                self.registered_ids = pickle.load(config_file)
        except (OSError, EOFError):
            self.registered_ids = CARDINAL_MAP
            self.save()
    
    def save(self):
        with open(self.globalfile, 'wb') as config_file:
            pickle.dump(self.global_subman_ids, config_file)
        with open(self.personalfile, 'wb') as config_file:
            pickle.dump(self.users, config_file)
        with open(self.regfile, 'wb') as config_file:
            pickle.dump(self.registered_ids, config_file)
            
    def add_subman_global(self, id: int):
        self.global_subman_ids.append(id)
        self.save()
    
    def remove_subman_global(self, id: int):
        self.global_subman_ids.remove(id)
        self.save()

    def clear_submen_global(self):
        self.global_subman_ids.clear()
        self.save()

    def add_subman_personal(self, userid: int, id: int):
        self.users[userid].append(id)
        self.save()

    def remove_subman_personal(self, userid: int, id: int):
        self.users[userid].append(id)
        self.save()
    
    def clear_submen_personal(self, userid: int):
        self.users[userid].clear()
        self.save()

    def tracked_list(self) -> list[int]:
        return self.global_subman_ids
    
    def global_submen_count(self) -> int:
        return len(self.tracked_list())

    def personal_tracked_list(self, userid: int) -> list[int]:
        return self.users[userid]
    
    def register(self, userid: int, dotaid: int):
        self.registered_ids[userid] = dotaid
        self.save()
    
    def registered(self, userid: int) -> bool:
        if userid in self.registered_ids.keys():
            return True
        return False
    
    def registered_as(self, dotaid: int) -> int:
        for key, val in self.registered_ids.items():
            if val == dotaid:
                return key
        return None