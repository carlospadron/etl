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

# Install pipenv
RUN pip install --no-cache-dir pipenv

# Set the working directory
WORKDIR /app

# Copy the Pipfile and Pipfile.lock into the container
COPY Pipfile Pipfile.lock ./

# Install Python dependencies using pipenv
RUN pipenv install --deploy --ignore-pipfile

# Copy the bash script into the container
COPY sling.sh /usr/local/bin/sling.sh

# Make the script executable
RUN chmod +x /usr/local/bin/sling.sh

# Set the entrypoint to execute the bash script
ENTRYPOINT ["pipenv", "run", "sh", "/usr/local/bin/sling.sh"]