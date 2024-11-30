# Use an official Scala runtime as a parent image
FROM sbtscala/scala-sbt:eclipse-temurin-11.0.17_8_1.8.2_3.2.1
# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Compile the Scala code
RUN sbt compile

# Run the Scala program
CMD ["sbt", "run"]