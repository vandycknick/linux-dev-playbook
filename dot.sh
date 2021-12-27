#!/bin/sh

set -eu

echo "[i] Ask for sudo password"
sudo -v

. /etc/os-release

ansible-galaxy install -r requirements.yml

ansible-playbook main.yml
