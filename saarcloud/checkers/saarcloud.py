import sys
import time
import websocket

try:
    from checkers.website_generator import gen_website_lambda, Website, gen_website_cdn, SaarCloudSession, gen_website_rds, fill_rds_site_with_demo_data, check_rds_site_demo_data, check_lambda_tests
except ImportError:
    from .website_generator import gen_website_lambda, Website, gen_website_cdn, SaarCloudSession, gen_website_rds, fill_rds_site_with_demo_data, check_rds_site_demo_data, check_lambda_tests

from gamelib import *


TABLE_SQL = '''
CREATE TABLE data (
id integer PRIMARY KEY,
name text NOT NULL,
value text NOT NULL
);
'''.strip()


def sanitizeUser(user: str) -> str:
    user = re.sub(r'[^A-Za-z0-9_]', '', user)[:64].lower()
    return user


class SaarCloudServiceInterface(ServiceInterface):
    name = 'SaarCloud'

    def check_integrity(self, team: Team, tick: int):
        s = SaarCloudSession(team, verbose=True)
        response = s.get('/')
        assert_requests_response(response, 'text/html; charset=utf-8')
        assert response.headers['server'] == 'drogon/1.7.5', 'Invalid server'
        # TODO do we want this?
        assert response.headers['content-encoding'] == 'br', 'Encoding is not brotli'
        x = usernames.generate_random_string()
        response = s.get(f'/hello/{x}')
        assert_requests_response(response, 'text/plain; charset=utf-8')

    def store_flags(self, team: Team, tick: int):
        # username 1 / flag 1: store stuff in SaarRDS database
        username1 = sanitizeUser(usernames.generate_username(False, False))
        flag1 = self.get_flag(team, tick)
        session = SaarCloudSession(team, verbose=True)
        website = gen_website_rds(username1, flag1, team.id + tick)

        response = assert_requests_response(session.post('/api/register/rds', json={'username': website.rds_name}))
        assert 'token' in response.json()
        token1 = response.json()['token']
        self.store(team, tick, 'user1', [username1, token1, website.secret, website.rds_name])
        print(f'Registered user 1/2 "{website.rds_name}" / "{token1}"')
        session.upload_rds_sql(website, token1)
        website.lambda_script = website.lambda_script.replace('<dbtoken>', token1)

        response = assert_requests_response(session.post('/api/register/lambda', json={'username': username1}))
        assert 'token' in response.json()
        token12 = response.json()['token']
        print(f'Registered user 2/2 "{username1}" / "{token12}"')
        session.upload_lambda_script(website, token12)
        session.upload_cdn_files(website, token12)
        assert_requests_response(session.post('/api/feature', json={'username': username1, 'feature': 'rds'}))

        fill_rds_site_with_demo_data(SaarCloudSession(team, username1, verbose=True), website)
        self.store(team, tick, 'rds', [website.api_base, website.data])

        # username 2 / flag 2: store stuff inside SaarLambda script
        username2 = sanitizeUser(usernames.generate_username(False, False))
        session = SaarCloudSession(team, verbose=True)
        response = assert_requests_response(session.post('/api/register/lambda', json={'username': username2}))
        assert 'token' in response.json()
        token2 = response.json()['token']
        website = gen_website_lambda(username2, self.get_flag(team, tick, 1), team.id + tick)
        self.store(team, tick, 'user2', [username2, token2, website.secret])
        print(f'Registered user "{username2}" / "{token2}"')

        session.upload_lambda_script(website, token2)
        session.upload_cdn_files(website, token2)
        assert_requests_response(session.post('/api/feature', json={'username': username2, 'feature': 'lambda'}))

        # test correct V8 functionality by triggering some unit tests:
        check_lambda_tests(SaarCloudSession(team, username2, verbose=True), website.data)

        # username 3 / flag 3: store in secret file in SaarCDN
        username3 = sanitizeUser(usernames.generate_username(False, False))
        flag3 = self.get_flag(team, tick, 2)
        session = SaarCloudSession(team, verbose=True)
        response = assert_requests_response(session.post('/api/register/cdn', json={'username': username3}))
        assert 'token' in response.json()
        token3 = response.json()['token']
        log_token3 = response.json()['log_token']
        website = gen_website_cdn(username3, flag3, team.id + tick)
        self.store(team, tick, 'user3', [username3, token3, log_token3, website.secret])
        print(f'Registered user "{username3}" / "{token3}" / "{log_token3}"')

        session.upload_cdn_files(website, token3)
        assert_requests_response(session.post('/api/feature', json={'username': username3, 'feature': 'cdn'}))

        pass

    def retrieve_flags(self, team: Team, tick: int):
        # username 1 / flag 1: store stuff in SaarRDS database
        flag1 = self.get_flag(team, tick)
        try:
            username1, token1, issue_id, username_rds = self.load(team, tick, 'user1')
            api_base, website_data = self.load(team, tick, 'rds')
        except TypeError:
            raise FlagMissingException('Flag never stored')
        session_default = SaarCloudSession(team, verbose=True)
        response = assert_requests_response(session_default.get(f'/api/rds/{username_rds}/appendonly_issues/select', params={'token': token1, 'where': json.dumps({'id': issue_id})}))
        data = response.json()
        assert len(data) >= 1
        if flag1 not in data[0].get('text', ''):
            raise FlagMissingException(f'Flag not found in database {username1}')
        session = SaarCloudSession(team, hostname=username1, verbose=True)
        response = assert_requests_response(session.get(f'{api_base}/issues/{issue_id}'))
        if flag1 not in response.json().get('issue', {}).get('text', ''):
            raise FlagMissingException(f'Flag not found in service {username1}')
        # check that demo data is still stored in service
        check_rds_site_demo_data(session, api_base, website_data)

        response = assert_requests_response(session_default.get('/api/featured'))
        featured = response.json()
        assert any(feature['name'] == username1 for feature in featured['rds']), f'User {username1} not in featured list'

        # username 2 / flag 2: store stuff inside SaarLambda script
        flag2 = self.get_flag(team, tick, 1)
        try:
            username2, token2, passwd = self.load(team, tick, 'user2')
        except TypeError:
            raise FlagMissingException('Flag never stored')
        session = SaarCloudSession(team, hostname=username2, verbose=True)
        response = assert_requests_response(session.post('/admin', json={'password': passwd}))
        if response.json()['latest_user'] != flag2:
            raise FlagMissingException(f'Flag not found in Lambda response for {username2}')
        assert any(feature['name'] == username2 for feature in featured['lambda']), f'User {username2} not in featured list'

        # username 3 / flag 3: store in secret file in SaarCDN
        flag3 = self.get_flag(team, tick, 2)
        try:
            username3, token3, log_token3, filename = self.load(team, tick, 'user3')
        except TypeError:
            raise FlagMissingException('Flag never stored')
        session = SaarCloudSession(team, hostname=username3, verbose=True)

        # Connect a websocket to the /logs endpoint (to see that our cdn request gets actually logged)
        print('> * WS ' + session_default.websocket_base + f'/logs?user={username3}&token={log_token3}')
        ws = websocket.create_connection(session_default.websocket_base + f'/logs?user={username3}&token={log_token3}', timeout=TIMEOUT//2)
        try:
            time.sleep(0.5)

            response = session.get('/')
            assert_requests_response(response, contenttype='text/html; charset=utf-8')
            assert 'Your digital store' in response.text, 'index.html file not properly delivered'
            response = session.get(f'/{filename}')
            assert_requests_response(response, contenttype='text/plain; charset=utf-8')
            if flag3 not in response.text:
                raise FlagMissingException(f'Flag not found in CDN response for {username3}')
            assert any(feature['name'] == username3 for feature in featured['cdn']), f'User {username3} not in featured list'

            try:
                while True:
                    msg = ws.recv()
                    print('[ws]', repr(msg))
                    if f'"GET /{username3}/{filename}"' in msg:
                        break
            except websocket.WebSocketTimeoutException:
                raise MumbleException(f"/logs endpoint for {username3} did not show logs in time")
        finally:
            ws.close()

        pass


if __name__ == '__main__':
    retrieve_only = 'retrieve' in sys.argv
    if retrieve_only:
        service = SaarCloudServiceInterface(1)
        team = Team(3, 'Test', '127.1.0.1' if len(sys.argv) <= 1 else sys.argv[1])
        ticks = range(1, 50)
        for tick in ticks:
            try:
                service.retrieve_flags(team, tick)
            except OfflineException:
                raise
            except:
                pass
        sys.exit(0)

    if 'brotlicheck' in sys.argv:
        team = Team(3, 'Test', '127.1.0.1' if len(sys.argv) <= 1 else sys.argv[1])
        s = SaarCloudSession(team)
        r = s.get('/')
        print(r, r.headers['Content-Encoding'] if 'Content-Encoding' in r.headers else '-', r.content[:20])
        r = s.get('/static/css/2.b52db17f.chunk.css')
        print(r, r.headers['Content-Encoding'] if 'Content-Encoding' in r.headers else '-', r.content[:20])
        r = s.get('/api/featured')
        print(r, r.headers['Content-Encoding'] if 'Content-Encoding' in r.headers else '-', r.content[:20])
        s = SaarCloudSession(team, 'workablemuddledascot8713')
        r = s.get('/paid_content_4FHxoDuVLbhz5J0cs3PCF6Ja.txt')
        print(r, r.headers['Content-Encoding'] if 'Content-Encoding' in r.headers else '-', r.content[:20])
        sys.exit(0)

    service = SaarCloudServiceInterface(1)
    team = Team(3, 'Test', '127.1.0.1' if len(sys.argv) <= 1 else sys.argv[1])
    ticks = range(1, 4)
    for tick in ticks:
        print(f'=== {tick} ===')
        if not retrieve_only:
            service.check_integrity(team, tick)
            service.store_flags(team, tick)
        service.retrieve_flags(team, tick)
    print("=== DONE ===")
