# Stage 1: Build stage to install OpenJDK
FROM openjdk:11-jre-slim AS jdk

# Stage 2: Build stage to install Python and application dependencies
FROM python:3.12-slim

# Set environment variables for non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Copy OpenJDK from the first stage
COPY --from=jdk /usr/local/openjdk-11 /usr/local/openjdk-11

# Set JAVA_HOME environment variable
ENV JAVA_HOME=/usr/local/openjdk-11
ENV PATH="${JAVA_HOME}/bin:${PATH}"

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

# Copy the rest of the application code into the container
COPY . .

# Set the entrypoint to run the main.py script
ENTRYPOINT ["pipenv", "run", "python", "main.py"]