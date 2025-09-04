import requests

HEROES = requests.get("https://assets.deadlock-api.com/v2/heroes?language=english&only_active=true").json()
RANKS = requests.get("https://assets.deadlock-api.com/v2/ranks").json()

def get_hero_id(name: str) -> int | None:
    for hero in HEROES:
        hero_name: str = hero["name"]
        if hero_name.lower() == name.lower():
            return hero["id"]
    return None

def hero_name(id: int) -> str:
    for hero in HEROES:
        if hero["id"] == id:
            return hero["name"]

def get_player_networth_8min(playerdata) -> int:
    for stat in playerdata["stats"]:
        if stat["time_stamp_s"] == 900:
            return stat["net_worth"]

#returns lane partner, then opps 1 and 2
def get_lane_players(data, player_team, player_id, player_lane):
    ret = []
    for player in data["match_info"]["players"]:
        if player["team"] == player_team and player["assigned_lane"] == player_lane and player["account_id"] != player_id:
            ret.append(player)
            break
    
    for player in data["match_info"]["players"]:
        if player["assigned_lane"] == player_lane and player["team"] != player_team:
            ret.append(player)

    return ret

def get_player_lane_diff(data, team, lane) -> float:
    soulcount_0 = 0
    soulcount_1 = 0
    for player in data["match_info"]["players"]:
        if player["assigned_lane"] == lane:
            if player["team"] == team:
                soulcount_0 += get_player_networth_8min(player)
            else:
                soulcount_1 += get_player_networth_8min(player)
    
    return round(float(soulcount_0 - soulcount_1) / 1000.0, 1)

def get_rank_str(num: int) -> str:
    tier: int = num // 10
    div: int = num % 10
    return f"{RANKS[tier]['name']} {div}"

def get_player_data(steam_id: int, data):
    for player in data["match_info"]["players"]:
        if player["account_id"] != steam_id:
            continue
        print("Found player in match")
        return player
    return None

def get_player_end_stats(match_duration: int, player_data):
    for stat in player_data["stats"]:
        if stat["time_stamp_s"] == match_duration:
            return stat
    return None

class Digest_lm():
    def __init__(self, steam_id, lm_detailed):

        self.lm_detailed = lm_detailed
        self.player_data = get_player_data(steam_id, lm_detailed)

        self.lm_id: int = lm_detailed["match_info"]["match_id"]
        self.duration: int = lm_detailed["match_info"]["duration_s"]
        self.player_team: int = self.player_data["team"]
        self.victory: bool = lm_detailed["match_info"]["winning_team"] == self.player_team
        self.player_lane: int = self.player_data["assigned_lane"]

        self.player_end_stats = get_player_end_stats(self.duration, self.player_data)
        self.lane_diff: float = get_player_lane_diff(lm_detailed, self.player_data["team"], self.player_data["assigned_lane"])

        self.player_items = self.player_data["items"]

        self.player_team_badge: int = lm_detailed["match_info"]["average_badge_team0"] if self.player_team == 0 else lm_detailed["match_info"]["average_badge_team1"]
        self.enemy_team_badge: int = lm_detailed["match_info"]["average_badge_team0"] if self.player_team == 1 else lm_detailed["match_info"]["average_badge_team1"]
        self.player_accuracy: float = round((self.player_end_stats["shots_hit"] / (self.player_end_stats["shots_missed"] + self.player_end_stats["shots_hit"])) * 100, 1)
        self.player_nw: int = self.player_end_stats["net_worth"]
        self.player_denies: int = self.player_end_stats["denies"]
        self.player_lh: int = self.player_end_stats["creep_kills"] + self.player_end_stats["neutral_kills"]
        self.player_lvl: int = self.player_end_stats["level"]
        self.player_obj_damage = self.player_end_stats["boss_damage"]

        self.player_hero: int = self.player_data["hero_id"]
        self.kills: int = self.player_data["kills"]
        self.deaths: int = self.player_data["deaths"]
        self.assists: int = self.player_data["assists"]

        self.player_nw_8 = get_player_networth_8min(self.player_data)
        self.laners = get_lane_players(lm_detailed, self.player_team, steam_id, self.player_lane)
        self.lane_partner_nw_8 = get_player_networth_8min(self.laners[0])
        self.lane_partner_hero = self.laners[0]["hero_id"]
        
        self.lane_opp_0_nw_8 = get_player_networth_8min(self.laners[1])
        self.lane_opp_1_nw_8 = get_player_networth_8min(self.laners[2])
        self.lane_opp_0_hero = self.laners[1]["hero_id"]
        self.lane_opp_1_hero = self.laners[2]["hero_id"]