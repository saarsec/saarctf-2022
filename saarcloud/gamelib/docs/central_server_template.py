import hashlib
import hmac
import json
import os
import threading
from typing import Dict, Any, Optional, List, Tuple

# === some settings for the service ===
import redis

SERVICE_TOKEN_SECRET = 'abcdefgh'

# === try to load the gameserver's config file ===
if 'SAARCTF_CONFIG_DIR' in os.environ:
    basedir = os.path.abspath(os.environ['SAARCTF_CONFIG_DIR'])
else:
    basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
possible_config_files = [
    basedir + '/config_test.json',
    basedir + '/config2.json',
    basedir + '/config.json'
]
if 'SAARCTF_CONFIG' in os.environ:
    possible_config_files = [os.environ['SAARCTF_CONFIG']] + possible_config_files

CONFIG: Dict[str, Any] = {}
for configfile in possible_config_files:
    if os.path.exists(configfile):
        with open(configfile, 'rb') as f:
            CONFIG = json.loads(f.read())
        break
if not CONFIG:
    print('Test config loaded')
    CONFIG = {
        "databases": {
            "redis": {
                "host": "localhost",
                "port": 6379,
                "db": 0
            }
        },
        "network": {
            "team_range": [10, [200, 256, 32], [1, 200, 0], 0, 24]
        }
    }
network_ip: List[Tuple[int, int, int]] = \
    [tuple(component) if type(component) is list else (1, 1, component) for component in CONFIG['network']['team_range'][:4]]  # type: ignore
network_size = CONFIG['network']['team_range'][4]


# === Utils ===

def network_ip_to_id(ip: str) -> Optional[int]:
    """
    Get IPv4 address, return team id (if in network) or None
    :param ip:
    :return:
    """
    ip_split = ip.split('.')
    a = []
    b = []
    pos = []
    for i in range(network_size // 8):
        ai, bi, ci = network_ip[i]
        if bi > 1:
            a.append(ai)
            b.append(bi)
            pos.append((int(ip_split[i]) - ci) * ai)
    while True:
        smallest = max(pos)
        largest = min((pos_i + a_i for pos_i, a_i in zip(pos, a)))
        if smallest >= 0xffff:
            return None
        if smallest < largest:
            return smallest
        for i in range(len(pos)):
            while pos[i] + a[i] <= smallest:
                pos[i] += a[i] * b[i]


def validate_service_token(team_id: int, token: str) -> bool:
    """
    Return True iff the token is valid for a team id
    :param team_id:
    :param token:
    :return:
    """
    expected = hmac.HMAC(SERVICE_TOKEN_SECRET.encode(), str(team_id).encode(), hashlib.sha256).hexdigest()[:32]
    return token == expected


class GameStatus:
    """
    Has (and automatically updates) these properties:
    - state (str) ("RUNNING"/"SUSPENDED"/"STOPPED")
    - currentTick (int)
    """

    def __init__(self):
        self.redis = redis.StrictRedis(**CONFIG['databases']['redis'])
        self.state: str = self.redis.get('timing:state').decode()
        r = self.redis.get('timing:currentRound')
        self.currentTick: int = int(r.decode()) if r else -1
        # watch for changes
        self.redis_pubsub = self.redis.pubsub()
        self.redis_pubsub.subscribe('timing:state', 'timing:currentRound')
        thread = threading.Thread(target=self.__listen_for_redis_events, name='Redis-Listener', daemon=True)
        thread.start()

    def __listen_for_redis_events(self):
        for item in self.redis_pubsub.listen():
            if item['type'] == 'message':
                if item['channel'] == b'timing:state':
                    newstate = item['data'].decode('utf-8')
                    if self.state != newstate:
                        self.state_changes(newstate)
                    self.state = newstate
                elif item['channel'] == b'timing:currentRound':
                    r = item['data']
                    self.currentTick = int(r.decode()) if r else -1
                    self.new_tick(self.currentTick)

    def state_changes(self, new_state: str):
        # your code if necessary
        pass

    def new_tick(self, tick: int):
        # your code if necessary
        pass


# === Your code ===

def main():
    # status = GameStatus()
    # print(status.state, status.currentTick)
    ...


if __name__ == '__main__':
    main()
