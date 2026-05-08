#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from meowfetch.__main__ import cli
if __name__ == '__main__':
    cli()
