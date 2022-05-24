import atexit
import glob
import json
import os
import random
import re
import string
import subprocess
import sys
import traceback
from typing import Union, Tuple


def generate_random_string(l=8, alphanum=True):
    s = string.ascii_letters + string.digits if alphanum else string.ascii_letters
    return ''.join(random.choice(s) for _ in range(l))


def read_file(fname: str, mode: str = 'r') -> Union[str, bytes]:
    with open(fname, mode) as f:
        return f.read()


def write_file(fname: str, content: Union[str, bytes]):
    with open(fname, 'w' if isinstance(content, str) else 'wb') as f:
        return f.write(content)


# TEMPFILE = '/tmp/' + generate_random_string(16) + '.js'
# atexit.register(lambda: os.remove(TEMPFILE) if os.path.exists(TEMPFILE) else None)
TEMPFILE = '/tmp/qd81fLgQHxoq8xRn.js'
PREFIX = read_file('collect_results.js')
SUFFIX = '\ndoReportAfterTestsHaveRun();\n'
SUFFIX2 = 'console.log("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\\n" + JSON.stringify(do_the_test()));'
NODE = 'node-v17.6.0-linux-x64/bin/node'

UTILS = {
    'addReportExpr': 'function addReportExpr(expr){ RESULT.push(JSON.parse(JSON.stringify(eval(expr)))); }',
    'addReportExprJson': 'function addReportExprJson(expr){ RESULT.push(JSON.stringify(eval(expr))); }',
    'addReportExprStr': 'function addReportExprStr(expr){ RESULT.push(""+eval(expr)); }',
    'addExceptionExpr': 'function addExceptionExpr(expr){ try{ RESULT.push(JSON.stringify(eval(expr))); } catch(e) { RESULT.push(e.toString()); } }',
}


def strip_license(content: str) -> Tuple[str, str]:
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        if lines[i].strip() != '' and not lines[i].startswith('//'):
            break
        i += 1
    return '\n'.join(lines[:i]) + '\n', '\n'.join(lines[i:])


def isEqual(x, y):
    if x == y:
        return True
    if isinstance(x, list) and isinstance(y, list):
        return len(x) == len(y) and all(isEqual(a, b) for a, b in zip(x, y))
    if isinstance(x, dict) and isinstance(y, dict):
        return len(x) == len(y) and all(k in y and isEqual(y[k] == v) for k, v in x.items())
    return False


def replace_should(m: re.Match) -> str:
    t = m.group(1).strip()
    c = t[-1]
    if c in ("'", '"'):
        matches = [(m2.start(), len(m2.group(0))) for m2 in re.finditer(r',\s+'+c, t)]
        if len(matches) > 0:
            p, l = matches[-1]
            t2 = t[p+l:-1]
            t2 = t2.replace('\\\\', '').replace('\\'+c, '')
            if c not in t2:
                t = t[:p].strip()
                return 'addReportExprJson(' + t + ');'
    for x in [', expected', ', result', ', result[0]', ', result[1]', ', oldValue.toString()', ', "" + expected', ', "" + i']:
        if t.endswith(x):
            t = t[:-len(x)]
            return 'addReportExprJson(' + t + ');'
    print('NOT HANDLED', t)
    return 'addReportExprJson(' + t + ');'


def prepare_test_file(fname):
    content = read_file(fname)
    content_orig = content
    for badword in ['import(', 'include(', 'require(', 'console.']:
        if badword in content:
            print(f'Contains "{badword}"')
            return False

    # remove some useless things
    content = re.sub(r'description\([\s\n]*["\'].*["\'][\s\n]*\);?', '', content)
    content = re.sub(r'description\(\n[\s\n]*["\'](.|\n)*?["\'][\s\n]*\n\);?', '', content)
    content = re.sub(r'description\(\n[\s\n]*["\'](.|\n)*?\n(\s+\'\.\')?\);?', '', content)
    content = re.sub(r'debug\s*\([^\n]*\);?', ';', content)
    content = content.replace('if (this.description)', '')
    license, content = strip_license(content)
    # and fix some others
    content = content.replace(' stringify(', ' JSON.stringify(')

    # do a test run to collect expected stuff
    write_file(TEMPFILE, PREFIX + content + SUFFIX)
    output = subprocess.check_output([NODE, TEMPFILE], timeout=3, stderr=sys.stderr)
    assert b'+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+' in output
    output = output[output.find(b'+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+') + 97:]
    was, expected = json.loads(output.decode())
    print(was)
    print(expected)
    assert len(was) == len(expected)
    errors = sum(0 if isEqual(a, b) else 1 for a, b in zip(was, expected))
    if errors > 0:
        log = read_file(fname.replace('.js', '-expected.txt'))
        log_errors = log.count('FAIL ')
        assert errors == log_errors, f'Had {errors}, log had {log_errors} fails'
        # we now "expect" to fail in the same way
        expected = was
    if len(expected) <= 1:
        print('too short')
        return False
    if len(expected) > 256:
        print('Too many results')
        return False

    # Collect the necessary utils for this test
    # Remove "expected" as good as possible
    prefix = ['var RESULT = [];']
    needed = set()
    for should in ['shouldBeTrue', 'shouldBeFalse', 'shouldBeNull']:
        if should in content:
            content = content.replace(should, 'addReportExpr')
            needed.add('addReportExpr')
    for should in ['shouldBeNaN', 'shouldBeUndefined']:
        if should in content:
            content = content.replace(should, 'addReportExprStr')
            needed.add('addReportExprStr')
    for should in ['shouldThrow', 'shouldNotThrow']:
        if should in content:
            content = content.replace(should, 'addExceptionExpr')
            needed.add('addExceptionExpr')
    content2 = content
    for should in ['shouldBeEqualToString', 'shouldBe']:
        if should in content:
            content = content.replace(should, 'addReportExprJson')
            # remove second argument in v2:
            content2 = re.sub(should + r'\((.*?)\);\n', replace_should, content2)
            needed.add('addReportExprJson')
    for n in needed:
        prefix.append(UTILS[n])
    # remove some more things
    content = re.sub(r'testPassed\([^\n]*\);', ';', content)
    content2 = re.sub(r'testPassed\([^\n]*\);', ';', content2)
    # Re-run to check if it executes and produces the expected result
    full_code = '\n'.join(prefix) + '\n' + content + '\nreturn RESULT;'
    full_code2 = '\n'.join(prefix) + '\n' + content + '\nreturn RESULT;'
    json_expected = json.dumps(expected)
    if len(full_code) > 10000:
        return 'code too long'
    if len(json_expected) > 10000:
        return 'json too long'

    write_file(TEMPFILE, 'function do_the_test() {' + full_code + '}' + SUFFIX2)
    output = subprocess.check_output([NODE, TEMPFILE], timeout=3, stderr=sys.stderr)
    assert b'+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+' in output
    output = output[output.find(b'+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+') + 97:]
    data = json.loads(output.decode())
    print(data)
    print(isEqual(data, expected))
    assert isEqual(data, expected)

    try:
        write_file(TEMPFILE, 'function do_the_test() {' + full_code2 + '}' + SUFFIX2)
        output = subprocess.check_output([NODE, TEMPFILE], timeout=3, stderr=sys.stderr)
        assert b'+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+' in output
        output = output[output.find(b'+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+') + 97:]
        data = json.loads(output.decode())
        print(data)
        print(isEqual(data, expected))
        assert isEqual(data, expected)
        full_code = full_code2
    except:
        print('(version 2 did not pass)')

    print(f'TEST {fname} SUCCESSFUL!')

    basename = os.path.join('working_tests', fname[5:-3])
    os.makedirs(os.path.dirname(basename), exist_ok=True)
    write_file(basename+'.js', license + full_code)
    write_file(basename+'.json', json_expected)
    write_file(basename+'.orig.js', content_orig)

    return True


if __name__ == '__main__':
    input_files = glob.glob('test/webkit/*.js')
    input_files += glob.glob('test/webkit/fast/*/*.js')
    # input_files = glob.glob('test/webkit/string-*.js')
    # input_files = ['test/webkit/string-replacement-outofmemory.js']
    # input_files = ['test/webkit/class-syntax-prototype.js']

    #input_files = [f.split(' ')[-1] for f in read_file('worklist.txt').split('\n') if f.strip() != '']
    #input_files = input_files[:1]

    # filter out some uninteresting files
    input_files = [f for f in input_files if '-crash' not in f]

    failed_list = []

    ok = 0
    fail = 0
    inv = 0
    for fname in input_files:
        print('+++', fname, ' ...')
        try:
            if prepare_test_file(fname):
                ok += 1
            else:
                inv += 1
                failed_list.append(f'INVALID {fname}')
        except:
            traceback.print_exc()
            fail += 1
            failed_list.append(f'CRASH   {fname}')
    write_file('errors.log', '\n'.join(failed_list) + '\n')
    print(f'OK:   {ok}')
    print(f'INV:  {inv}')
    print(f'FAIL: {fail}')
    # prepare_test_file('test/webkit/string-sort.js')
