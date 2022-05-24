import glob
import io
import os.path
import random
import wave

import gamelib.usernames
from gamelib import *
try:
    from .gen_synth import bytes_to_synth
    from .loop_gen import gen_loop
except ImportError:
    from gen_synth import bytes_to_synth
    from loop_gen import gen_loop


DATADIR = os.path.dirname(os.path.realpath(__file__)) + "/data"


def gen_flag_sample(flag):
    flag = flag.encode()

    infile = random.choice(glob.glob(f'{DATADIR}/*wav'))

    with wave.open(infile) as f:
        nchannels = f.getnchannels()
        sampwidth = f.getsampwidth()
        framerate = f.getframerate()
        buf = bytearray(f.readframes(f.getnframes()))

    insert_point = random.randint(0, len(buf) - (len(flag) + 1))
    buf[insert_point: insert_point + len(flag)] = flag

    file_buf = io.BytesIO()

    with wave.open(file_buf, "wb") as f:
        f.setnchannels(nchannels)
        f.setsampwidth(sampwidth)
        f.setframerate(framerate)
        f.writeframes(buf)

    # be kind, rewind
    file_buf.seek(0)
    return file_buf


class SaarloopAPI:
    def __init__(self, url):
        self.url = url
        self.session = requests.Session()
        self.session.headers["Connection"] = "Close"

    def register(self, username, password):
        r = self.session.post(self.url + '/register', {"username": username, "password": password},
                              timeout=gamelib.TIMEOUT)
        print(f"Trying to register with {username=} {password=}, got {r.status_code}")
        assert r.status_code == 200

    def login(self, username, password):
        r = self.session.post(self.url + '/login', {"username": username, "password": password},
                              timeout=gamelib.TIMEOUT)
        print(f"Trying to login with {username=} {password=}, got {r.status_code}")
        assert r.status_code == 200

    def upload_sample(self, sample_name, samplefile):
        r = self.session.post(self.url + '/new_sample', files={"sample_file": (sample_name, samplefile)},
                              timeout=gamelib.TIMEOUT)
        assert r.status_code == 200
        samples = self.parse_samples(r)
        assert sample_name in samples
        return samples[sample_name]

    def list_samples(self):
        r = self.session.get(self.url + '/samples', timeout=gamelib.TIMEOUT)
        assert r.status_code == 200
        return self.parse_samples(r)

    def parse_samples(self, r):
        samples = {}
        for chunk in r.text.split('<source src="')[1:]:
            sample_url, rem = chunk.split('"', maxsplit=1)
            sample_name = rem.split('<p class="card-text">', maxsplit=1)[1].split('</p>', maxsplit=1)[0].strip()
            samples[sample_name] = sample_url
        return samples

    def download_sample(self, sample_name):
        r = self.session.get(self.url + f'/sample/USER/{sample_name}', timeout=gamelib.TIMEOUT)
        assert r.status_code == 200
        assert r.content.startswith(b'RIFF')
        return r.content

    def create_synth(self, synth_name, synth):
        r = self.session.post(self.url + '/new_synth', {"synth": json.dumps(synth), "synth_name": synth_name},
                              timeout=gamelib.TIMEOUT)
        assert r.status_code == 200
        synths = self.parse_synths(r)
        assert synth_name in synths
        return synths[synth_name]

    def list_synths(self):
        r = self.session.get(self.url + '/synths', timeout=gamelib.TIMEOUT)
        assert r.status_code == 200
        return self.parse_synths(r)

    def parse_synths(self, r):
        synths = {}
        for chunk in r.text.split('<source src="')[1:]:
            synth_url, rem = chunk.split('"', maxsplit=1)
            synth_name = rem.split('<p class="card-text">', maxsplit=1)[1].split('</p>', maxsplit=1)[0].strip()
            synths[synth_name] = synth_url
        return synths

    def download_synth_preview(self, synth_name):
        r = self.session.get(self.url + f'/synth/USER/{synth_name}', timeout=gamelib.TIMEOUT)
        assert r.status_code == 200
        assert r.content.startswith(b'RIFF')
        return r.content

    def create_loop(self, loop_name, loop):
        r = self.session.post(self.url + '/create_loop', {"loop": json.dumps(loop), "loop_name": loop_name},
                              timeout=gamelib.TIMEOUT)
        assert r.status_code == 200
        loops = self.parse_loops(r)
        assert loop_name in loops
        loop_id, public = loops[loop_name]
        assert not public
        return loop_id

    def list_loops(self):
        r = self.session.get(self.url + '/loops', timeout=gamelib.TIMEOUT)
        assert r.status_code == 200
        return self.parse_loops(r)

    def parse_loops(self, r):
        loops = {}
        for chunk in r.text.split('<source src="')[1:]:
            loop_url, rem = chunk.split('"', maxsplit=1)
            loop_id = int(loop_url.rsplit('/', maxsplit=1)[1])
            loop_name = rem.split('<p class="card-text">', maxsplit=1)[1].split('</p>', maxsplit=1)[0].strip()
            is_public = '/publish/' not in rem
            loops[loop_name] = (loop_id, is_public)
        return loops

    def publish_loop(self, loop_id):
        r = self.session.get(self.url + f'/publish/{loop_id}', timeout=gamelib.TIMEOUT)
        assert r.status_code == 200

    def download_loop(self, loop_id):
        r = self.session.get(self.url + f'/loops/{loop_id}', timeout=gamelib.TIMEOUT)
        assert r.status_code == 200
        assert r.content.startswith(b'RIFF')
        return r.content


# See the "SampleServiceInterface" from gamelib for a bigger example
# See https://gitlab.saarsec.rocks/saarctf/gamelib/-/blob/master/docs/howto_checkers.md for documentation.

PORT = 11025
SAMPLE_CREDENTIALS_KEY = 'sample_credentials'
SAMPLE_FLAG = 0
SYNTH_FLAG = 1
SYNTH_CREDENTIALS_KEY = 'synth_credentials'
FLAG_LOOP_KEY = 'flag_loop'


class SaarloopInterface(ServiceInterface):
    name = 'Saarloop'
    flag_id_types = ['pattern:${username}:samples/${hex8}', 'pattern:${username}:synth/${hex8}']

    def check_integrity(self, team: Team, tick: int):
        url_base = f'http://{team.ip}:{PORT}/'
        # pwntools "Could not connect" exception is accepted as OFFLINE
        gamelib.assert_requests_response(requests.get(url_base, timeout=gamelib.TIMEOUT), 'text/html; charset=utf-8')

    def store_flags(self, team: Team, tick: int):
        self.store_sample_flag(team, tick)
        self.store_synth_flag(team, tick)

    def store_sample_flag(self, team: Team, tick: int):
        if self.load(team, tick, SAMPLE_CREDENTIALS_KEY) is not None:
            # credentials stored? -> setting flag succeeded before
            return

        api = SaarloopAPI(f'http://{team.ip}:{PORT}')
        sample_flag = self.get_flag(team, tick, SAMPLE_FLAG)
        sample_flag_id = self.get_flag_id(team, tick, SAMPLE_FLAG)

        username = sample_flag_id.split(':', maxsplit=1)[0]
        password = usernames.generate_password()
        api.register(username, password)

        sample_name = sample_flag_id.rsplit('/', maxsplit=1)[1]
        sample_buf = gen_flag_sample(sample_flag)
        api.upload_sample(sample_name, sample_buf)
        self.store(team, tick, SAMPLE_CREDENTIALS_KEY, [username, password])

    def store_synth_flag(self, team: Team, tick: int):
        if self.load(team, tick, SYNTH_CREDENTIALS_KEY) is not None:
            # credentials stored? -> setting flag succeeded before
            return

        api = SaarloopAPI(f'http://{team.ip}:{PORT}')
        synth_flag = self.get_flag(team, tick, SYNTH_FLAG)
        synth_flag_id = self.get_flag_id(team, tick, SYNTH_FLAG)

        username = synth_flag_id.split(':', maxsplit=1)[0]
        password = usernames.generate_password()
        api.register(username, password)

        flag_synth = bytes_to_synth(synth_flag.encode())
        synth_name = synth_flag_id.rsplit('/', maxsplit=1)[1]
        api.create_synth(synth_name, flag_synth)

        loop_id = api.create_loop(usernames.generate_name(), gen_loop())
        api.publish_loop(loop_id)

        self.store(team, tick, SYNTH_CREDENTIALS_KEY, [username, password])

    def retrieve_flags(self, team: Team, tick: int):
        self.retrieve_sample_flags(team, tick)
        self.retrieve_synth_flags(team, tick)

    def retrieve_sample_flags(self, team: Team, tick: int):
        stored_info = self.load(team, tick, SAMPLE_CREDENTIALS_KEY)
        if stored_info is None:
            raise FlagMissingException("Store of flag failed before")
        username, password = stored_info
        api = SaarloopAPI(f'http://{team.ip}:{PORT}')
        api.login(username, password)

        sample_flag_id = self.get_flag_id(team, tick, SAMPLE_FLAG)
        sample_name = sample_flag_id.rsplit('/', maxsplit=1)[1]

        sample_content = api.download_sample(sample_name)
        sample_flag = self.get_flag(team, tick, SAMPLE_FLAG)

        if sample_flag.encode() not in sample_content:
            raise FlagMissingException('Flag not found')

    def retrieve_synth_flags(self, team: Team, tick: int):
        stored_info = self.load(team, tick, SYNTH_CREDENTIALS_KEY)
        if stored_info is None:
            raise FlagMissingException("Store of flag failed before")
        username, password = stored_info
        api = SaarloopAPI(f'http://{team.ip}:{PORT}')
        api.login(username, password)

        flag_loop_id = self.load(team, tick, FLAG_LOOP_KEY)

        if flag_loop_id is None:
            synth_flag_id = self.get_flag_id(team, tick, SYNTH_FLAG)
            synth_name = synth_flag_id.rsplit('/', maxsplit=1)[1]
            loop_length = random.choice([1, 2, 4, 8])
            flag_loop = {
                "bpm": random.randint(80, 160),
                "length": loop_length,
                "tracks": [
                    {
                        "type": "SYNTH_USER",
                        "id": synth_name,
                        "vol": 1.0,
                        "env": {"a": 0, "d": 0, "s": 1.0, "r": 0},
                        "notes": [{
                            "p": 41, "t": random.randint(0, loop_length - 1), "d": 1
                        }]
                    }
                ]
            }

            flag_loop_id = api.create_loop(usernames.generate_name(random.randint(1, 4)), flag_loop)
            self.store(team, tick, FLAG_LOOP_KEY, flag_loop_id)

        flag_loop_content = api.download_loop(flag_loop_id)

        synth_flag = self.get_flag(team, tick, SYNTH_FLAG)

        if synth_flag.encode() not in flag_loop_content:
            raise FlagMissingException('Flag not found')


if __name__ == '__main__':
    # USAGE: python3 interface.py                      # test against localhost
    # USAGE: python3 interface.py 1.2.3.4              # test against IP
    # USAGE: python3 interface.py 1.2.3.4 retrieve     # retrieve last 10 ticks (for exploits relying on checker interaction)
    # (or use gamelib/run-checkers to test against docker container)
    import sys

    team = Team(1, 'TestTeam', sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1')
    service = SaarloopInterface(1)

    if len(sys.argv) > 2 and sys.argv[2] == 'retrieve':
        for tick in range(1, 10):
            try:
                service.retrieve_flags(team, tick)
            except:
                pass
        sys.exit(0)

    for tick in range(1, 4):
        print(f'\n\n=== TICK {tick} ===')
        service.check_integrity(team, tick)
        service.store_flags(team, tick)
        service.retrieve_flags(team, tick)
