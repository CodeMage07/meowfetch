# meowfetch

Hi, this is an experimental project I have been working on with an agentic coding agent as a part of a module in one of my classes; this project is not a serious one, nor should it be taken seriously.

Meowfetch is a fetch utility with a pawesome twist! When ran it will display one of four cats, along side system information.

![preview](preview.png)

---
what it shows

- OS, kernel, uptime
- CPU (model, clock speed, core/thread count)
- GPU
- RAM and disk usage, with a progress bar
- shell, terminal, installed packages

---
requirements

- Python 3.10+

---
installation

clone the repo and run the installer:

```bash
git clone https://codeberg.org/anyasretro/meowfetch
cd meowfetch
python3 meowfetch.py --install   # use 'python' on Windows
```

the installer will copy the script to `~/.local/bin/meowfetch` and let you know if that directory needs to be added to your PATH.

once installed, just run:

```bash
meowfetch
```

if `~/.local/bin` isn't in your PATH yet:

```bash
# zsh (macOS default)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc

# bash (Linux default)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

on Windows, run this in PowerShell:

```powershell
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$HOME\.local\bin", "User")
```
