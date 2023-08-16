#!/usr/bin/env bash

LOCAL_WORKSPACE_FOLDER=$1

set -ex

docker volume create devvolume-sdis-content

TZ=$(readlink /etc/localtime | awk -F'/zoneinfo/' '{print $2}')

echo "TZ=$TZ" > ${LOCAL_WORKSPACE_FOLDER}/.devcontainer/devcontainer.env