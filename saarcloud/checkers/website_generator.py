import glob
import os
import random
import socket
import string
from typing import Union, Dict

import requests

try:
    from gamelib import *
    from gamelib.usernames import generate_username
except ImportError:
    TIMEOUT = 5


    def assert_requests_response(response):
        assert response.status_code < 300
        return response


    def generate_username():
        return generate_random_string(24)


def generate_random_string(l=8, alphanum=True):
    s = string.ascii_letters + string.digits if alphanum else string.ascii_letters
    return ''.join(random.choice(s) for _ in range(l))


def read_file(fname: str, mode: str = 'r') -> Union[str, bytes]:
    with open(fname, mode) as f:
        return f.read()


def read_test_script(fname: str):
    lines = read_file(fname).split('\n')
    return '\n'.join(l for l in lines if not l.startswith('//')).strip()


# load websites
SITES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sites')
SEMANTIC_CSS = [read_file(fname, 'rb') for fname in sorted(glob.glob(os.path.join(SITES_PATH, 'cdnstore', 'semantic-*.min.css')))]
CDN_INDEX = read_file(os.path.join(SITES_PATH, 'cdnstore', 'index.html'))
PRIMARY_COLORS = ['primary', 'red', 'green', 'teal', 'blue', 'violet', 'purple', 'pink', 'brown']
LAMBDA_INDEX = read_file(os.path.join(SITES_PATH, 'lambdaadmin', 'index.html'))
RDS_INDEX = read_file(os.path.join(SITES_PATH, 'issues', 'index.html'))
RDS_SCRIPT = read_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'issues.js'))
TEST_SCRIPT_FILES = list(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'working_tests', '*.js')))
IS_DEMO_SITES = False


def set_demo_site():
    global IS_DEMO_SITES
    IS_DEMO_SITES = True


class Website:
    def __init__(self, username: str, secret):
        self.username = username
        self.secret = secret
        self.api_base = '/api'
        self.lambda_script: Optional[str] = None
        self.cdn_files: Dict[str, Union[str, bytes]] = {}
        self.rds_name: Optional[str] = None
        self.rds_sql: List[str] = []
        self.data = []

    def __repr__(self):
        s = f'Website {self.username}, secret {self.secret}:'
        for fname, content in self.cdn_files.items():
            s += f'\n  - {fname}: length {len(content)}'
        return s


class SaarCloudSession(requests.Session):
    def __init__(self, team, hostname='default', verbose: bool = False):
        super().__init__()
        if hostname == 'default':
            hostname = 'www'
        if '.' not in team.ip:
            team.ip = socket.gethostbyname(team.ip)
        self.base = f'http://{hostname}.{team.ip}.nip.io:8080'
        self.websocket_base = f'ws://{hostname}.{team.ip}.nip.io:8080'
        self.headers['Accept-Encoding'] = 'br, gzip, deflate'
        self.verbose = verbose

    def get(self, url, **kwargs):
        if self.verbose:
            print('> GET', url)
        if url.startswith('/'):
            url = self.base + url
        response = super().get(url, timeout=TIMEOUT, **kwargs)
        if self.verbose:
            print('<', response, response.headers.get('content-type', '-'))
        return response

    def post(self, url, **kwargs):
        if self.verbose:
            print('> POST', url)
        if url.startswith('/'):
            url = self.base + url
        response = super().post(url, timeout=TIMEOUT, **kwargs)
        if self.verbose:
            print('<', response, response.headers.get('content-type', '-'))
        return response

    def upload_rds_sql(self, website: Website, token: str):
        for sql in website.rds_sql:
            assert_requests_response(self.post(f'/api/rds/{website.rds_name}?token={token}', data=sql))

    def upload_lambda_script(self, website: Website, token: str):
        assert_requests_response(self.post(f'/api/lambda/write/{website.username}?token={token}', data=website.lambda_script.encode('utf-8')))

    def upload_cdn_files(self, website: Website, token: str):
        for filename, content in website.cdn_files.items():
            assert_requests_response(self.post(f'/api/cdn/write/{website.username}/{filename}?token={token}', data=content))


def gen_website_lambda(username: str, flag: str, number: int) -> Website:
    number += 1
    passwd = generate_random_string(16)
    website = Website(username, passwd)
    website.lambda_script = '''
    LambdaRequests.post(/^\/admin$/, async (request, match) => {
        if (request.json().password !== 'PASSWORD') {
            debug("Unauthorized Access:", request.json());
            throw new Error("Unauthenticated!");
        }
        return {users: 1337, latest_user: 'FLAG'};
    });
    '''.replace('\n    ', '\n').replace('FLAG', flag).replace('PASSWORD', passwd)
    website.cdn_files['index.html'] = LAMBDA_INDEX \
        .replace('primary', PRIMARY_COLORS[number % len(PRIMARY_COLORS)]) \
        .replace('yourlongusername', username)
    website.cdn_files['semantic.min.css'] = SEMANTIC_CSS[number % len(SEMANTIC_CSS)]

    # add a js-check-utility function to the site (and check with gameserver!)
    if IS_DEMO_SITES:
        website.lambda_script += '\n\n// Websites might have additional handlers, testing the correct functionality of this v8 engine:'
        website.lambda_script += '\nLambdaRequests.get(/^\\/testabc$/, (___request, ___match) => {'
        website.lambda_script += 'var RESULT=[];RESULT.push(JSON.stringify(eval(\'"a b  c".split(/\\\\s+/)\')));return RESULT'
        website.lambda_script += '});\n'
    else:
        website.lambda_script += '\n\n// Handlers testing the correct functionality of this v8 engine'
        tests = ''
        while len(tests) < 2048:
            h = generate_random_string(random.randint(12, 64))
            f = random.choice(TEST_SCRIPT_FILES)
            print(f'Sending unit test {os.path.basename(f)} to handler /{h} ...')
            tests += '\nLambdaRequests.get(/^\\/' + h + '$/, (___request, ___match) => {' + read_test_script(f) + '});\n'
            website.data.append([h, f + 'on'])
            if random.randint(0, 100) < 50:
                break
        website.lambda_script += tests

    return website


def check_lambda_tests(session: SaarCloudSession, data):
    for handler, fname in data:
        response = assert_requests_response(session.get('/' + handler))
        expected = json.loads(read_file(fname))
        assert response.json() == expected, 'V8 test failed (' + os.path.basename(fname[:-2]) + ')'


def gen_website_cdn(username: str, flag: str, number: int) -> Website:
    filename = 'paid_content_' + generate_random_string(24) + '.txt'
    testtoken = generate_random_string(12)
    website = Website(username, filename)
    website.cdn_files['index.html'] = CDN_INDEX.replace('ABCDEFGH', testtoken).replace('yourlongusername', username)
    website.cdn_files['semantic.min.css'] = SEMANTIC_CSS[number % len(SEMANTIC_CSS)]
    website.cdn_files[filename] = f'You paid a lot of money for {flag}!\n'
    website.cdn_files[f'paid_content_{testtoken}.txt'] = 'Welcome! Your flag is in another file!\n'
    return website


def gen_website_rds(username: str, flag: str, number: int) -> Website:
    number += 2
    issue_id = generate_random_string(32)
    website = Website(username, issue_id)
    # website.rds_name = username + random.choice(['', '', '', '_issues', '_db', '_database', '_intern'])
    website.rds_name = username
    website.rds_sql = [
        '''PRAGMA foreign_keys = ON;''',
        '''
        CREATE TABLE appendonly_issues (
            id TEXT NOT NULL PRIMARY KEY,
            title TEXT NOT NULL,
            text TEXT NOT NULL,
            author TEXT NOT NULL,
            public BOOLEAN NOT NULL DEFAULT false,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''',
        '''
        CREATE TABLE appendonly_comments (
            issue_id TEXT NOT NULL REFERENCES appendonly_issues(id),
            text TEXT NOT NULL,
            author TEXT NOT NULL,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''',
        f'''
        INSERT INTO appendonly_issues(id, title, text, author, public) 
        VALUES ('{issue_id}', '{generate_random_string(64)}', 'Found this bug: {flag}', '{generate_random_string(16)}', FALSE);
        '''
    ]
    website.lambda_script = RDS_SCRIPT.replace('<dbname>', website.rds_name)
    website.cdn_files['index.html'] = RDS_INDEX.replace('yourlongusername', username)
    website.cdn_files['semantic.min.css'] = SEMANTIC_CSS[number % len(SEMANTIC_CSS)]
    if not IS_DEMO_SITES:
        randomized_rds_script(website)
    return website


def randomized_rds_script(website: Website):
    # add random comments
    scriptlines = website.lambda_script.split('\n')
    for _ in range(random.randint(0, 5)):
        l = random.randint(0, len(scriptlines))
        scriptlines.insert(l, ' ' * random.randint(0, 8) + '// ' + generate_random_string(random.randint(32, 64)))
    for _ in range(random.randint(0, 3)):
        l = random.randint(0, len(scriptlines) - 1)
        if scriptlines[l] != '':
            scriptlines[l] += ' ' * random.randint(1, 4) + '/* ' + generate_random_string(random.randint(16, 64)) + '*/'
    website.lambda_script = '\n'.join(scriptlines)
    # add random whitespaces
    website.lambda_script = re.sub(r' ', lambda m: ' ' * random.randint(1, 5) if random.randint(0, 100) < 5 else ' ', website.lambda_script)
    website.lambda_script = re.sub(r'\n\n', lambda m: '\n' * random.randint(2, 5) if random.randint(0, 100) < 20 else '\n\n', website.lambda_script)
    # rename variables
    vars = [
        ('request', ['request', 'req', 'rq', 'Request', 'reqst']),
        ('result', ['result', 'r', 'res', 'Result', 'rslt']),
        ('charactersLength', ['charactersLength', 'clen', 'cl', 'len', 'l', 'characters_length']),
        ('characters', ['characters', 'c', 'chars', 'CHARACTERS', 'CHARS', 'str']),
    ]
    for var, alternate_names in vars:
        if random.randint(0, 100) < 50:
            website.lambda_script = website.lambda_script.replace(var, random.choice(alternate_names))
    # replace /api/ path sometimes
    if random.randint(0, 100) < 50:
        website.api_base = '/' + generate_random_string(random.randint(4, 16))
        website.lambda_script = website.lambda_script.replace(r'\/api\/', '\\' + website.api_base + '\\/')
        website.cdn_files['index.html'] = website.cdn_files['index.html'].replace('/api/', website.api_base + '/')


def fill_rds_site_with_demo_data(session: SaarCloudSession, website: Website):
    text = generate_random_string(random.randint(8, 64))
    response = assert_requests_response(session.post(website.api_base + '/issues', json={
        'title': '',
        'text': text,
        'author': generate_username(),
        'public': True
    }))
    issue_id = response.json().get('id')
    assert issue_id
    for _ in range(0, random.randint(1, 4)):
        assert_requests_response(session.post(website.api_base + '/comments', json={
            'issue_id': issue_id,
            'text': generate_random_string(random.randint(8, 64)),
            'author': generate_username()
        }))
    website.data = [issue_id, text]


def check_rds_site_demo_data(session: SaarCloudSession, api_base, data):
    issue_id, text = data
    response = assert_requests_response(session.get(api_base + '/issues'))
    assert any(issue['id'] == issue_id for issue in response.json()), f'Issue {issue_id} not found in site {session.base}'
    response = assert_requests_response(session.get(api_base + '/issues/' + issue_id))
    assert 'issue' in response.json(), 'Key "issue" missing (.../issues/...)'
    assert text == response.json()['issue'].get('text', ''), f'Text in issue {issue_id} wrong'


if __name__ == '__main__':
    website = gen_website_rds('testsite', 'SAAR{ABC}', 0)
    print(website)
