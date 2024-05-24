#!/usr/bin/env bash

set -euo pipefail

echo "[i] Ask for sudo password"
sudo -v

# shellcheck source=/dev/null
# . /etc/os-release

ansible-galaxy install -r requirements.yml

ansible-playbook main.yml
