#!/bin/bash

CONTAINER_WORKSPACE_FOLDER=$1

# Iterate through the files in /workspace/.venv/bin
for file in /workspace/.venv/bin/*; do
    base_file_name=$(basename "$file")

    # Check if the file is a script that begins with '#!'
    if head -n 1 "$file" | grep -q "^#!" || [[ $base_file_name == activate* ]]; then
        # Use sed to replace occurrences of "/workspace/.venv" with the evaluated value of "${CONTAINER_WORKSPACE_FOLDER}/.venv"
        sed -i "s|/workspace/.venv|${CONTAINER_WORKSPACE_FOLDER//\//\\/}/.venv|g" "$file"
    fi
done

set -ex

rsync -a --info=progress2 --delete /workspace/frontend/node_modules/ ${CONTAINER_WORKSPACE_FOLDER}/frontend/node_modules/
rsync -a --info=progress2 --delete /workspace/.venv/ ${CONTAINER_WORKSPACE_FOLDER}/.venv/

rm -rf /etc/localtime && ln -s /usr/share/zoneinfo/${TZ} /etc/localtime