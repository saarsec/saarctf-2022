import glob
import json
import os.path
import random
import shutil
import string
import subprocess
import sys
import traceback
from typing import Tuple, Union, List

try:
    from website_generator import gen_website_lambda, SaarCloudSession, Website, set_demo_site
except ImportError:
    from .website_generator import gen_website_lambda, SaarCloudSession, Website, set_demo_site

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
INPUT_PATH = BASE_PATH + '/../jstests/working_tests'
OUTPUT_PATH = BASE_PATH + '/working_tests'


class Team:
    def __init__(self, ip):
        self.ip = ip


def generate_random_string(l=8, alphanum=True) -> str:
    s = string.ascii_letters + string.digits if alphanum else string.ascii_letters
    return ''.join(random.choice(s) for _ in range(l))


def read_file(fname: str, mode: str = 'r') -> Union[str, bytes]:
    with open(fname, mode) as f:
        return f.read()


def write_file(fname: str, content: Union[str, bytes]):
    with open(fname, 'w' if isinstance(content, str) else 'wb') as f:
        return f.write(content)


def check_site_works(session: SaarCloudSession, website: Website, check_css: bool):
    response = session.get('/')
    assert response.status_code == 200
    assert response.headers['content-type'] == 'text/html; charset=utf-8'
    assert response.text.startswith('<!DOCTYPE html><html lang="en"><meta charset="utf-8"><meta http-equiv="X-UA-Compatible"')

    response = session.post('/admin', json={'password': website.secret})
    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/json; charset=utf-8'
    assert response.json()['latest_user'] == 'SAAR{test}'

    response = session.post('/admin', json={'password': 'wrong_password!'})
    assert response.status_code == 500
    assert response.headers['content-type'] == 'text/html; charset=utf-8'
    assert response.text.startswith('Error:')

    if check_css:
        for _ in range(2):
            response = session.get('/semantic.min.css')
            assert response.status_code == 200
            assert response.headers['content-type'] == 'text/css; charset=utf-8'
            assert response.text.startswith('/*')


def strip_license(content: str) -> Tuple[str, str]:
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        if lines[i].strip() != '' and not lines[i].startswith('//'):
            break
        i += 1
    return '\n'.join(lines[:i]) + '\n', '\n'.join(lines[i:])


def minify_js(original_code: str) -> str:
    license, code = strip_license(original_code)
    code = 'function CONTAINER(){\n' + code + '\n}'
    try:
        output = subprocess.check_output(['terser', '-c', 'defaults=false,drop_console=true,drop_debugger=true,ecma=2015'], input=code.encode('utf-8'))
        code = output.decode('utf-8').strip()
        assert code.startswith('function CONTAINER(){')
        assert code.endswith('}')
        return license + code[21:-1]
    except:
        traceback.print_exc()
        return original_code


def validate_test(team, testfile: str, solutionfile: str) -> Tuple[bool, str, str]:
    script = read_file(testfile)
    if 'toString' not in testfile and 'dfg-redundant-load-of-captured-variable-proven-constant' not in testfile and 'do-while-semicolon' not in testfile:
        script = minify_js(script)
    solution = json.loads(read_file(solutionfile))

    # stuff works in raw v8?
    username = 'test' + generate_random_string(12, False).lower()
    website = gen_website_lambda(username, 'SAAR{test}', 0)
    website.lambda_script += '\n\n\nLambdaRequests.get(/^\\/run_test$/, (___request, ___match) => {\n' + script + '\n});\n'
    session_admin = SaarCloudSession(team)
    response = session_admin.post('/api/register/lambda', json={'username': website.username})
    token = response.json()['token']
    session_admin.upload_lambda_script(website, token)
    session_admin.upload_cdn_files(website, token)

    session = SaarCloudSession(team, website.username)
    check_site_works(session, website, False)
    response = session.get('/run_test')
    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/json; charset=utf-8'
    result = response.json()
    print(result)
    print(solution)
    if result != solution:
        return False, 'Solution not reproduced', ""

    # stuff does not damage real logic
    check_site_works(session, website, False)

    # stuff can be repeated
    for i in range(2, 5):
        response = session.get('/run_test')
        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/json; charset=utf-8'
        result = response.json()
        print(result)
        print(solution)
        if result != solution:
            return False, f'Solution not reproduced a {i}-th time', ""

    check_site_works(session, website, True)

    return True, "", script


def run_tests(team, input_files: List[str], copy_working: bool) -> Tuple[int, int, int]:
    logs = []
    ok = 0
    fail = 0
    crash = 0

    for f in input_files:
        print(f'+++++ {f} +++++')
        try:
            result, msg, script = validate_test(team, f, f + 'on')
            if result:
                print('OK')
                ok += 1
                if copy_working:
                    write_file(os.path.join(OUTPUT_PATH, os.path.basename(f)), script)
                    shutil.copy(f + 'on', os.path.join(OUTPUT_PATH, os.path.basename(f + 'on')))
            else:
                logs.append(f'FAIL  {f} {msg}')
                fail += 1
        except Exception as e:
            traceback.print_exc()
            logs.append(f'CRASH {f} {e}')
            crash += 1
    print(f'ok:    {ok}')
    print(f'fail:  {fail}')
    print(f'crash: {crash}')
    if len(logs) > 0:
        write_file('errors.log', '\n'.join(logs) + '\n')
    return ok, fail, crash


def main():
    team = Team('127.1.0.1' if len(sys.argv) <= 2 else sys.argv[2])
    if sys.argv[1] == 'build':
        os.makedirs(OUTPUT_PATH, exist_ok=True)
        # input_files = [INPUT_PATH + '/webkit/string-substr.js']
        # input_files = [INPUT_PATH + '/webkit/gmail-re-re.js']
        input_files = glob.glob(INPUT_PATH + '/webkit/*.js')
        input_files += glob.glob(INPUT_PATH + '/webkit/fast/*/*.js')
        input_files = [f for f in input_files if not f.endswith('.orig.js')]
        run_tests(team, input_files, True)
    elif sys.argv[1] == 'check':
        input_files = glob.glob(OUTPUT_PATH + '/*.js')
        ok, fail, crash = run_tests(team, input_files, False)
        assert ok == len(input_files)
        assert fail == 0
        assert crash == 0
        assert ok > 0
        print('[DONE] All good!')
    else:
        raise Exception('Invalid subcommand. Try: build, check')


if __name__ == '__main__':
    set_demo_site()
    main()
