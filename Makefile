.PHONY: install-poetry install-frontend build-frontend build-sdis clean sync-assets build

# Install Poetry if it's not available
install-poetry:
	@[ -z "$$(command -v poetry)" ] && curl -sSL https://install.python-poetry.org | python3 - || echo "Poetry already installed."

# Install frontend dependencies
install-frontend:
	cd frontend && npm install

# Sync assets from src to dist
sync-assets:
	rsync -av --progress frontend/src/js/ frontend/dist/js/ \
    && rsync -av --progress frontend/src/images/ frontend/dist/images/ \
    && rsync -av --progress frontend/src/fonts/ frontend/dist/fonts/ \
    && rsync -av --progress frontend/src/favicon.png frontend/dist/

# Build frontend assets with TailwindCSS
build-frontend:
	cd frontend && npm run tailwind-build

# Build the sdis package
build-sdis:
	poetry build

# Install the sdis package locally
install-sdis:
	poetry install

# The main build task that builds everything
build: install-poetry install-frontend sync-assets build-frontend build-sdis

# Clean build artifacts
clean:
	cd frontend && rm -rf dist node_modules
	rm -rf dist
