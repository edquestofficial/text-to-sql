# Base image
FROM python:3.12

# Set the working directory
WORKDIR /app

# Clone the repository from GitHub
RUN apt-get update && apt-get install -y git
RUN git clone https://github.com/edquestofficial/text-to-sql.git .

# Change directory to the main directory
WORKDIR /app/text-to-sql

# Install Python and pip (already included in the base image)

# Install pipenv
RUN pip install --no-cache-dir pipenv

# Run pipenv shell
RUN pipenv shell

# Install project dependencies
RUN pipenv install

# Run the main.py file
CMD ["pipenv", "run", "python", "main.py"]