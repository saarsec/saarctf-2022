import hashlib
import hmac
import random
import re
import string

try:
    from saarctf_commons.config import SECRET_FLAG_KEY
except ImportError:
    # These values / methods will later be defined by the server-side configuration
    SECRET_FLAG_KEY: bytes = b'\x00' * 32  # type: ignore


def generate_flag_id(flag_id_type: str, service_id: int, team_id: int, tick: int, index: int = 0, **kwargs) -> str:
    """
    Generate the FlagID for the flag stored in a given tick.
    The FlagID is public from the moment the gameserver script is scheduled.
    The format must be specified in #ServiceInterface.flag_id_types, see possible types there.
    :param str flag_id_type:
    :param int service_id:
    :param int team_id:
    :param int tick:
    :param int index:
    :return:
    """
    seed = hmac.new(SECRET_FLAG_KEY, f'{service_id}|{team_id}|{tick}|{index}'.encode(), hashlib.sha1).digest()
    rnd = random.Random(seed)
    return generate_flag_id_rnd(flag_id_type, rnd, **kwargs)


def generate_flag_id_rnd(flag_id_type: str, rnd: random.Random, **kwargs) -> str:
    if flag_id_type == 'username':
        from . import usernames
        return usernames.generate_username(generator=rnd, **kwargs)
    elif flag_id_type.startswith('hex'):
        return ''.join(rnd.choice('0123456789abcdef') for _ in range(int(flag_id_type[3:])))
    elif flag_id_type.startswith('alphanum'):
        return ''.join(rnd.choice(string.ascii_letters + string.digits) for _ in range(int(flag_id_type[8:])))
    elif flag_id_type == 'email':
        from . import usernames
        return usernames.generate_username(generator=rnd, camelcase=False, **kwargs) + "@" + usernames.generate_username(generator=rnd, camelcase=False, **kwargs) + ".com"
    elif flag_id_type.startswith('pattern:'):
        pattern = flag_id_type[8:]
        return re.sub(r'\$\{(.*?)}', lambda m: generate_flag_id_rnd(m.group(1), rnd, **kwargs), pattern)
    else:
        raise Exception(f'Invalid FlagId type requested: {repr(flag_id_type)}')
