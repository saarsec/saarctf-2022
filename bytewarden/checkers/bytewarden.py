from gamelib import ServiceInterface, usernames, TIMEOUT, Team, assert_requests_response, FlagMissingException, OfflineException
from re import findall
from requests import get
import sys
try:
    from .utils import *
except ImportError:
    from utils import *


#####################################################


class BytewardenServiceInterface(ServiceInterface):
    name = "BytewardenService"
    flag_id_types = ["username", "username"]


    def check_integrity(self, team: Team, tick: int):
        try:
            r = get(f"http://{team.ip}:{PORT}/", timeout = TIMEOUT)
            assert_requests_response(r, "text/html; charset=utf-8")
        except IOError:
            raise OfflineException("Could not display homepage")


    def store_flags(self, team: Team, tick: int):
        
        # Flagstore 1: Question n°10
        credentials = self.load(team, tick, "credentials_flag1")
        if credentials:
            username1, password1 = credentials
        else:
            username1 = self.get_flag_id(team, tick, 0)
            password1 = usernames.generate_password()
            self.store(team, tick, "credentials_flag1", [username1, password1])
        
        flag1 = self.get_flag(team, tick, 0)

        s = register_and_login(team.ip, username1, password1)
        
        for i in range(1, 11):
            question = usernames.generate_random_string(15) if i < 10 else flag1
            answer = usernames.generate_random_string(15)
            post_question(s, team.ip, i, question, answer, username1)
        s.close()


        # Flagstore 2: Password in Password Manager
        credentials = self.load(team, tick, "credentials_flag2")
        if credentials:
            username2, password2 = credentials
        else:
            username2 = self.get_flag_id(team, tick, 1)
            password2 = usernames.generate_password()
            self.store(team, tick, "credentials_flag2", [username2, password2])

        flag2 = self.get_flag(team, tick, 1)

        s = register_and_login(team.ip, username2, password2)
        post_question(s, team.ip, 1, usernames.generate_random_string(15), usernames.generate_random_string(15), username2, True)

        # Get 2FA Code
        code = self.load(team, tick, "code_flag2")
        if not code:
            resp = s.get(f"http://{team.ip}:{PORT}/vault/", timeout = TIMEOUT)
            code = findall(REGEX_2FA_CODE, resp.text)[0]
            self.store(team, tick, "code_flag2", code)

        enter_2fa(s, team.ip, code)

        password_data = {
            "add_title": encrypt("Not a Password", username2),
            "add_url": encrypt("https://ctf.saarland/", username2),
            "add_pwd": encrypt(flag2, username2),
        }

        s.post(f"http://{team.ip}:{PORT}/vault/passwords/", data = password_data, timeout = TIMEOUT)
        s.close()


    def retrieve_flags(self, team: Team, tick: int):
        
        # Flag1: Get Question n° 10
        credentials = self.load(team, tick, "credentials_flag1")
        if credentials:
            username1, password1 = credentials
        else:
            raise FlagMissingException("Flag not found (No credentials stored for flag 1)")

        s = register_and_login(team.ip, username1, password1)
        
        resp = s.get(f"http://{team.ip}:{PORT}/questions/", params = {"num" : 10}, timeout = TIMEOUT)
        try:
            question_question = findall(REGEX_QUESTION_QUESTION, resp.text)[0]
        except IndexError:
            raise FlagMissingException("Flag not found, no regex match for question 10")
        
        flag1 = self.get_flag(team, tick, 0)
        if flag1 != decrypt(question_question, username1):
            raise FlagMissingException("Flag not found, question didn't match flag")
        s.close()

        # Flag2: Get First Password
        credentials = self.load(team, tick, "credentials_flag2")
        if credentials:
            username2, password2 = credentials
        else:
            raise FlagMissingException("Flag not found (No credentials stored for flag 2)")

        s = register_and_login(team.ip, username2, password2)

        code = self.load(team, tick, "code_flag2")
        if not code:
            raise FlagMissingException("Flag not found (No 2FA code stored for flag 2)")

        enter_2fa(s, team.ip, code)
        resp = s.get(f"http://{team.ip}:{PORT}/vault/passwords/", timeout = TIMEOUT)
        try:
            password_password = findall(REGEX_PASSWORD_PASSWORD, resp.text)[0]
        except IndexError:
            raise FlagMissingException("Flag not found, no regex match for password")

        flag2 = self.get_flag(team, tick, 1)
        if flag2 != decrypt(password_password, username2):
                raise FlagMissingException("Flag not found, password didn't match flag")
        s.close()


if __name__ == '__main__':
    # USAGE: python3 interface.py                      # test against localhost
    # USAGE: python3 interface.py 1.2.3.4              # test against IP
    # USAGE: python3 interface.py 1.2.3.4 retrieve     # retrieve last 10 ticks (for exploits relying on checker interaction)
    # (or use gamelib/run-checkers to test against docker container)
    team = Team(1, 'TestTeam', sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1')
    service = BytewardenServiceInterface(1)

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