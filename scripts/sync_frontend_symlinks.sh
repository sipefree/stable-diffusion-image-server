#!/bin/sh

poetry run scripts/sync_symlinks.py \
    frontend/src/fonts:frontend/dist/fonts \
    frontend/src/images:frontend/dist/images \
    frontend/src/js:frontend/dist/js \
    frontend/src/css-legacy:frontend/dist/css-legacy \
    frontend/src:frontend/dist \
    --watch