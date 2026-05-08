import os, platform, shutil, subprocess
from datetime import timedelta

_SYS = platform.system()

if _SYS == 'Windows':
    os.system('')

RST  = '\033[0m'
BOLD = '\033[1m'

_COLOURS = {
    'red':     '\033[31m',
    'green':   '\033[32m',
    'yellow':  '\033[33m',
    'blue':    '\033[34m',
    'magenta': '\033[35m',
    'cyan':    '\033[36m',
}


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

def install():
    import subprocess as sp, sys
    project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    result = sp.run([sys.executable, '-m', 'pip', 'install', '--user', project_dir], check=False)
    if result.returncode == 0:
        print('Installed successfully. Run: meowfetch')
        local_bin = os.path.expanduser('~/.local/bin')
        if _SYS != 'Windows' and local_bin not in os.environ.get('PATH', '').split(':'):
            shell = os.environ.get('SHELL', '')
            rc = '~/.zshrc' if 'zsh' in shell else '~/.bashrc'
            print(f'\nadd to PATH:\n  echo \'export PATH="$HOME/.local/bin:$PATH"\' >> {rc}')
    else:
        print('Installation failed. Try: pip install --user .')
