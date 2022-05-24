#!/usr/bin/env python3

import os
import shutil
import subprocess
import sys
from typing import List, Iterable

from checker_utils import get_checker_class, basedir, run_checker, CHECKER_PACKAGES_PATH


def retrieve_some_flags(target: str, cls_id: int, team_id: int, ticks: Iterable[int]):
    cls = get_checker_class()
    checker = cls(cls_id)
    print('[OK]  Checker class has been created.')
    import gamelib
    team = gamelib.Team(team_id, os.urandom(6).hex(), target)
    for tick in ticks:
        checker.initialize_team(team)
        try:
            print(f'[...] Run retrieve_flags(team, {tick})')
            status, msg = run_checker(checker.retrieve_flags, team, tick)
            assert status == 'SUCCESS', f'Wrong status: {status} ("{msg}")'
        finally:
            checker.finalize_team(team)
    return checker


def test_exploit(exploit_file: str, target: str, checker, flag_ids: List[List[str]]) -> bool:
    print(f'\n\n--- Testing {exploit_file} ---')
    try:
        cmd = ['python3', exploit_file, target] + [','.join(ids) for ids in flag_ids]
        output = subprocess.check_output(
            cmd, cwd=os.path.join(basedir, 'exploits'), stderr=subprocess.STDOUT,
            timeout=60, start_new_session=True
        )
    except subprocess.CalledProcessError as e:
        print(f'Process failed with code {e.returncode}')
        print(f'Output: ')
        print(e.stdout.decode('utf-8', errors='ignore'))
        return False
    flags = checker.search_flags(output.decode('utf-8', errors='ignore'))
    if len(flags) < 1:
        print('Exploit did not return any flags. Output:\n' + output.decode('utf-8', errors='ignore'))
        return False
    valid_flags = [flag for flag in flags if checker.check_flag(flag)[0] is not None]
    if len(valid_flags) < len(flags):
        print(f'[WARNING] Exploit returned {len(flags) - len(valid_flags)} invalid flags (out of {len(flags)})')
    if len(valid_flags) < 1:
        print('Exploit did not return any valid flags. Output:\n' + output.decode('utf-8', errors='ignore'))
        return False
    return True


def main():
    # Parse commandline
    target = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    cls_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    team_id = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    range_from = int(sys.argv[4]) if len(sys.argv) > 4 else 40
    range_to = int(sys.argv[5]) if len(sys.argv) > 5 else 50
    print(f'Checking exploits against "{target}" (cls {cls_id}, team #{team_id}) ...')

    # Checker script is required to store flags in the service
    if not os.path.exists(os.path.join(basedir, 'checkers', 'config')):
        print('No checkerscript found. Create a file "config" in folder "checkers", content: "your-script-file.py:YourClassName".')
        sys.exit(1)

    # Retrieve some flags
    retrieve_some_flags(target, cls_id, team_id, range(range_from, range_to))


if __name__ == '__main__':
    try:
        main()
    finally:
        shutil.rmtree(CHECKER_PACKAGES_PATH, ignore_errors=True)
