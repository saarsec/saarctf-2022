import importlib
import os
import re
import shutil
import sys
import traceback
from types import ModuleType
from typing import Tuple, Optional
import requests

import timeout_decorator

basedir = os.path.abspath(os.getcwd())

CHECKER_PACKAGES_PATH = '/dev/shm/' + os.urandom(8).hex()
PACKAGE = os.urandom(8).hex()
FULL_PACKAGE_PATH = CHECKER_PACKAGES_PATH + '/' + PACKAGE
sys.path.append(CHECKER_PACKAGES_PATH)

ignore_patterns = [
    re.compile(r'^__pycache__$'),
    re.compile(r'\.pyc$'),
    re.compile(r'^\.idea$'),
    re.compile(r'^\.git'),
    re.compile(r'^\.mypy_cache$'),
    re.compile(r'^gamelib$')
]


def is_ignored(folder: str) -> bool:
    return any(p.match(folder) for p in ignore_patterns)


def create_package(folder):
    # Code is basically a mocked copy of the DB-Filesystem code from the gameserver.
    os.makedirs(FULL_PACKAGE_PATH, exist_ok=True)
    for root, subdirs, files in os.walk(folder, followlinks=True):
        # add directories
        subdirs[:] = [dir for dir in subdirs if not is_ignored(dir)]
        for dir in subdirs:
            path = dir if root == folder else root[len(folder) + 1:] + '/' + dir
            os.makedirs(os.path.join(FULL_PACKAGE_PATH, path), exist_ok=True)

        # add files
        for file in files:
            if is_ignored(file):
                continue
            fname = root + '/' + file
            path = file if root == folder else root[len(folder) + 1:] + '/' + file
            shutil.copy(fname, os.path.join(FULL_PACKAGE_PATH, path))

    # Find and link gamelib
    if os.path.exists(basedir + '/gamelib'):
        os.symlink(basedir + '/gamelib', CHECKER_PACKAGES_PATH + '/gamelib')
    elif os.path.exists(basedir + '/checkers/gamelib'):
        os.symlink(basedir + '/checkers/gamelib', CHECKER_PACKAGES_PATH + '/gamelib')
    elif os.path.exists(basedir + '/ci/service-scripts/gamelib'):
        os.symlink(basedir + '/ci/service-scripts/gamelib', CHECKER_PACKAGES_PATH + '/gamelib')
    else:
        raise Exception('gamelib not found!')

    print(f'[OK]  Created package {FULL_PACKAGE_PATH}')


def import_module_from_package(filename: str) -> ModuleType:
    modulename = '{}.{}'.format(PACKAGE, filename.replace('.py', '').replace('/', '.'))
    spec = importlib.util.spec_from_file_location(modulename, FULL_PACKAGE_PATH + '/' + filename)
    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise Exception('Loader is not present')
    try:
        spec.loader.exec_module(module)  # type: ignore
    except ImportError:
        print('=== IMPORT ERROR ===')
        print('Remember: ')
        print('1. Only use relative imports (with dot) for your own script files:   import .my_other_python_file')
        print('2. If you need additional libraries for your script (not in requirements-checker), report them to the orgas.')
        raise
    print('[OK]  PackageLoader imported {}'.format(modulename))
    return module


def get_checker_class():
    # Find checkerfile
    with open(os.path.join(basedir, 'checkers', 'config'), 'r') as f:
        checker_script_filename, checker_classname = f.read().strip().split(':')
    # Create package
    create_package(os.path.join(basedir, 'checkers'))
    # Import checkerscript
    module = import_module_from_package(checker_script_filename)
    return getattr(module, checker_classname)


@timeout_decorator.timeout(30)
def run_checker(func, team, tick) -> Tuple[str, Optional[str]]:
    import gamelib
    from pwnlib import exception
    try:
        func(team, tick)
        return 'SUCCESS', None

    except gamelib.FlagMissingException as e:
        traceback.print_exc()
        return 'FLAGMISSING', e.message
    except gamelib.MumbleException as e:
        traceback.print_exc()
        return 'MUMBLE', e.message
    except AssertionError as e:
        traceback.print_exc()
        if len(e.args) == 1 and type(e.args[0]) == str:
            return 'MUMBLE', e.args[0]
        return 'MUMBLE', repr(e.args)
    except requests.ConnectionError as e:
        traceback.print_exc()
        return 'OFFLINE', 'Connection timeout'
    except requests.exceptions.Timeout as e:
        traceback.print_exc()
        return 'OFFLINE', 'Connection timeout'
    except exception.PwnlibException as e:
        if 'Could not connect to' in e.args[0]:
            return 'OFFLINE', str(e.args[0])
        return 'CRASHED', None
    except gamelib.OfflineException as e:
        traceback.print_exc()
        return 'OFFLINE', e.message
    # except SoftTimeLimitExceeded:
    #	traceback.print_exc()
    #	return 'TIMEOUT', 'Timeout, service too slow'
    except MemoryError:
        traceback.print_exc()
        return 'CRASHED', None
    except:
        traceback.print_exc()
        return 'CRASHED', None
