from gamelib import *
from pwn import remote
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps
from pyzbar.pyzbar import decode, ZBarSymbol
import os
import hashlib
import sys

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PORT = 8000
# See the "SampleServiceInterface" from gamelib for a bigger example
# See https://gitlab.saarsec.rocks/saarctf/gamelib/-/blob/master/docs/howto_checkers.md for documentation.


FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SourceCodePro-Regular.ttf")
if not os.path.exists(FONT_PATH):
    response = requests.get('https://github.com/adobe-fonts/source-code-pro/raw/release/TTF/SourceCodePro-Regular.ttf')
    assert response.status_code == 200
    with open(FONT_PATH, 'wb') as f:
        f.write(response.content)


def decode_qrcode(qrcode):
    img = Image.new('RGB', (2000, 2000))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_PATH, 40)
    d.text((0, 0), qrcode, fill=(255, 255, 255), font=font)
    img = ImageOps.invert(img)

    data = decode(img, symbols=[ZBarSymbol.QRCODE])
    return data[0].data

class SaarbahnInterface(ServiceInterface):
    name = 'Saarbahn'
    p=None
    flag_id_types = ["email"]


    def check_integrity(self, team: Team, tick: int):
        # pwntools "Could not connect" exception is accepted as OFFLINE
        try:
            r = requests.get(f"https://{team.ip}:{PORT}/",timeout=gamelib.TIMEOUT, verify=False)
            assert_requests_response(r, 'text/html; charset=utf-8')
        except:
        	raise OfflineException('Could not connect!')
        return

    def store_flags(self, team: Team, tick: int):
        username = self.get_flag(team, tick, 1)
        first = usernames.generate_name(words=1)
        last = usernames.generate_name(words=1)
        email = self.get_flag_id(team, tick, 0)  # a valid-looking username
        password = hashlib.sha256(("seeeecretsaarsec"+email).encode()).hexdigest()
        username2 = usernames.generate_username()
        first2 = usernames.generate_name(words=1)
        last2 = usernames.generate_name(words=1)
        email2 = usernames.generate_name(words=1)+"@"+usernames.generate_name(words=1)+".com"
        password2 = usernames.generate_password()
        print(f'Storing flag for user {username} / email {email} / password {password}')
        flag0 = self.get_flag(team, tick, 0)
        try:
            s2 = requests.Session()
            s = requests.Session()
            register_data = {"username": username2, "first": first2, "last": last2, "email": email2, "password": password2}
            r = s2.post(f"https://{team.ip}:{PORT}/register",data=register_data,timeout=gamelib.TIMEOUT, verify=False)
            assert_requests_response(r, 'text/html; charset=utf-8')
            r = s2.get(f"https://{team.ip}:{PORT}/generate_ticket",timeout=gamelib.TIMEOUT, verify=False)
            assert_requests_response(r, 'text/html; charset=utf-8')
            try:
                qrcode = r.text.split('<code style="display: block; white-space: pre">')[1].split('</code>')[0]
            except:
                raise MumbleException('Could not get QR code')
            register_data = {"username": username, "first": first, "last": last, "email": email, "password": password}
            r = requests.post(f"https://{team.ip}:{PORT}/register",data=register_data,timeout=gamelib.TIMEOUT, verify=False)
            assert_requests_response(r, 'text/html; charset=utf-8')
            login_data = {"email": email, "password": password}
            r = s.post(f"https://{team.ip}:{PORT}/login",data=login_data,timeout=gamelib.TIMEOUT, verify=False)
            assert_requests_response(r, 'text/html; charset=utf-8')
            comment_data = {"comment": f"This is a very nice place to store my secrets. Like this: {flag0}"}
            r = s.post(f"https://{team.ip}:{PORT}/profile",data=comment_data,timeout=gamelib.TIMEOUT, verify=False)
            assert_requests_response(r, 'text/html; charset=utf-8')
            friend = usernames.generate_name(words=1)+"@"+usernames.generate_name(words=1)+".com"
            r = s.post(f"https://{team.ip}:{PORT}/generate_group_ticket",data={"friends": [email2, friend]},timeout=gamelib.TIMEOUT, verify=False)
            assert_requests_response(r, 'text/html; charset=utf-8')
            try:
                qrcode = r.text.split('<code style="display: block; white-space: pre">')[1].split('</code>')[0]
            except:
                raise MumbleException('Could not get QR code')
            try:
                jsonn = decode_qrcode(qrcode)
            except:
                raise MumbleException('Could not decode QR code')
            if email2.encode() not in jsonn or friend.encode() not in jsonn:
                raise MumbleException("QR code does not contain friend's email")
            if email.encode() not in jsonn:
                raise MumbleException("QR code does not contain user's email")
            r = requests.post(f"https://{team.ip}:{PORT}/quick_login",data={"ticket": jsonn},timeout=TIMEOUT, verify=False)
            assert_requests_response(r, 'text/html; charset=utf-8')
            if r.url != f"https://{team.ip}:{PORT}/profile":
                raise MumbleException("quick_login failed")
            r = s.get(f"https://{team.ip}:{PORT}/logout",timeout=gamelib.TIMEOUT, verify=False)
            assert_requests_response(r, 'text/html; charset=utf-8')

            self.store(team, tick, 'credentials', [email, password])
        except requests.exceptions.ConnectTimeout:
            raise OfflineException('Could not connect!')
        except requests.exceptions.ConnectionError:
            raise OfflineException('Could not connect!')
        except requests.exceptions.ReadTimeout:
            raise OfflineException('Could not connect!')
        except requests.exceptions.HTTPError:
            raise MumbleException('HTTPerror')
        except requests.exceptions.TooManyRedirects:
            raise MumbleException('TooManyRedirects')
        finally:
            s.close()
            s2.close()

    def retrieve_flags(self, team: Team, tick: int):
        flag = self.get_flag(team, tick, 0)
        flag2 = self.get_flag(team, tick, 1)
        try:
            [email, password] = self.load(team, tick, 'credentials')
        except:
            # no flag if we cannot get creds
            raise FlagMissingException('Flag not found')
        flag_data = ""
        try:
            s = requests.Session()
            login_data = {"email": email, "password": password}
            r = s.post(f"https://{team.ip}:{PORT}/login",data=login_data,timeout=gamelib.TIMEOUT, verify=False)
            assert_requests_response(r, 'text/html; charset=utf-8')
            r = s.get(f"https://{team.ip}:{PORT}/profile",timeout=gamelib.TIMEOUT, verify=False)
            assert_requests_response(r, 'text/html; charset=utf-8')
            flag_data = r.text
            r = s.get(f"https://{team.ip}:{PORT}/logout",timeout=gamelib.TIMEOUT, verify=False)
            assert_requests_response(r, 'text/html; charset=utf-8')
            self.store(team, tick, 'credentials', [email, password])
        except requests.exceptions.ConnectTimeout:
            raise OfflineException('Could not connect!')
        except requests.exceptions.ConnectionError:
            raise OfflineException('Could not connect!')
        except requests.exceptions.ReadTimeout:
            raise OfflineException('Could not connect!')
        except requests.exceptions.HTTPError:
            raise MumbleException('HTTPerror')
        except requests.exceptions.TooManyRedirects:
            raise MumbleException('TooManyRedirects')
        finally:
            s.close()
        if flag not in flag_data or flag2 not in flag_data:
            # verbose error logging is always a good idea
            print('GOT:', flag_data)
            # flag not found? Raise FlagMissingException
            raise FlagMissingException('Flag not found')


if __name__ == '__main__':
    # USAGE: python3 interface.py                      # test against localhost
    # USAGE: python3 interface.py 1.2.3.4              # test against IP
    # USAGE: python3 interface.py 1.2.3.4 retrieve     # retrieve last 10 ticks (for exploits relying on checker interaction)
    # (or use gamelib/run-checkers to test against docker container)
    team = Team(1, 'TestTeam', sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1')
    service = SaarbahnInterface(1)

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
