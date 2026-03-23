# Use a lightweight Python base image
FROM python:3.12-slim

# Set environment variables for non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set the working directory
WORKDIR /app

# Copy the pyproject.toml and lockfile into the container
COPY pyproject.toml uv.lock ./

# Install Python dependencies using uv
RUN uv sync --frozen --no-dev

# Copy the bash script into the container
COPY sling.sh /usr/local/bin/sling.sh

# Make the script executable
RUN chmod +x /usr/local/bin/sling.sh

# Set the entrypoint to execute the bash script
ENTRYPOINT ["uv", "run", "sh", "/usr/local/bin/sling.sh"]