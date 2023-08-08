FROM mcr.microsoft.com/vscode/devcontainers/base:alpine-3.18

# Install Python 3 and pip
RUN apk add --no-cache python3 py3-pip git jpeg-dev

# Create directories for shis content and thumbnails
RUN mkdir /sdis-content
RUN mkdir /thumbs

# Define volumes
VOLUME /sdis-content
VOLUME /thumbs

# Install project python dependencies
RUN mkdir /tmp/pip-requirements

COPY requirements.txt /tmp/pip-requirements/

RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install --upgrade pip
    
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r /tmp/pip-requirements/requirements.txt

# Install NPM and JS dependencies
RUN apk add nodejs npm


# Expose port
EXPOSE 7862