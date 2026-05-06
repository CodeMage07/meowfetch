# meowfetch

a neofetch-inspired system info tool for the terminal, but with a cat. because why not.

displays your system specs next to some ascii cat art, which gets randomly picked each time you run it. nothing groundbreaking, just a fun little script.

![screenshot placeholder]

---

## what it shows

- OS, kernel, uptime
- CPU (model, clock speed, core/thread count)
- GPU
- RAM and disk usage with a little progress bar
- shell, terminal, installed packages
- a colour palette strip at the bottom

---

## requirements

- Python 3.6+
- `psutil` — used for RAM, disk, CPU info. the script still works without it but the info will be less accurate.

---

## installation

clone the repo and install the dependency:

```bash
git clone https://codeberg.org/anyasretro/meowfetch
cd meowfetch
pip install psutil
```

then just run it:

```bash
python3 meowfetch.py
```

if you want to call it like a command without typing `python3` every time, you can make it executable and drop it somewhere in your PATH:

```bash
chmod +x meowfetch.py
sudo cp meowfetch.py /usr/local/bin/meowfetch
```

after that you can just type `meowfetch` anywhere.

---

## notes

- tested on Linux (Gentoo, Arch, Debian-based) and macOS. should work on Windows too but it's less tested there.
- GPU detection works out of the box for NVIDIA (via `nvidia-smi`) and AMD/Intel (via `lspci` on Linux, `system_profiler` on macOS, `wmic` on Windows).
- package count works with pacman, dpkg, rpm, flatpak, and brew. if you're on something else it'll just say Unknown.

---

## licence

do whatever you want with it, i don't care. MIT if you need something to put in a field.
