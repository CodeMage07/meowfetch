import json, os, platform, shutil, subprocess
from datetime import timedelta

_SYS      = platform.system()
_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

if _SYS == 'Windows':
    os.system('')

RST  = '\033[0m'
BOLD = '\033[1m'

def _load_json(name):
    with open(os.path.join(_DATA_DIR, name)) as f:
        return json.load(f)

_COLOURS = _load_json('colours.json')


def run(*cmd):
    flags = subprocess.CREATE_NO_WINDOW if _SYS == 'Windows' else 0
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3, creationflags=flags)
        return result.stdout.strip()
    except Exception:
        return ''

def has(cmd):
    return shutil.which(cmd) is not None

def cmd_lines(*args):
    out = run(*args)
    return out.splitlines() if out else []

def bar(pct, width=10):
    filled = round(width * pct / 100)
    return f'[{"█" * filled}{"░" * (width - filled)}]'

def fmt_secs(secs):
    td = timedelta(seconds=int(secs))
    h, rem = divmod(td.seconds, 3600)
    parts = []
    if td.days: parts.append(f'{td.days}d')
    if h:       parts.append(f'{h}h')
    parts.append(f'{rem // 60}m')
    return ' '.join(parts)

def color_strip():
    normal = ''.join(f'\033[4{i}m   ' for i in range(8)) + RST
    bright = ''.join(f'\033[10{i}m   ' for i in range(8)) + RST
    return [normal, bright]

_CACHE_FILE = os.path.expanduser('~/.cache/meowfetch/cache.json')

def load_cache():
    try:
        with open(_CACHE_FILE) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError, ValueError):
        return {}

def save_cache(data):
    os.makedirs(os.path.dirname(_CACHE_FILE), exist_ok=True)
    try:
        with open(_CACHE_FILE, 'w') as f:
            json.dump(data, f)
    except OSError:
        pass


def install():
    import sys
    project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    local_bin   = os.path.expanduser('~/.local/bin')
    os.makedirs(local_bin, exist_ok=True)

    if _SYS == 'Windows':
        dest = os.path.join(local_bin, 'meowfetch.bat')
        with open(dest, 'w') as f:
            f.write(
                f'@echo off\n'
                f'"{sys.executable}" -c "'
                f'import sys; sys.path.insert(0, r\'{project_dir}\'); '
                f'from meowfetch.__main__ import cli; cli()" %*\n'
            )
    else:
        dest = os.path.join(local_bin, 'meowfetch')
        with open(dest, 'w') as f:
            f.write(
                f'#!/bin/sh\n'
                f'exec python3 -c "'
                f'import sys; sys.path.insert(0, \'{project_dir}\'); '
                f'from meowfetch.__main__ import cli; cli()" "$@"\n'
            )
        os.chmod(dest, os.stat(dest).st_mode | 0o111)

    print(f'installed → {dest}')
    if _SYS != 'Windows' and local_bin not in os.environ.get('PATH', '').split(':'):
        shell = os.environ.get('SHELL', '')
        rc = '~/.zshrc' if 'zsh' in shell else '~/.bashrc'
        print(f'\nadd to PATH:\n  echo \'export PATH="$HOME/.local/bin:$PATH"\' >> {rc}')
