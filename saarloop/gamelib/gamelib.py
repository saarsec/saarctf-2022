"""
Library for GameserverScript developers. Inherit ServiceInterface.

This file is intentionally without type annotations, to allow script devs to work with older versions of Python (3).
"""

import hmac
import hashlib
import base64
import json
import re
import struct
import os
from typing import List, Any, Optional, Tuple, Set

import requests

from . import flag_ids

try:
    from saarctf_commons.config import SECRET_FLAG_KEY, get_redis_connection

except ImportError:
    # These values / methods will later be defined by the server-side configuration
    SECRET_FLAG_KEY: bytes = b'\x00' * 32  # type: ignore

    import redis

    REDIS_HOST = os.environ['REDIS_HOST'] if 'REDIS_HOST' in os.environ else 'localhost'
    REDIS_DB = int(os.environ['REDIS_DB']) if 'REDIS_DB' in os.environ else 3

    def get_redis_connection() -> redis.StrictRedis:
        return redis.StrictRedis(REDIS_HOST, db=REDIS_DB)

# default timeout for a single connection
TIMEOUT = 7

# determines size of the flag
MAC_LENGTH = 16
FLAG_LENGTH = 24
FLAG_REGEX = re.compile(r'SAAR{[A-Za-z0-9-_]{' + str(FLAG_LENGTH // 3 * 4) + '}}')


class FlagMissingException(Exception):
    """
    Service is working, but flag could not be retrieved
    """

    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return str(self.message)


class MumbleException(AssertionError):
    """
    Service is online, but behaving unexpectedly (dropping data, returning wrong answers, ...). AssertionError is also valid.
    """

    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return str(self.message)


class OfflineException(Exception):
    """
    Service is not reachable / connections get dropped or interrupted
    """

    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return str(self.message)


class Team:
    def __init__(self, _id: int, name: str, ip: str):
        """
        :param int _id: database team id
        :param str name: team name
        :param str ip: vulnbox ip
        """
        self.id = _id
        self.name = name  # don't rely on name - it might be dropped
        self.ip = ip


class ServiceInterface:
    """
    Stateless class that interacts with a specific service. Each service has an ID and a name.
    Inherit and override: check_integrity, store_flags and retrieve_flags.
    Check out the other methods, they might show useful:
    - Get a flag you want to store
    - Search for flags and check their validity
    - Make server-side data persistent (store them to Redis)
    """

    # Set this one in your inherited class
    name: str = '?'

    # Set this one in your inherited class if you need FlagIDs.
    # Possible values: 'username', 'hex<number>', 'alphanum<number>', 'email', 'pattern:${username}/constant_string/${hex12}'
    flag_id_types: List[str] = []

    def __init__(self, service_id: int):
        self.id = service_id

    def check_integrity(self, team: Team, tick: int):
        """
        Do integrity checks that are not related to flags (checking the frontpage, or if exploit-relevant functions are still available)
        :param Team team:
        :param int tick:
        :raises MumbleException: Service is broken
        :raises AssertionError: Service is broken
        :raises OfflineException: Service is not reachable
        :return:
        """
        raise Exception('Override me')

    def store_flags(self, team: Team, tick: int):
        """
        Send one or multiple flags to a given team. You can perform additional functionality checks here.
        :param Team team:
        :param int tick:
        :raises MumbleException: Service is broken
        :raises AssertionError: Service is broken
        :raises OfflineException: Service is not reachable
        :return:
        """
        raise Exception('Override me')

    def retrieve_flags(self, team: Team, tick: int):
        """
        Retrieve all flags stored in a previous tick from a given team. You can perform additional functionality checks here.
        :param Team team:
        :param int tick: The tick in which the flags have been stored
        :raises FlagMissingException: Flag could not be retrieved
        :raises MumbleException: Service is broken
        :raises AssertionError: Service is broken
        :raises OfflineException: Service is not reachable
        :return:
        """
        raise Exception('Override me')

    def initialize_team(self, team: Team):
        """
        Called once before check/store/retrieve are issued for a team.
        Override for initialization code.
        :param team:
        :return:
        """
        pass

    def finalize_team(self, team: Team):
        """
        Called once after check/store/retrieve have been issued, even in case of exceptions or timeout.
        Override for finalization code.
        :param team:
        :return:
        """
        pass

    def store(self, team: Team, tick: int, key: str, value):
        """
        Store arbitrary data for the next ticks
        :param Team team:
        :param int tick:
        :param str key:
        :param any value:
        :return:
        """
        get_redis_connection().set('services:' + self.name + ':' + str(team.id) + ':' + str(tick) + ':' + key, json.dumps(value))

    def load(self, team: Team, tick: int, key: str) -> Any:
        """
        Retrieve a previously stored value
        :param Team team:
        :param int tick:
        :param str key:
        :return: the previously stored value, or None
        """
        value = get_redis_connection().get('services:' + self.name + ':' + str(team.id) + ':' + str(tick) + ':' + key)
        if value is not None:
            return json.loads(value.decode('utf-8'))
        return value

    def get_flag(self, team: Team, tick: int, payload: int = 0) -> str:
        """
        Generates the flag for this service. Flag is deterministic.
        :param Team team:
        :param int tick: The tick number this flag will be set
        :param int payload: must be >= 0 and <= 0xffff. If you don't need the payload, use (0, 1, 2, ...).
        :rtype: str
        :return: the flag
        """
        data = struct.pack('<HHHH', tick & 0xffff, team.id, self.id, payload)
        mac = hmac.new(SECRET_FLAG_KEY, data, hashlib.sha256).digest()[:MAC_LENGTH]
        flag = base64.b64encode(data + mac).replace(b'+', b'-').replace(b'/', b'_')
        return 'SAAR{' + flag.decode('utf-8') + '}'

    def check_flag(self, flag: str, check_team_id: Optional[int] = None, check_stored_tick: Optional[int] = None) \
            -> Tuple[Optional[int], Optional[int], Optional[int], Optional[int]]:
        """
        Check if a given flag is valid for this service, and returns the components (team-id, service-id, the tick it
        has been set and the payload bytes).

        (Optional:) Check if the flag is for this team, and stored in a given tick.
        Pass check_team_id and check_stored_tick parameters for this.

        :param str flag:
        :param int|None check_team_id: Check if the flag is from this team
        :param int|None check_stored_tick: Check if the flag has been stored in the given tick
        :rtype: (int, int, int, int)
        :return: Tuple (teamid, serviceid, stored_tick, payload) or (None, None, None, None) if flag is invalid
        """
        if flag[:5] != 'SAAR{' or flag[-1] != '}':
            print('Flag "{}": invalid format'.format(flag))
            return (None, None, None, None)
        data = base64.b64decode(flag[5:-1].replace('_', '/').replace('-', '+'))
        if len(data) != FLAG_LENGTH:
            print('Flag "{}": invalid length'.format(flag))
            return (None, None, None, None)
        stored_tick, teamid, serviceid, payload = struct.unpack('<HHHH', data[:-MAC_LENGTH])
        if serviceid != self.id:
            print('Flag "{}": invalid service'.format(flag))
            return (None, None, None, None)
        mac = hmac.new(SECRET_FLAG_KEY, data[:-MAC_LENGTH], hashlib.sha256).digest()[:MAC_LENGTH]
        if data[-MAC_LENGTH:] != mac:
            print('Flag "{}": invalid mac'.format(flag))
            return (None, None, None, None)
        # Optional checks
        if check_team_id is not None and check_team_id != teamid:
            print('Flag "{}": invalid team'.format(flag))
            return (None, None, None, None)
        if check_stored_tick is not None and check_stored_tick & 0xffff != stored_tick:
            print('Flag "{}": invalid tick'.format(flag))
            return (None, None, None, None)
        return teamid, serviceid, stored_tick, payload

    def search_flags(self, text: str) -> Set[str]:
        """
        Find all flags in a given string (no validation is done)
        :param str text:
        :return: a (possibly empty) set of all flags contained in the input
        """
        return set(FLAG_REGEX.findall(text))

    def get_flag_id(self, team: Team, tick: int, index: int = 0, **kwargs) -> str:
        """
        Generate the FlagID for the flag stored in a given tick.
        The FlagID is public from the moment the gameserver script is scheduled.
        The format must be specified in #ServiceInterface.flag_id_types, see possible types there.
        :param Team team:
        :param int tick:
        :param int index:
        :return:
        """
        return flag_ids.generate_flag_id(self.flag_id_types[index], self.id, team.id, tick, index, **kwargs)


# === Assertion methods ===

def assert_equals(expected, result):
    """
    :param expected:
    :param result:
    :return: Raises an AssertionError if expected != result
    """
    if expected != result:
        raise AssertionError("Expected {} but was {}".format(repr(expected), repr(result)))


def assert_requests_response(resp, contenttype: str = 'application/json; charset=utf-8') -> requests.Response:
    """
    :param requests.Response resp:
    :param str contenttype:
    :return: Assert that a request was answered with statuscode 200 and a given content-type
    """
    if resp.status_code != 200:
        print('Response =', resp)
        print('Url =', resp.url)
        print('---Response---\n' + resp.text[:4096] + '\n\n')
        raise AssertionError('Invalid status code {} (text: "{}")'.format(resp.status_code, resp.text[:512]))
    assert_equals(contenttype.lower(), resp.headers['Content-Type'].lower())
    return resp
