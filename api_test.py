import requests
import json
import time

api_url = 'http://api.steampowered.com/'

dead_api = "https://api.deadlock-api.com/v1"

def request():
    lock_request = requests.get(f"{dead_api}/players/{75688374}/match-history?force_refetch=true&only_stored_history=false")
    lm = lock_request.json()[0]
    m_id = lm["match_id"]


if __name__ == '__main__':
    print("Requesting")
    request()