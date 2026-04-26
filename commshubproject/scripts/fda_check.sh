#!/bin/bash
# ### FILE: commshubproject/scripts/fda_check.sh

echo "Checking Full Disk Access for Terminal/Python..."
if ls ~/Library/Messages/chat.db > /dev/null 2>&1; then
    echo "Full Disk Access is GRANTED."
else
    echo "Full Disk Access is DENIED. Please grant it in System Settings -> Privacy & Security."
    exit 1
fi
