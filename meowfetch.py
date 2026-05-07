#!/usr/bin/env python3
"""Meowfetch — a fetch script with a pawesome twist"""

import argparse, glob, os, platform, random, re, shutil, socket, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

try:
    import psutil
    _PSUTIL = True
except ImportError:
    _PSUTIL = False

_SYS = platform.system()

if _SYS == 'Windows':
    os.system('')

RST  = '\033[0m'
BOLD = '\033[1m'

_WIN_FLAGS  = subprocess.CREATE_NO_WINDOW if _SYS == 'Windows' else 0
_VENDOR_TAG = re.compile(r'^(AMD|ATI|NVIDIA|Intel)[/\s]', re.I)

CATS = [
    [
        r"   /\_____/\   ",
        r"  /  o   o  \  ",
        r" ( ==  ^  == ) ",
        r"  )  ~~~~~  (  ",
        r" (           ) ",
        r"( (  )   (  ) )",
        r" (__(__)_(__) )",
    ],
    [
        r"   /\_____/\   ",
        r"  /  -   -  \  ",
        r" ( ==  ^  == ) ",
        r"  )  ~~~~~  (  ",
        r" (  z Z z   ) ",
        r"( (  )   (  ) )",
        r" (__(__)_(__) )",
    ],
    [
        r"   /\_____/\   ",
        r"  /  o   o  \  ",
        r" ( ==  ^  == ) ",
        r"  )  ~~~u~  (  ",
        r" (           ) ",
        r"( (  )   (  ) )",
        r" (__(__)_(__) )",
    ],
    [
        r"   /\_____/\   ",
        r"  /  -   -  \  ",
        r" ( ==  ^  == ) ",
        r"  )  ~~~~~  (  ",
        r" (~~~~~~~~~~~) ",
        r"( u  z z z  u )",
        r" ~~~~~~~~~~~~~ ",
    ],
    [
        r"   /\_____/\   ",
        r"  /  o   o  \  ",
        r" ( ==  ^  == ) ",
        r"  \  ~~~~~  /  ",
        r"|_____________|",
        r"|             |",
        r"|_____________|",
    ],
]

# helpers

def run(*cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3, creationflags=_WIN_FLAGS)
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

_COLOURS = {
    'red':     '\033[31m',
    'green':   '\033[32m',
    'yellow':  '\033[33m',
    'blue':    '\033[34m',
    'magenta': '\033[35m',
    'cyan':    '\033[36m',
}

def color_strip():
    normal = ''.join(f'\033[4{i}m   ' for i in range(8)) + RST
    bright = ''.join(f'\033[10{i}m   ' for i in range(8)) + RST
    return [normal, bright]

# info collectors

def get_user():
    return os.environ.get('USER') or os.environ.get('USERNAME') or 'user'

def get_hostname():
    return socket.gethostname()

def get_os():
    if _SYS == 'Linux':
        try:
            with open('/etc/os-release') as f:
                data = dict(line.strip().split('=', 1) for line in f if '=' in line)
            return data.get('PRETTY_NAME', 'Linux').strip('"\'')
        except OSError:
            return f'Linux {platform.release()}'
    if _SYS == 'Darwin':
        name = run('sw_vers', '-productName') or 'macOS'
        ver  = run('sw_vers', '-productVersion')
        return f'{name} {ver}'.strip()
    if _SYS == 'Windows':
        return f'Windows {platform.release()} (build {platform.version()})'
    return f'{_SYS} {platform.release()}'

def get_kernel():
    return platform.version() if _SYS == 'Windows' else platform.release()

def get_uptime():
    if _PSUTIL:
        secs             = int(time.time() - psutil.boot_time())
        td               = timedelta(seconds=secs)
        hours, remainder = divmod(td.seconds, 3600)
        minutes          = remainder // 60
        parts = []
        if td.days: parts.append(f'{td.days}d')
        if hours:   parts.append(f'{hours}h')
        parts.append(f'{minutes}m')
        return ' '.join(parts)
    return run('uptime', '-p').replace('up ', '') or 'Unknown'

# (label, binary, args, line-filter or None)  — requires Python 3.10+ for match/case
_PKG_TABLE = {
    'Darwin': [
        ('brew',     'brew', ('brew', 'list'),      None),
        ('macports', 'port', ('port', 'installed'), lambda l: l.startswith('  ')),
    ],
    'Windows': [
        ('winget', 'winget', ('winget', 'list'),
            lambda l: l.strip() and not l.startswith('-') and not l.lower().startswith('name')),
        ('choco',  'choco',  ('choco', 'list', '--local-only'),
            lambda l: l.strip() and 'packages installed' not in l),
        ('scoop',  'scoop',  ('scoop', 'list'),
            lambda l: l.strip() and not l.startswith('---') and not l.lower().startswith('name')),
    ],
    'Linux': [
        ('pacman',   'pacman',     ('pacman', '-Qq'),                            None),
        ('dpkg',     'dpkg-query', ('dpkg-query', '-f', '${Package}\n', '-W'),  None),
        ('rpm',      'rpm',        ('rpm', '-qa', '--queryformat', '%{NAME}\n'), None),
        ('xbps',     'xbps-query', ('xbps-query', '-l'),                         None),
        ('apk',      'apk',        ('apk', 'list', '--installed'),               None),
        ('eopkg',    'eopkg',      ('eopkg', 'list-installed', '-q'),            None),
        ('guix',     'guix',       ('guix', 'package', '--list-installed'),      None),
        ('pkg_info', 'pkg_info',   ('pkg_info',),                                None),
        ('pkg',      'pkg',        ('pkg', 'query', '%n'),                       None),
        ('brew',     'brew',       ('brew', 'list'),                             None),
    ],
    '_any': [
        ('nix',     'nix-env',  ('nix-env', '-q'),                               None),
        ('snap',    'snap',     ('snap', 'list'),    lambda l: not l.lower().startswith('name')),
        ('flatpak', 'flatpak',  ('flatpak', 'list', '--app', '--columns=name'),  None),
    ],
}

def get_packages():
    counts = []

    def add(label, lines):
        if lines:
            counts.append(f'{len(lines)} ({label})')

    def process(entries):
        for label, binary, args, filt in entries:
            if has(binary):
                lines = cmd_lines(*args)
                add(label, [l for l in lines if filt(l)] if filt else lines)

    match _SYS:
        case 'Darwin':
            process(_PKG_TABLE['Darwin'])
        case 'Windows':
            process(_PKG_TABLE['Windows'])
        case _:  # Linux / BSD — portage and kiss are path-based, not command-based
            portage = glob.glob('/var/db/pkg/*/*')
            if portage:
                add('portage', portage)
            kiss_db = '/var/db/kiss/installed'
            if os.path.isdir(kiss_db):
                add('kiss', [e for e in os.listdir(kiss_db) if os.path.isdir(f'{kiss_db}/{e}')])
            process(_PKG_TABLE['Linux'])

    process(_PKG_TABLE['_any'])
    return ', '.join(counts) or 'Unknown'

def get_shell():
    if _SYS == 'Windows':
        psver = run('powershell', '-NoProfile', '-Command', '$PSVersionTable.PSVersion.ToString()')
        if psver:
            return f'powershell {psver}'
        return os.path.basename(os.environ.get('COMSPEC', 'cmd'))
    sh = os.environ.get('SHELL', '')
    if not sh:
        return 'Unknown'
    name  = os.path.basename(sh)
    match = re.search(r'[\d.]+', run(sh, '--version'))
    return f'{name} {match.group()}' if match else name

def get_terminal():
    if _SYS == 'Windows':
        if os.environ.get('WT_SESSION'):
            return 'Windows Terminal'
        if os.environ.get('ConEmuBuild'):
            return 'ConEmu'
        return 'cmd'
    return next(
        (os.environ[v] for v in ('TERM_PROGRAM', 'COLORTERM', 'TERM') if os.environ.get(v)),
        'Unknown',
    )

def get_cpu():
    name = None
    if _SYS == 'Linux':
        try:
            with open('/proc/cpuinfo') as f:
                for line in f:
                    if line.startswith('model name'):
                        name = line.split(':', 1)[1].strip()
                        break
        except OSError:
            pass
    elif _SYS == 'Darwin':
        name = run('sysctl', '-n', 'machdep.cpu.brand_string')
    elif _SYS == 'Windows':
        for line in run('wmic', 'cpu', 'get', 'name', '/value').splitlines():
            if line.startswith('Name='):
                name = line.split('=', 1)[1].strip()
                break

    name = name or platform.processor() or 'Unknown'
    name = re.sub(r'\(R\)|\(TM\)', '', name)
    name = re.sub(r'\s+', ' ', name).strip()

    if _PSUTIL:
        cores    = psutil.cpu_count(logical=False)
        threads  = psutil.cpu_count(logical=True)
        freq     = psutil.cpu_freq()
        freq_str = f' @ {freq.current/1000:.1f}GHz' if freq else ''
        return f'{name}{freq_str} ({cores}C/{threads}T)'
    return name

def get_gpu():
    out = run('nvidia-smi', '--query-gpu=name', '--format=csv,noheader,nounits')
    if out:
        return out.splitlines()[0].strip()
    if _SYS == 'Darwin':
        for line in run('system_profiler', 'SPDisplaysDataType').splitlines():
            if 'Chipset Model' in line or 'Chip Model' in line:
                return line.split(':', 1)[1].strip()
    elif _SYS == 'Windows':
        for line in run('wmic', 'path', 'win32_VideoController', 'get', 'name', '/value').splitlines():
            if line.startswith('Name='):
                val = line.split('=', 1)[1].strip()
                if val:
                    return val
    else:
        for line in run('lspci').splitlines():
            if any(k in line for k in ('VGA', '3D controller', 'Display controller')):
                brackets = re.findall(r'\[([^\]]+)\]', line)
                product  = next((b for b in reversed(brackets) if not _VENDOR_TAG.match(b)), None)
                if product:
                    return product
                return re.sub(r'\s*\[.*?\]', '', line.split(':', 2)[-1]).strip()
    return 'Unknown'

def get_ram():
    if _PSUTIL:
        mem = psutil.virtual_memory()
        return f'{mem.used/2**30:.1f}G / {mem.total/2**30:.1f}G  {bar(mem.percent)}'
    if _SYS == 'Linux':
        try:
            info = {}
            with open('/proc/meminfo') as f:
                for line in f:
                    if ':' not in line:
                        continue
                    key, val = line.split(':', 1)
                    info[key.strip()] = int(val.strip().split()[0])
            total = info['MemTotal']
            used  = total - info.get('MemAvailable', info.get('MemFree', 0))
            return f'{used/2**20:.1f}G / {total/2**20:.1f}G  {bar(used/total*100)}'
        except (OSError, KeyError):
            pass
    return 'Unknown'

def get_disk():
    if _PSUTIL:
        disk = psutil.disk_usage('/')
        return f'{disk.used/2**30:.1f}G / {disk.total/2**30:.1f}G  {bar(disk.percent)}'
    root  = 'C:\\' if _SYS == 'Windows' else '/'
    lines = run('df', '-h', root).splitlines()
    if len(lines) >= 2:
        parts = lines[1].split()
        return f'{parts[2]} / {parts[1]} ({parts[4]})'
    return 'Unknown'

# install

def install():
    dest = os.path.expanduser('~/.local/bin/meowfetch')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(os.path.realpath(__file__), dest)
    os.chmod(dest, os.stat(dest).st_mode | 0o111)
    print(f'installed → {dest}')
    if not _PSUTIL:
        ans = input('install psutil for richer CPU/RAM/disk info? [Y/n] ').strip().lower()
        if ans in ('', 'y', 'yes'):
            subprocess.run([sys.executable, '-m', 'pip', 'install', '--user', 'psutil'])
    local_bin = os.path.expanduser('~/.local/bin')
    if local_bin not in os.environ.get('PATH', '').split(':'):
        print(f'\nadd {local_bin} to your PATH:')
        print(f'  echo \'export PATH="$HOME/.local/bin:$PATH"\' >> ~/.bashrc')

# main

def main(color='cyan'):
    user   = get_user()
    host   = get_hostname()
    cat    = random.choice(CATS)
    accent = _COLOURS[color]

    collectors = {
        'OS':       get_os,
        'Kernel':   get_kernel,
        'Uptime':   get_uptime,
        'Packages': get_packages,
        'Shell':    get_shell,
        'Terminal': get_terminal,
        'CPU':      get_cpu,
        'GPU':      get_gpu,
        'RAM':      get_ram,
        'Disk (/)': get_disk,
    }

    with ThreadPoolExecutor() as pool:
        futures = {label: pool.submit(fn) for label, fn in collectors.items()}
    results = {label: future.result() for label, future in futures.items()}

    rows = [
        f'{BOLD}{accent}{user}{RST}@{BOLD}{accent}{host}{RST}',
        f'{accent}{"─" * (len(user) + len(host) + 1)}{RST}',
    ]
    for label, val in results.items():
        if val:
            rows.append(f'{BOLD}{accent}{label}{RST}: {val}')
    rows += [''] + color_strip()

    cat_w    = max(len(line) for line in cat)
    cat_rows = [f'{BOLD}{accent}{line.ljust(cat_w)}{RST}' for line in cat]

    n = max(len(cat_rows), len(rows))
    cat_rows += [' ' * cat_w] * (n - len(cat_rows))
    rows     += [''] * (n - len(rows))

    print()
    for cat_line, info_line in zip(cat_rows, rows):
        print(f'  {cat_line}    {info_line}')
    print()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='meowfetch')
    parser.add_argument(
        '--color', '-c',
        choices=_COLOURS,
        default='cyan',
        metavar='NAME',
        help=f'colour scheme ({", ".join(_COLOURS)})',
    )
    parser.add_argument('--install', action='store_true', help='install to ~/.local/bin')
    args = parser.parse_args()

    if args.install:
        install()
    else:
        main(args.color)
