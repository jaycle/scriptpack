import argparse
from io import TextIOWrapper, StringIO
import re
import subprocess

VARS_HEADER = re.compile('===.*Config vars')
KEY_VAL_PATTERN = re.compile('^(?P<key>\w+):\s+(?P<val>.+)$')

def get_env_vars(f: TextIOWrapper):
    # Skip past header
    l = f.readline()
    while l and not VARS_HEADER.search(l):
        l = f.readline()

    vars = {}
    while l:
        l = f.readline()
        match = KEY_VAL_PATTERN.search(l)
        if (match):
            vars[match.group('key')] = match.group('val')

    return vars

def print_vars(keys, vars):
    for k in keys:
        print(f'{k}={vars[k]}')


def get_heroku_vars(app_name):
    output = subprocess.check_output(['heroku', 'releases:info', '-a', app_name]).decode('utf-8')
    sio = StringIO(output)
    return sio


def diff_envs() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("target")
    parser.add_argument("-f", "--file", help="Files instead of app names", action="store_true")
    args = parser.parse_args()

    if args.file:
        with open(args.source) as f:
            source_vars = get_env_vars(f)
        with open(args.target) as f:
            target_vars = get_env_vars(f)
    else:
        heroku_output = get_heroku_vars(args.source)
        source_vars = get_env_vars(heroku_output)
        heroku_output = get_heroku_vars(args.target)
        target_vars = get_env_vars(heroku_output)

    source_keys = set(source_vars.keys())
    target_keys = set(target_vars.keys())

    missing = source_keys - target_keys
    print_vars(sorted(missing), source_vars)
    

if __name__ == "__main__":
    diff_envs()
