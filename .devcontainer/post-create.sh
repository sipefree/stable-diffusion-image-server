#!/bin/bash

set -ex

mv /workspace/frontend/node_modules ${containerWorkspaceFolder}/frontend/
mv /workspace/.venv ${containerWorkspaceFolder}/.venv