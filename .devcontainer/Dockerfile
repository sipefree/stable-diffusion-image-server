# ---------------------------------------------------------------------------- #
#                     Stage One: Build RedisJSON with Rust                     #
# ---------------------------------------------------------------------------- #
FROM rust:1.71.1-slim-bookworm as rust_builder

# Install curl, libclang
RUN apt-get update && apt-get install -y curl libclang-dev

# Download and unpack the RedisJSON bundle
RUN curl -L "https://github.com/RedisJSON/RedisJSON/archive/refs/tags/v2.6.6.tar.gz" | tar xz && mv RedisJSON-2.6.6 RedisJSON

# Build the Rust project
WORKDIR /RedisJSON
RUN cargo build --release

# ---------------------------------------------------------------------------- #
#                             Stage Two: Main Image                            #
# ---------------------------------------------------------------------------- #

# Second stage: Main image
FROM mcr.microsoft.com/vscode/devcontainers/python:3.11-bookworm

# Set working directory
WORKDIR /workspace

# ---------------------------------------------------------------------------- #

# Copy the built RedisJSON product from the first stage.
COPY --from=rust_builder /RedisJSON/target/release/librejson.so /usr/lib/redis/modules/

# Install Redis etc
RUN apt-get update && \
    apt install -y redis-server \
                   redis-tools \
                   redis-redisearch \
                   redis-redisearch-doc


# Copy Redis configuration files.
COPY ./.devcontainer/redis.conf /etc/redis/redis.conf

# Set up Redis permissions.
RUN chown redis:redis /etc/redis/redis.conf &&\
    chmod 0400 /etc/redis/redis.conf

# ---------------------------------------------------------------------------- #

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Install Python dependencies using Poetry
# Note: It assumes pyproject.toml and poetry.lock are in the root of your project
COPY pyproject.toml poetry.lock ./
RUN --mount=type=cache,target=/root/.cache/pypoetry \
    poetry config virtualenvs.create true && \
    poetry config virtualenvs.in-project true && \
    poetry install --no-root

# ---------------------------------------------------------------------------- #

# Install node/npm
COPY .devcontainer/install-node.sh ./
RUN /bin/bash install-node.sh

# Install JavaScript dependencies
# Note: package.json and package-lock.json are in the frontend directory
RUN mkdir ./frontend
COPY frontend/package.json frontend/package-lock.json ./frontend/
RUN --mount=type=cache,target=/root/.npm \
    cd frontend && npm install

# ---------------------------------------------------------------------------- #

# Create directories for import content and output data
RUN mkdir /sdis-content && \
    mkdir -p /data/www && \
    mkdir -p /data/redis && \
    chown redis:redis /data/redis && \
    chmod 0755 /data/redis

# Define volumes
VOLUME /sdis-content
VOLUME /data

# Expose port
EXPOSE 7862
