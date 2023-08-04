FROM python:alpine
LABEL Maintainer="sipefree@gmail.com"

# Set environment variables
ENV PORT 8000
ENV WATCH_DELAY 15
ENV NCPUS 4
ENV CLEAN false

# Create directories for shis content and thumbnails
RUN mkdir /sdis-content
RUN mkdir /thumbs

# Define volumes
VOLUME /sdis-content
VOLUME /thumbs

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the package
RUN python3 -m pip install .

# Run the command to start the server with environment variables
CMD python3 -m sdis.server -p ${PORT} -w ${WATCH_DELAY} --ncpus ${NCPUS} --thumb-dir /thumbs -d /sdis-content $(if ${CLEAN}; then echo '--clean'; fi)
