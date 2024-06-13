# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# List the files to verify the presence of requirements.txt and server.py
RUN ls -al /app

# Install any needed dependencies specified in requirements.txt
RUN pip install -r requirements.txt

# Run app.py when the container launches
CMD ["python", "-u", "server.py"]
