#!/usr/bin/env python3
"""catfetch — neofetch-style system info with randomised cat ASCII art"""

import os, platform, random, re, socket, subprocess
from datetime import timedelta

try:
    import psutil
    _PSUTIL = True
except ImportError:
    _PSUTIL = False

_SYS = platform.system()  # 'Linux', 'Darwin', 'Windows'

# Enable ANSI colour codes on Windows 10+
if _SYS == 'Windows':
    os.system('')

# ANSI colours
RST  = '\033[0m';  BOLD = '\033[1m'
CYN  = '\033[96m'; YLW  = '\033[93m'; WHT = '\033[97m'
MGT  = '\033[95m'; GRN  = '\033[92m'; RED = '\033[91m'

# ASCII cats 
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
]

# helpers
def run(*cmd):
    try:
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3,
            creationflags=subprocess.CREATE_NO_WINDOW if _SYS == 'Windows' else 0,
        )
        return r.stdout.strip()
    except Exception:
        return ''

def bar(pct, width=10):
    filled = round(width * pct / 100)
    color  = GRN if pct < 60 else (YLW if pct < 85 else RED)
    return f'{color}[{"█" * filled}{"░" * (width - filled)}]{RST}'

def color_palette():
    block = '   '
    row1 = ''.join(f'\033[4{i}m{block}' for i in range(8)) + RST
    row2 = ''.join(f'\033[10{i}m{block}' for i in range(8)) + RST
    return [row1, row2]

# info collectors
def get_user():
    return os.environ.get('USER') or os.environ.get('USERNAME') or 'user'

def get_hostname():
    return socket.gethostname()

def get_os():
    if _SYS == 'Linux':
        try:
            with open('/etc/os-release') as f:
                d = dict(l.strip().split('=', 1) for l in f if '=' in l)
            return d.get('PRETTY_NAME', 'Linux').strip('"\'')
        except Exception:
            return f'Linux {platform.release()}'
    if _SYS == 'Darwin':
        name = run('sw_vers', '-productName') or 'macOS'
        ver  = run('sw_vers', '-productVersion')
        return f'{name} {ver}'.strip()
    if _SYS == 'Windows':
        return f'Windows {platform.release()} (build {platform.version()})'
    return f'{_SYS} {platform.release()}'

def get_host_model():
    if _SYS == 'Linux':
        for path in (
            '/sys/devices/virtual/dmi/id/product_name',
            '/sys/devices/virtual/dmi/id/board_name',
        ):
            try:
                val = open(path).read().strip()
                PLACEHOLDERS = {
                    'None', 'Default string', 'To be filled by OEM',
                    'System Product Name', 'All Series', 'OEM',
                    'Not Applicable', 'Not Specified',
                }
                if val and val not in PLACEHOLDERS:
                    return val
            except Exception:
                pass
    elif _SYS == 'Darwin':
        return run('sysctl', '-n', 'hw.model') or None
    elif _SYS == 'Windows':
        out = run('wmic', 'computersystem', 'get', 'model', '/value')
        for line in out.splitlines():
            if '=' in line:
                v = line.split('=', 1)[1].strip()
                if v:
                    return v
    return None

def get_kernel():
    if _SYS == 'Windows':
        return platform.version()
    return platform.release()

def get_uptime():
    if _PSUTIL:
        import time
        secs = int(time.time() - psutil.boot_time())
        td   = timedelta(seconds=secs)
        h, r = divmod(td.seconds, 3600)
        m    = r // 60
        parts = []
        if td.days: parts.append(f'{td.days}d')
        if h:       parts.append(f'{h}h')
        parts.append(f'{m}m')
        return ' '.join(parts)
    out = run('uptime', '-p')
    return out.replace('up ', '') or 'Unknown'

def get_packages():
    if _SYS == 'Darwin':
        out = run('brew', 'list')
        if out:
            pkgs = [f'{len(out.splitlines())} (brew)']
            flat = run('flatpak', 'list', '--app', '--columns=name')
            if flat:
                pkgs.append(f'{len(flat.splitlines())} (flatpak)')
            return ', '.join(pkgs)
        return 'Unknown'
    if _SYS == 'Windows':
        out = run('winget', 'list')
        if out:
            pkgs = [l for l in out.splitlines()
                    if l.strip() and not l.startswith('-') and not l.lower().startswith('name')]
            if pkgs:
                return f'{len(pkgs)} (winget)'
        out = run('choco', 'list', '--local-only')
        if out:
            pkgs = [l for l in out.splitlines()
                    if l.strip() and 'packages installed' not in l]
            return f'{len(pkgs)} (choco)'
        return 'Unknown'
    # Linux
    out = run('pacman', '-Qq')
    if out:
        return f'{len(out.splitlines())} (pacman)'
    out = run('dpkg-query', '-f', '${Package}\n', '-W')
    if out:
        count = [f'{len(out.splitlines())} (dpkg)']
        flat  = run('flatpak', 'list', '--app', '--columns=name')
        if flat:
            count.append(f'{len(flat.splitlines())} (flatpak)')
        return ', '.join(count)
    out = run('rpm', '-qa', '--queryformat', '%{NAME}\n')
    if out:
        return f'{len(out.splitlines())} (rpm)'
    return 'Unknown'

def get_shell():
    if _SYS == 'Windows':
        # Prefer PowerShell if running inside it
        psver = run('powershell', '-NoProfile', '-Command', '$PSVersionTable.PSVersion.ToString()')
        if psver:
            return f'powershell {psver}'
        return os.path.basename(os.environ.get('COMSPEC', 'cmd'))
    sh = os.environ.get('SHELL', '')
    if not sh:
        return 'Unknown'
    name = os.path.basename(sh)
    ver  = run(sh, '--version')
    if ver:
        m = re.search(r'[\d.]+', ver)
        if m:
            return f'{name} {m.group()}'
    return name

def get_terminal():
    if _SYS == 'Windows':
        if os.environ.get('WT_SESSION'):
            return 'Windows Terminal'
        if os.environ.get('ConEmuBuild'):
            return 'ConEmu'
        return 'cmd'
    for v in ('TERM_PROGRAM', 'COLORTERM', 'TERM'):
        val = os.environ.get(v)
        if val:
            return val
    return 'Unknown'

def get_cpu():
    name = None
    if _SYS == 'Linux':
        try:
            with open('/proc/cpuinfo') as f:
                for line in f:
                    if line.startswith('model name'):
                        name = line.split(':', 1)[1].strip()
                        break
        except Exception:
            pass
    elif _SYS == 'Darwin':
        name = run('sysctl', '-n', 'machdep.cpu.brand_string')
    elif _SYS == 'Windows':
        out = run('wmic', 'cpu', 'get', 'name', '/value')
        for line in out.splitlines():
            if line.startswith('Name='):
                name = line.split('=', 1)[1].strip()
                break

    if not name:
        name = platform.processor() or 'Unknown'

    name = re.sub(r'\(R\)|\(TM\)', '', name)
    name = re.sub(r'\s+', ' ', name).strip()

    if _PSUTIL:
        c    = psutil.cpu_count(logical=False)
        t    = psutil.cpu_count(logical=True)
        freq = psutil.cpu_freq()
        f_s  = f' @ {freq.current/1000:.1f}GHz' if freq else ''
        return f'{name}{f_s} ({c}C/{t}T)'
    return name

def get_gpu():
    # NVIDIA — works on Linux, Windows, and macOS
    out = run('nvidia-smi', '--query-gpu=name', '--format=csv,noheader,nounits')
    if out:
        return out.splitlines()[0].strip()
    if _SYS == 'Darwin':
        out = run('system_profiler', 'SPDisplaysDataType')
        for line in out.splitlines():
            if 'Chipset Model' in line or 'Chip Model' in line:
                return line.split(':', 1)[1].strip()
    elif _SYS == 'Windows':
        out = run('wmic', 'path', 'win32_VideoController', 'get', 'name', '/value')
        for line in out.splitlines():
            if line.startswith('Name=') and '=' in line:
                v = line.split('=', 1)[1].strip()
                if v:
                    return v
    else:  # Linux
        out = run('lspci')
        for line in out.splitlines():
            if any(k in line for k in ('VGA', '3D controller', 'Display controller')):
                # lspci puts the human-readable product name in the last [brackets]
                # e.g. "Navi 48 [Radeon RX 9070 XT]" or "GA102 [GeForce RTX 3080]"
                # vendor tags like [AMD/ATI] appear earlier and match this pattern
                vendor_tag = re.compile(r'^(AMD|ATI|NVIDIA|Intel)[/\s]', re.I)
                brackets = re.findall(r'\[([^\]]+)\]', line)
                product = next(
                    (b for b in reversed(brackets) if not vendor_tag.match(b)),
                    None,
                )
                if product:
                    return product
                # fallback: strip brackets and return the description
                gpu = line.split(':', 2)[-1].strip()
                return re.sub(r'\s*\[.*?\]', '', gpu).strip()
    return 'Unknown'

def get_ram():
    if _PSUTIL:
        v    = psutil.virtual_memory()
        used = v.used  / 2**30
        tot  = v.total / 2**30
        return f'{used:.1f}G / {tot:.1f}G  {bar(v.percent)}'
    if _SYS == 'Linux':
        try:
            info = {}
            with open('/proc/meminfo') as f:
                for line in f:
                    k, v = line.split(':', 1)
                    info[k.strip()] = int(v.strip().split()[0])
            total = info['MemTotal']
            avail = info.get('MemAvailable', info.get('MemFree', 0))
            used  = total - avail
            pct   = used / total * 100
            return f'{used/2**20:.1f}G / {total/2**20:.1f}G  {bar(pct)}'
        except Exception:
            pass
    return 'Unknown'

def get_disk():
    if _PSUTIL:
        d = psutil.disk_usage('/')
        return f'{d.used/2**30:.1f}G / {d.total/2**30:.1f}G  {bar(d.percent)}'
    root = 'C:\\' if _SYS == 'Windows' else '/'
    out  = run('df', '-h', root)
    lines = out.splitlines()
    if len(lines) >= 2:
        p = lines[1].split()
        return f'{p[2]} / {p[1]} ({p[4]})'
    return 'Unknown'

# main
def main():
    user = get_user()
    host = get_hostname()
    cat  = random.choice(CATS)

    rows = []
    rows.append(f'{BOLD}{MGT}{user}{WHT}@{MGT}{host}{RST}')
    rows.append(f'{WHT}{"─" * (len(user) + len(host) + 1)}{RST}')

    def add(label, val):
        if val:
            rows.append(f'{BOLD}{YLW}{label}{RST}: {WHT}{val}{RST}')

    model = get_host_model()
    if model:
        add('Host',     model)
    add('OS',       get_os())
    add('Kernel',   get_kernel())
    add('Uptime',   get_uptime())
    add('Packages', get_packages())
    add('Shell',    get_shell())
    add('Terminal', get_terminal())
    add('CPU',      get_cpu())
    add('GPU',      get_gpu())
    add('RAM',      get_ram())
    add('Disk (/)', get_disk())

    rows.append('')
    rows.extend(color_palette())

    cat_w    = max(len(l) for l in cat)
    cat_rows = [f'{CYN}{l.ljust(cat_w)}{RST}' for l in cat]

    while len(cat_rows) < len(rows):
        cat_rows.append(' ' * cat_w)
    while len(rows) < len(cat_rows):
        rows.append('')

    print()
    for cat_line, info_line in zip(cat_rows, rows):
        print(f'  {cat_line}    {info_line}')
    print()

if __name__ == '__main__':
    main()
