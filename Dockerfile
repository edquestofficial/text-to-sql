ARG GITHUB_TOKEN

# Base image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the code from your local directory
COPY . .
RUN echo "Copying code from local directory..."

# Clone the repository from GitHub
# RUN apt-get update && apt-get install -y git
# RUN git clone https://${GITHUB_TOKEN}@github.com/edquestofficial/text-to-sql.git .

# Change directory to the main directory

# Install Python and pip (already included in the base image)

# Install pipenv
RUN pip install --no-cache-dir --upgrade pip
# COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 7860

# Run the main.py 
CMD ["python", "main.py"]