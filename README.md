# Stable Diffusion Image Server

Stable Diffusion Image Server is a Python library designed to serve directories of images produced by the Stable Diffusion ML image generation software. It's a fork of the Simple HTTP Image Server project ([shis](https://github.com/nikhilweee/shis)), and we're thankful to the original author for their work. The primary addition in this fork is the capability to extract PNG EXIF data embedded in the images which contain the image diffusion prompt and configuration information and display them in the HTML.

## Running with Docker

The recommended way to run the Stable Diffusion Image Server is via a Docker container. The Docker image is available at `ghcr.io/sipefree/stable-diffusion-image-server:latest`.

### Command Line

You can start the Docker container with the following command:

```bash
docker run -d --name stable_diffusion_shis -p 8000:8000 -v /path/to/your/content:/sdis-content -v /path/to/data:/data -e PORT=8000 -e WATCH_DELAY=15 -e NCPUS=4 -e CLEAN=false ghcr.io/sipefree/stable-diffusion-image-server:latest
```

Replace `/path/to/your/content` and `/path/to/data` with the actual paths to your directories on the host machine, where the latter is the location where SDIS will save its database and generated content. You can also adjust the PORT, WATCH_DELAY, NCPUS, and CLEAN environment variables as needed.

### Docker Compose

Alternatively, you can use Docker Compose to manage the Docker container. Create a `docker-compose.yml` file with the following content:

```yaml
version: '3'
services:
  stable_diffusion_shis:
    image: ghcr.io/sipefree/stable-diffusion-image-server:latest
    volumes:
      - /path/to/your/content:/sdis-content
      - /path/to/thumbnail-cache:/thumbs
    environment:
      - PORT=8000
      - WATCH_DELAY=15
      - NCPUS=4
      - CLEAN=false
    ports:
      - 8000:8000
```

Then run `docker-compose up` to start the server.

For more detailed instructions and options for running the server manually outside of a Docker container, please refer to the upstream SHIS [documentation](https://shis.readthedocs.io/en/stable/).

## License

The Stable Diffusion Image Server is licensed under the MIT License. See the [LICENSE](./LICENSE.md) file for more details.
