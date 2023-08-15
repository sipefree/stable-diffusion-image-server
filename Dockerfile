FROM python:alpine
LABEL Maintainer="sipefree@gmail.com"

# Set environment variables
ENV PORT 8000
ENV WATCH_DELAY 15
ENV NCPUS 4
ENV CLEAN false

# Create directories for import content and output data
RUN mkdir /sdis-content && mkdir -p /data/www && mkdir -p /data/redis

# Define volumes
VOLUME /sdis-content
VOLUME /data

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies.
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt

# Install the package
RUN python3 -m pip install .

# Run the command to start the server with environment variables
CMD python3 -m sdis.server -p ${PORT} -w ${WATCH_DELAY} --ncpus ${NCPUS} --thumb-dir /data/www -d /sdis-content $(if ${CLEAN}; then echo '--clean'; fi)
