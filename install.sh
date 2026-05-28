#!/bin/sh
set -e

DEST="$HOME/.local/share/meowfetch"
BIN="$HOME/.local/bin"

if [ -d "$DEST/.git" ]; then
  git -C "$DEST" pull -q
else
  git clone -q https://github.com/CodeMage07/meowfetch "$DEST"
fi

mkdir -p "$BIN"
printf '#!/bin/sh\nexec python3 -c "import sys; sys.path.insert(0, '"'"'%s'"'"'); from meowfetch.__main__ import cli; cli()" "$@"\n' "$DEST" > "$BIN/meowfetch"
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
