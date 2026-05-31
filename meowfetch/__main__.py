#!/usr/bin/env python3
"""Meowfetch — a fetch script with a pawesome twist"""

import argparse, random, time
from concurrent.futures import ThreadPoolExecutor

from .utils import BOLD, RST, _COLOURS, color_strip, install, load_cache, save_cache, _load_json
from .collectors import (
    get_user, get_hostname,
    get_os, get_kernel, get_uptime,
    get_packages,
    get_shell, get_terminal,
    get_cpu, get_gpu,
    get_ram, get_disk,
)

CATS = _load_json('cats.json')


_CACHE_TTL = {
    'OS':       86400,   # 24h — static between reinstalls
    'Kernel':   86400,   # 24h — static between reboots
    'Shell':    86400,   # 24h — rarely changes
    'CPU':      86400,   # 24h — static hardware
    'GPU':      86400,   # 24h — static hardware
    'Packages': 300,     # 5min — slow to collect, changes infrequently
    'Disk (/)': 60,      # 1min — changes occasionally
    # Uptime, RAM, Terminal intentionally absent — always collected fresh
}


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

    now   = time.time()
    cache = load_cache()

    results  = {}
    to_fetch = {}
    for label, fn in collectors.items():
        ttl   = _CACHE_TTL.get(label, 0)
        entry = cache.get(label)
        if ttl > 0 and entry and now - entry['ts'] < ttl:
            results[label] = entry['val']
        else:
            to_fetch[label] = fn

    if to_fetch:
        with ThreadPoolExecutor() as pool:
            futures = {label: pool.submit(fn) for label, fn in to_fetch.items()}
        fresh = {label: f.result() for label, f in futures.items()}
        results.update(fresh)
        for label, val in fresh.items():
            if _CACHE_TTL.get(label, 0) > 0:
                cache[label] = {'val': val, 'ts': now}
        save_cache(cache)

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


def cli():
    parser = argparse.ArgumentParser(prog='meowfetch')
    parser.add_argument(
        '--color', '-c',
        choices=_COLOURS,
        default='cyan',
        metavar='NAME',
        help=f'colour scheme ({", ".join(_COLOURS)})',
    )
    parser.add_argument('--install', action='store_true', help='install to ~/.local/bin via pip')
    args = parser.parse_args()

    if args.install:
        install()
    else:
        main(args.color)


if __name__ == '__main__':
    cli()
