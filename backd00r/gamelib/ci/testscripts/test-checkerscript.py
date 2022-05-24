#!/usr/bin/env python3
import functools
import random
import sys
import time
import urllib.parse
import requests
import os
import traceback

from checker_utils import *


def make_badge(text: str, color: str, name='checkers'):
    r = requests.get(f'https://img.shields.io/badge/{urllib.parse.quote(name)}-{urllib.parse.quote(text)}-{urllib.parse.quote(color)}')
    assert r.status_code == 200
    os.makedirs(os.path.join(basedir, 'public'), exist_ok=True)
    with open(os.path.join(basedir, 'public', f'ci-{name}.svg'), 'wb') as f:
        f.write(r.content)
    open(os.path.join(basedir, '.nobadge'), 'w').close()


def check_basic_operations(checker, team, tick=1):
    checker.initialize_team(team)
    try:
        print(f'[...] Run check_integrity(team, {tick})')
        status, msg = run_checker(checker.check_integrity, team, tick)
        assert status == 'SUCCESS', f'Wrong status: {status} ("{msg}")'
        print(f'[...] Run store_flags(team, {tick})')
        status, msg = run_checker(checker.store_flags, team, tick)
        assert status == 'SUCCESS', f'Wrong status: {status} ("{msg}")'
        print(f'[...] Run retrieve_flags(team, {tick})')
        status, msg = run_checker(checker.retrieve_flags, team, tick)
        assert status == 'SUCCESS', f'Wrong status: {status} ("{msg}")'
    finally:
        checker.finalize_team(team)


def check_retrieve_all(checker, team, max_tick):
    for tick in range(1, max_tick + 1):
        checker.initialize_team(team)
        try:
            print(f'[...] Run retrieve_flags(team, {tick})')
            status, msg = run_checker(checker.retrieve_flags, team, tick)
            assert status == 'SUCCESS', f'Wrong status: {status} ("{msg}")'
        finally:
            checker.finalize_team(team)


def check_offline(checker, team, tick):
    checker.initialize_team(team)
    try:
        print(f'[...] Run check_integrity(team, {tick})')
        status, msg = run_checker(checker.check_integrity, team, tick)
        assert status == 'OFFLINE', f'Wrong status: {status} ("{msg}")'
        print(f'[...] Run store_flags(team, {tick})')
        status, msg = run_checker(checker.store_flags, team, tick)
        assert status == 'OFFLINE', f'Wrong status: {status} ("{msg}")'
    finally:
        checker.finalize_team(team)


def checker_test(name, hint=''):
    def wrapper(test):
        @functools.wraps(test)
        def run(*args):
            from gamelib import GameLogger
            GameLogger.reset()
            print(f'\n\n\n\n===== Test "{name}" =====')
            try:
                test(*args)
                print('[OK]  ' + name)
                result = True
            except:
                traceback.print_exc()
                print('[ERR] Test failed: ' + name)
                if hint:
                    print('      ' + hint)
                result = False
            sys.stderr.flush()
            sys.stdout.flush()
            time.sleep(0.01)
            return result

        run.__setattr__('testname', name)
        return run

    return wrapper


# TESTS
@checker_test('Sanity', 'Test basic instance sanity (valid configuration, valid flag ids etc.)')
def test_sanity(cls, instance, team):
    assert len(instance.name) > 1, "Please give your script a name!"
    assert instance.name != 'SampleService', "Please give your script a name!"
    for x in instance.flag_id_types:
        assert x == 'username' or x.startswith('hex') or x.startswith('alphanum') or x == 'email' or x.startswith('pattern:'), f'Invalid flag id: {x}'
        if x.startswith('pattern:'):
            parts = re.findall(r'\$\{(.*?)}', x[8:])
            for p in parts:
                assert p == 'username' or p.startswith('hex') or p.startswith('alphanum') or p == 'email', f'Invalid flag id in pattern: "{p}" in {x}'


@checker_test('Basic operations', 'Apply game server script with ticks 1, 2, 3.')
def test_basic_ops(cls, instance, team):
    check_basic_operations(instance, team)
    check_basic_operations(instance, team, 2)
    check_basic_operations(instance, team, 3)
    check_retrieve_all(instance, team, 3)


@checker_test('Store multiple times', 'Store flag for tick 2 (which had already been stored before)')
def test_multi_store(cls, instance, team):
    check_basic_operations(instance, team, 2)


@checker_test('Recreate instance', 'Recreates instance and retrieves flags again. Remember: global state is forbidden!')
def test_recreate(cls, instance, team):
    print('\n      Recreate instance (remember: global state is forbidden!)')
    instance = cls(instance.id)
    check_retrieve_all(instance, team, 3)


@checker_test('Negative ticks', 'Test negative ticks (which will later be used for test-runs with invalid flags')
def test_negative_ticks(cls, instance, team):
    print('\n      Test runs will use negative ticks, your script needs to deal with that...')
    check_basic_operations(instance, team, -1)
    check_basic_operations(instance, team, -2)


@checker_test('Offline test', 'Check against offline team. Remember: all your requests must have a timeout of gamelib.TIMEOUT set!')
def test_offline(cls, instance, team):
    import gamelib
    team_offline = gamelib.Team(team.id + 1, os.urandom(6).hex(), '10.213.214.215')  # lets hope no one actually uses this one
    print('\n      Check against offline team ...')
    t = time.time()
    check_offline(instance, team_offline, 1)
    t = time.time() - t
    if t > 2 * gamelib.TIMEOUT + 10:
        print(f'You took {t:.3f} seconds for a request to an offline team. That is too long.')
        raise Exception('Timeout')


@checker_test('Missing test', 'Retrieve flag from team that was never issued. Script should return FLAGMISSING.')
def test_missing(cls, instance, team):
    print('\n      Check for a flag that has never been issued ...')
    tick = -3
    instance.initialize_team(team)
    try:
        print(f'[...] Run retrieve_flags(team, {tick})')
        status, msg = run_checker(instance.retrieve_flags, team, tick)
        assert status == 'FLAGMISSING', f'Wrong status: {status} ("{msg}")'
    finally:
        instance.finalize_team(team)


@checker_test('Real-world test', 'Run gameserver script for more ticks, trying to find edge-cases')
def test_realworld(cls, instance, team):
    start = 4
    end = 20
    times = []
    print('\n      Test a few more ticks ...')
    for tick in range(start, end + 1):
        t = time.time()
        instance.initialize_team(team)
        try:
            print(f'      Simulate tick {tick} ...')
            print(f'[...] Run check_integrity(team, {tick})')
            status, msg = run_checker(instance.check_integrity, team, tick)
            assert status == 'SUCCESS', f'Wrong status: {status} ("{msg}")'
            print(f'[...] Run store_flags(team, {tick})')
            status, msg = run_checker(instance.store_flags, team, tick)
            assert status == 'SUCCESS', f'Wrong status: {status} ("{msg}")'
            print(f'[...] Run retrieve_flags(team, {tick - 1})')
            status, msg = run_checker(instance.retrieve_flags, team, tick - 1)
            assert status == 'SUCCESS', f'Wrong status: {status} ("{msg}")'
        finally:
            instance.finalize_team(team)
        times.append(time.time() - t)
        time.sleep(1)
    print(f'Average runtime: {sum(times) / len(times):6.3f} sec')
    print(f'Minimal runtime: {max(times):6.3f} sec')
    print(f'Maximal runtime: {min(times):6.3f} sec')


def run_unittests(cls, instance, team):
    TESTS = [
        test_sanity,
        test_basic_ops,
        test_recreate,
        test_multi_store,
        test_negative_ticks,
        test_offline,
        test_missing,
        test_realworld
    ]
    results = [test(cls, instance, team) for test in TESTS]
    failed = sum(1 for r in results if not r)

    print('\n\n\n==== Summary =====')
    for test, r in zip(TESTS, results):
        print('[OK]  ' if r else '[ERR] ', test.testname)
    print('\n')

    if failed > 0:
        print(f'[ERR] {failed} tests failed.')
        make_badge(f'{failed}/{len(TESTS)} failed', 'red')
        raise Exception()
    print('[OK]  ALL TESTS PASSED.')


def run_simple(cls, instance, team):
    start = 1
    end = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    times = []
    times_per_operation = {'check': 0, 'store': 0, 'retrieve': 0}
    print(f'      Testing {end} ticks ...')
    states_integrity = {}
    states_store = {}
    states_retrieve = {}
    for tick in range(start, end + 1):
        t = time.time()
        instance.initialize_team(team)
        try:
            print(f'      Simulate tick {tick} ...')
            print(f'[...] Run check_integrity(team, {tick})')
            status, msg = run_checker(instance.check_integrity, team, tick)
            states_integrity[status] = states_integrity.get(status, 0) + 1
            t2 = time.time()
            times_per_operation['check'] += t2 - t
            print(f'[...] Run store_flags(team, {tick})')
            status, msg = run_checker(instance.store_flags, team, tick)
            states_store[status] = states_store.get(status, 0) + 1
            t3 = time.time()
            times_per_operation['store'] += t3 - t2
            if tick > 1:
                print(f'[...] Run retrieve_flags(team, {tick - 1})')
                status, msg = run_checker(instance.retrieve_flags, team, tick - 1)
                states_retrieve[status] = states_retrieve.get(status, 0) + 1
            else:
                states_retrieve['SUCCESS'] = states_retrieve.get('SUCCESS', 0) + 1
            times_per_operation['retrieve'] += time.time() - t3
        finally:
            instance.finalize_team(team)
        times.append(time.time() - t)
        time.sleep(1)
    print(('[OK]  ' if states_integrity.get('SUCCESS', 0) == end else '[ERR] ') + 'Integrity checks: ' + ', '.join(f'{c}x{s}' for s, c in states_integrity.items()))
    print(('[OK]  ' if states_store.get('SUCCESS', 0) == end else '[ERR] ')     + 'Storing flags:    ' + ', '.join(f'{c}x{s}' for s, c in states_store.items()))
    print(('[OK]  ' if states_retrieve.get('SUCCESS', 0) == end else '[ERR] ')  + 'Retrieving flags: ' + ', '.join(f'{c}x{s}' for s, c in states_retrieve.items()))
    print(f'Average runtime: {sum(times) / len(times):6.3f} sec')
    print(f'Minimal runtime: {min(times):6.3f} sec')
    print(f'Maximal runtime: {max(times):6.3f} sec')
    print(f'Avg. time per step:  {times_per_operation["check"]/len(times):6.3f} sec check   |   {times_per_operation["store"]/len(times):6.3f} sec store   |   {times_per_operation["retrieve"]/len(times):6.3f} sec retrieve')


def main(target: str, method: str):
    # Check if any checker scripts are present
    if not os.path.exists(os.path.join(basedir, 'checkers', 'config')):
        print('No checkerscript found. Create a file "config" in folder "checkers", content: "your-script-file.py:YourClassName".')
        make_badge('not found', 'yellow')
        return
    cls = get_checker_class()
    instance = cls(random.randint(1, 10))
    print('[OK]  Checker class has been created.')

    # Target
    import gamelib
    team = gamelib.Team(random.randint(1, 1000), os.urandom(6).hex(), target)

    # Run tests
    if method == 'test':
        run_unittests(cls, instance, team)
    elif method == 'run':
        run_simple(cls, instance, team)
    else:
        raise Exception(f'Invalid method: {method}')


if __name__ == '__main__':
    """
    USAGE:
    ./test-checkerscript.py                       # unit-test checkers against docker container
    ./test-checkerscript.py <target>              # unit-test checkers against ip
    ./test-checkerscript.py <target> run [ticks]  # run checkers against ip and give summary
    """
    target = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    method = sys.argv[2] if len(sys.argv) > 2 else 'test'
    print(f'[...] Checking checkerscript against "{target}" ...')
    try:
        main(target, method)
    finally:
        shutil.rmtree(CHECKER_PACKAGES_PATH, ignore_errors=True)
