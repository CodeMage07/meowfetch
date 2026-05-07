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

one-liner — no cloning needed:

```bash
mkdir -p ~/.local/bin && curl -o ~/.local/bin/meowfetch https://codeberg.org/anyasretro/meowfetch/raw/branch/main/meowfetch.py && chmod +x ~/.local/bin/meowfetch
```

once installed, just run:

```bash
meowfetch
```

if `~/.local/bin` isn't in your PATH yet, add this to your shell config and restart your terminal:

```bash
# zsh (macOS default, ~/.zshrc)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc

# bash (Linux default, ~/.bashrc)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

---
manual install

if you'd rather clone the repo:

```bash
git clone https://codeberg.org/anyasretro/meowfetch
cd meowfetch
python3 meowfetch.py --install
```

the `--install` flag will copy the script to `~/.local/bin/meowfetch`.
