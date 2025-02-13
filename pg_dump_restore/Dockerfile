# Use a lightweight base image
FROM ubuntu:latest

# Set environment variables for non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Install PostgreSQL client and other necessary packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the bash script into the container
COPY el_job.sh /usr/local/bin/el_job.sh
COPY table_definitions.sql .

# Make the script executable
RUN chmod +x /usr/local/bin/el_job.sh

# Set the entrypoint to execute the bash script
ENTRYPOINT ["/usr/local/bin/el_job.sh"]