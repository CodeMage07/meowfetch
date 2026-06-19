#!/bin/sh
set -e

DEST="$HOME/.local/share/meowfetch"
BIN="$HOME/.local/bin"

# Require Python 3.10+ for match/case support
PYTHON=""
for candidate in python3.14 python3.13 python3.12 python3.11 python3.10; do
  if command -v "$candidate" >/dev/null 2>&1; then
    PYTHON="$candidate"
    break
  fi
done
if [ -z "$PYTHON" ]; then
  echo "error: Python 3.10 or newer is required but was not found" >&2
  exit 1
fi

if [ -d "$DEST/.git" ]; then
  git -C "$DEST" remote set-url origin https://github.com/CodeMage07/meowfetch
  git -C "$DEST" fetch -q origin
  git -C "$DEST" reset -q --hard origin/main
else
  git clone -q https://github.com/CodeMage07/meowfetch "$DEST"
fi

mkdir -p "$BIN"
printf '#!/bin/sh\nexec %s -c "import sys; sys.path.insert(0, '"'"'%s'"'"'); from meowfetch.__main__ import cli; cli()" "$@"\n' "$PYTHON" "$DEST" > "$BIN/meowfetch"
chmod +x "$BIN/meowfetch"
echo "installed → $BIN/meowfetch"

case ":$PATH:" in
  *":$BIN:"*) ;;
  *)
    RC="$HOME/.bashrc"
    [ "$(basename "$SHELL")" = "zsh" ] && RC="$HOME/.zshrc"
    printf '\nadd to PATH:\n  echo '"'"'export PATH="$HOME/.local/bin:$PATH"'"'"' >> %s\n' "$RC"
    ;;
esac
