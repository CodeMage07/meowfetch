# meowfetch

Hi, this is an experimental python project I have been working on with an agentic coding agent as a part of a module in one of my classes; this project is not a serious one, nor should it be taken seriously.

Meowfetch is a fetch utility with a pawesome twist! When ran it will display one of several cats, along side system information.

![preview](Screenshot_20260507_153129.png)

---
what it shows

- OS, kernel, uptime
- CPU (model, clock speed, core/thread count)
- GPU
- RAM and disk usage, with a progress bar
- shell, terminal, installed packages

---
installation

## Linux / macOS

```bash
sh <(curl -fsSL https://raw.githubusercontent.com/CodeMage07/meowfetch/main/install.sh)
```

if `~/.local/bin` isn't in your PATH yet:

```bash
# bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# zsh (macOS)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
```

---
manual install

```bash
git clone https://github.com/CodeMage07/meowfetch
cd meowfetch
python3 meowfetch.py --install
```

---
colours

use `--color` / `-c` to set the accent colour:

```bash
meowfetch --color pink
meowfetch -c bright_cyan
```

available: `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`, `pink`, `bright_red`, `bright_green`, `bright_blue`, `bright_cyan`

default is `cyan`.

---
updating

re-run the install command and it will pull the latest changes automatically.
