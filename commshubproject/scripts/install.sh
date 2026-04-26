#!/bin/bash
set -e

INSTALL_PATH="/Users/okgoogle13/Projects/commshubproject/commshubproject"
COMMSHUB_DIR="$HOME/.commshub"
LAUNCH_AGENTS="$HOME/Library/LaunchAgents"

echo "=== Comms Hub Installer ==="

# 1. Check macOS 14+
MACOS_MAJOR=$(sw_vers -productVersion | cut -d. -f1)
if [ "$MACOS_MAJOR" -lt 14 ]; then
  echo "ERROR: Requires macOS 14+. Found: $(sw_vers -productVersion)"
  exit 1
fi
echo "[OK] macOS $(sw_vers -productVersion)"

# 2. Check Python 3.10+
PYTHON_BIN=$(which python3.13 2>/dev/null || which python3.12 2>/dev/null || which python3.11 2>/dev/null || which python3.10 2>/dev/null || echo "")
if [ -z "$PYTHON_BIN" ]; then
  echo "ERROR: Python 3.10+ not found. Install via: brew install python@3.13"
  exit 1
fi
echo "[OK] $($PYTHON_BIN --version)"

# 3. Create virtualenv
cd "$INSTALL_PATH"
if [ ! -d "venv" ]; then
  "$PYTHON_BIN" -m venv venv
  echo "[OK] Virtualenv created at $INSTALL_PATH/venv"
else
  echo "[OK] Virtualenv already exists"
fi
source venv/bin/activate

# 4. Install requirements
pip install -r requirements.txt --quiet
echo "[OK] Dependencies installed"

# 5. Create ~/.commshub directory structure
mkdir -p "$COMMSHUB_DIR/logs"
echo "[OK] ~/.commshub structure created"

# 6. Create .env if missing
if [ ! -f "$COMMSHUB_DIR/.env" ]; then
  RANDOM_KEY=$(openssl rand -hex 16 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(16))")
  echo "GEMINI_API_KEY=" > "$COMMSHUB_DIR/.env"
  echo "DB_ENCRYPTION_KEY=$RANDOM_KEY" >> "$COMMSHUB_DIR/.env"
  echo "[OK] ~/.commshub/.env created — add your GEMINI_API_KEY"
else
  echo "[OK] ~/.commshub/.env already exists"
fi

# 7. Check Full Disk Access
echo "[CHECK] Verifying Full Disk Access for Messages..."
bash "$INSTALL_PATH/scripts/fda_check.sh"
if [ $? -ne 0 ]; then
  echo ""
  echo "ACTION REQUIRED: Grant Full Disk Access to Terminal"
  echo "  System Settings → Privacy & Security → Full Disk Access → add Terminal"
  echo "  Then re-run this installer: bash scripts/install.sh"
  exit 1
fi
echo "[OK] Full Disk Access confirmed"

# 8. Load env vars and inject into plists
source "$COMMSHUB_DIR/.env"
if [ -z "$GEMINI_API_KEY" ]; then
  echo "WARNING: GEMINI_API_KEY is not set in ~/.commshub/.env"
  echo "  Edit ~/.commshub/.env before first use, then re-run: bash scripts/install.sh"
fi

# 9. Install launchd plists with env var substitution
mkdir -p "$LAUNCH_AGENTS"
for AGENT in watcher digest; do
  SRC="$INSTALL_PATH/launchd/com.commshub.$AGENT.plist"
  DST="$LAUNCH_AGENTS/com.commshub.$AGENT.plist"
  # Substitute PLACEHOLDER_SET_IN_ENV with actual values
  sed "s/PLACEHOLDER_SET_IN_ENV/$GEMINI_API_KEY/g" "$SRC" > "$DST.tmp"
  mv "$DST.tmp" "$DST"
  launchctl unload "$DST" 2>/dev/null || true
  launchctl load "$DST"
  echo "[OK] Loaded $AGENT agent"
done

echo ""
echo "=== Comms Hub installed successfully! ==="
echo ""
echo "Next steps:"
echo "  1. Edit ~/.commshub/.env and add your GEMINI_API_KEY"
echo "  2. Re-run installer to reload agents with the key: bash scripts/install.sh"
echo "  3. Test: python -m src.cli watch"
echo "  4. Check status: python -m src.cli status"
echo "  5. Run digest: python -m src.cli digest"
echo ""
echo "Watcher: runs hourly"
echo "Digest:  fires at 09:00, 13:00, 18:00, 21:00 AEST"
