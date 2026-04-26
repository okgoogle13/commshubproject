#!/bin/bash
# ### FILE: commshubproject/scripts/install.sh

echo "Installing Comms Hub Dependencies..."
pip install -r requirements.txt

echo "Loading LaunchAgents..."
cp launchd/*.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.commshub.watcher.plist
launchctl load ~/Library/LaunchAgents/com.commshub.digest.plist

echo "Install complete."
