#!/usr/bin/env python3
"""Meowfetch — a fetch script with a pawesome twist"""

import argparse, random
from concurrent.futures import ThreadPoolExecutor

from .utils import BOLD, RST, _COLOURS, color_strip, install
from .collectors import (
    get_user, get_hostname,
    get_os, get_kernel, get_uptime,
    get_packages,
    get_shell, get_terminal,
    get_cpu, get_gpu,
    get_ram, get_disk,
)

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
