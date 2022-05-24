import sys
import requests

from gamelib import *


class SampleServiceInterface(ServiceInterface):
    name = 'SampleService'

    def check_integrity(self, team, tick):
        try:
            assert_requests_response(requests.get('http://{}:8000/'.format(team.ip)), 'text/html; charset=utf-8')
        except IOError:
            raise OfflineException('Could not login')

    def store_flags(self, team, tick):
        username = usernames.generate_username()
        password = usernames.generate_password()
        self.store(team, tick, 'credentials', [username, password])

        try:
            flag = self.get_flag(team, tick, 1)
            response = assert_requests_response(
                requests.post('http://{}:8000/register'.format(team.ip), data={'username': username, 'password': password, 'flag': flag}),
                'text/html; charset=utf-8'
            )
            assert 'Flag stored!' in response.text
            return 1
        except IOError:
            raise OfflineException('Could not register')

    def retrieve_flags(self, team, tick):
        username, password = self.load(team, tick, 'credentials')
        try:
            session = requests.Session()
            assert_requests_response(
                session.post('http://{}:8000/login'.format(team.ip), data={'username': username, 'password': password}),
                'text/html; charset=utf-8'
            )

            response = assert_requests_response(session.get('http://{}:8000/data'.format(team.ip)), 'text/html; charset=utf-8')
            # V1 - easy check for flag
            flag = self.get_flag(team, tick, 1)
            if flag not in response.text:
                raise FlagMissingException("Flag not found")

            # V2 - advanced check with payload
            flags = self.search_flags(response.text)
            assert len(flags) > 0, 'No flags found'
            flag = list(flags)[0]
            _, _, _, payload = self.check_flag(flag, team.id, tick)  # returns None,None,None,None if invalid
            if not flag or not payload or payload != 1:
                # not the flag we're looking for
                raise FlagMissingException("Flag not found")

            return 1
        except IOError:
            raise OfflineException('Could not login')


if __name__ == '__main__':
    # TEST CODE
    team = Team(12, 'n00bs', '127.0.0.1')
    tick = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    service = SampleServiceInterface(7)

    print('[1] Integrity check...')
    service.check_integrity(team, tick)
    print('Passed.')

    print('[2] Store flags...')
    flags = service.store_flags(team, tick)
    print('Done ({} flags).'.format(flags))

    print('[3] Retrieve the flags in the next tick')
    flags = service.retrieve_flags(team, tick)
    print('Done ({} flags).'.format(flags))
