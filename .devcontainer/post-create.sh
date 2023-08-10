#!/bin/bash

CONTAINER_WORKSPACE_FOLDER=$1

set -ex

rsync -a --info=progress2 --delete /workspace/frontend/node_modules/ ${CONTAINER_WORKSPACE_FOLDER}/frontend/node_modules/
rsync -a --info=progress2 --delete /workspace/.venv/ ${CONTAINER_WORKSPACE_FOLDER}/.venv/