#!/bin/bash

# Set variables
ANSIBLE_PLAYBOOK_PATH="/root/patching/playbooks/download-ESXi-patches.yaml"

# Check if ansible-playbook command is available
if ! command -v ansible-playbook &> /dev/null; then
    echo "Error: ansible-playbook is not installed or not in PATH."
    exit 1
fi

# Execute the playbook
echo "Executing Ansible playbook: $ANSIBLE_PLAYBOOK_PATH"
ansible-playbook "$ANSIBLE_PLAYBOOK_PATH"

# Check if the playbook executed successfully
if [ $? -eq 0 ]; then
    echo "Playbook executed successfully."
else
    echo "Error: Playbook execution failed."
    exit 2
fi
