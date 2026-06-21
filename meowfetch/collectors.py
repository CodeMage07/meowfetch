import glob, os, platform, re, time
from concurrent.futures import ThreadPoolExecutor
from .utils import run, has, cmd_lines, bar, fmt_secs, _SYS, _load_json

_VENDOR_TAG = re.compile(r'^(AMD|ATI|NVIDIA|Intel)[/\s]', re.I)

_FILTERS = {
    'indent':      lambda l: l.startswith('  '),
    'skip_header': lambda l: not l.lower().startswith('name'),
}

def _load_pkg_table():
    raw = _load_json('pkg_table.json')
    result = {}
    for key, entries in raw.items():
        result[key] = [
            (label, binary, tuple(args), _FILTERS.get(filt) if filt else None)
            for label, binary, args, filt in entries
        ]
    return result

_PKG_TABLE = _load_pkg_table()


def get_user():
    return os.environ.get('USER') or os.environ.get('USERNAME') or 'user'

def get_hostname():
    return platform.node()

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
    return f'{_SYS} {platform.release()}'

def get_kernel():
    return platform.release()

def get_uptime():
    if _SYS == 'Linux':
        try:
            with open('/proc/uptime') as f:
                return fmt_secs(float(f.read().split()[0]))
        except OSError:
            pass
    if _SYS == 'Darwin':
        raw = run('sysctl', '-n', 'kern.boottime')
        m = re.search(r'sec\s*=\s*(\d+)', raw)
        if m:
            return fmt_secs(time.time() - int(m.group(1)))
        # fall back to parsing `uptime` if boottime is unavailable
        return run('uptime').split(',')[0].split('up')[-1].strip() or 'Unknown'
    return run('uptime', '-p').replace('up ', '') or 'Unknown'

def get_packages():
    counts = []

    def query(label, binary, args, filt):
        if not has(binary):
            return None
        lines = cmd_lines(*args)
        filtered = [l for l in lines if filt(l)] if filt else lines
        return f'{len(filtered)} ({label})' if filtered else None

    entries = []
    match _SYS:
        case 'Darwin':
            entries += _PKG_TABLE['Darwin']
        case _:
            portage = glob.glob('/var/db/pkg/*/*')
            if portage:
                counts.append(f'{len(portage)} (portage)')
            kiss_db = '/var/db/kiss/installed'
            if os.path.isdir(kiss_db):
                kiss_pkgs = [e for e in os.listdir(kiss_db) if os.path.isdir(f'{kiss_db}/{e}')]
                if kiss_pkgs:
                    counts.append(f'{len(kiss_pkgs)} (kiss)')
            entries += _PKG_TABLE['Linux']
    entries += _PKG_TABLE['_any']

    with ThreadPoolExecutor() as pool:
        counts += filter(None, pool.map(lambda e: query(*e), entries))

    return ', '.join(counts) or 'Unknown'

def get_shell():
    sh = os.environ.get('SHELL', '')
    if not sh:
        return 'Unknown'
    name = os.path.basename(sh)
    m    = re.search(r'\d[\d.]*', run(sh, '--version'))
    return f'{name} {m.group()}' if m else name

def get_terminal():
    return next(
        (os.environ[v] for v in ('TERM_PROGRAM', 'COLORTERM', 'TERM') if os.environ.get(v)),
        'Unknown',
    )

def get_cpu():
    name = None
    cores = threads = None
    freq_str = ''

    if _SYS == 'Linux':
        try:
            with open('/proc/cpuinfo') as f:
                content = f.read()
            threads = 0
            phys, pid = set(), '0'
            for line in content.splitlines():
                if line.startswith('processor'):
                    threads += 1
                elif line.startswith('model name') and name is None:
                    name = line.split(':', 1)[1].strip()
                elif line.startswith('physical id'):
                    pid = line.split(':', 1)[1].strip()
                elif line.startswith('core id'):
                    phys.add((pid, line.split(':', 1)[1].strip()))
            cores = len(phys) if phys else threads
            m = re.search(r'cpu MHz\s*:\s*([\d.]+)', content)
            if m:
                freq_str = f' @ {float(m.group(1))/1000:.1f}GHz'
        except OSError:
            pass
    elif _SYS == 'Darwin':
        name = run('sysctl', '-n', 'machdep.cpu.brand_string')
        try:
            cores   = int(run('sysctl', '-n', 'hw.physicalcpu'))
            threads = int(run('sysctl', '-n', 'hw.logicalcpu'))
        except (ValueError, TypeError):
            pass
        hz = run('sysctl', '-n', 'hw.cpufrequency')
        if hz.isdigit():
            freq_str = f' @ {int(hz)/1e9:.1f}GHz'

    name = name or platform.processor() or 'Unknown'
    name = re.sub(r'\(R\)|\(TM\)', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    ct = f' ({cores}C/{threads}T)' if cores and threads else ''
    return f'{name}{freq_str}{ct}'

def get_gpu():
    if has('nvidia-smi'):
        out = run('nvidia-smi', '--query-gpu=name', '--format=csv,noheader,nounits')
        if out:
            return out.splitlines()[0].strip()
    if _SYS == 'Darwin':
        for line in run('system_profiler', 'SPDisplaysDataType').splitlines():
            if 'Chipset Model' in line or 'Chip Model' in line:
                return line.split(':', 1)[1].strip()
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
            avail = info.get('MemAvailable') or info.get('MemFree', 0)
            used  = total - avail
            return f'{used/2**20:.1f}G / {total/2**20:.1f}G  {bar(used/total*100)}'
        except (OSError, KeyError, ValueError, ZeroDivisionError):
            pass
    if _SYS == 'Darwin':
        try:
            total = int(run('sysctl', '-n', 'hw.memsize'))
            vm = run('vm_stat')
            ps = re.search(r'page size of (\d+)', vm)
            page_size = int(ps.group(1)) if ps else 4096
            pages = {m.group(1).lower(): int(m.group(2))
                     for m in (re.match(r'Pages\s+(.+?):\s+(\d+)', l) for l in vm.splitlines()) if m}
            avail = (pages.get('free', 0) + pages.get('speculative', 0) + pages.get('inactive', 0)) * page_size
            used  = total - avail
            return f'{used/2**30:.1f}G / {total/2**30:.1f}G  {bar(used/total*100)}'
        except (OSError, AttributeError, ValueError, ZeroDivisionError):
            pass
    return 'Unknown'

def get_disk():
    import shutil as _shutil
    try:
        d = _shutil.disk_usage('/')
        return f'{d.used/2**30:.1f}G / {d.total/2**30:.1f}G  {bar(d.used/d.total*100)}'
    except (OSError, ZeroDivisionError):
        return 'Unknown'
