FROM mcr.microsoft.com/vscode/devcontainers/base:alpine-3.18

# Install Python 3, pip, git, and jpeg-dev (for Pillow)
RUN apk add --no-cache python3 py3-pip git jpeg-dev libffi-dev

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Install NPM and Node.js
RUN apk add --no-cache nodejs npm

# Set working directory
WORKDIR /workspace

# Install Python dependencies using Poetry
# Note: It assumes pyproject.toml and poetry.lock are in the root of your project
COPY pyproject.toml poetry.lock ./
RUN --mount=type=cache,target=/root/.cache/pypoetry \
    poetry config virtualenvs.create false && \
    poetry install --no-root

# Install JavaScript dependencies
# Note: package.json and package-lock.json are in the frontend directory
RUN mkdir ./frontend
COPY frontend/package.json frontend/package-lock.json ./frontend/
RUN --mount=type=cache,target=/root/.npm \
    cd frontend && npm install

# Create directories for sdis content and thumbnails
RUN mkdir /sdis-content
RUN mkdir /thumbs

# Define volumes
VOLUME /sdis-content
VOLUME /thumbs

# Expose port
EXPOSE 7862
