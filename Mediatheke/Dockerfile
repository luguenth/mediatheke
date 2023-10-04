FROM python:3.10
# Set the working directory to /app
WORKDIR /Mediatheke

# Copy the current directory contents into the container at /app
COPY . /Mediatheke

# Install any needed packages specified in requirements.txt
RUN pip install pipenv
RUN pipenv install

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME Mediatheke

# Make the script executable
RUN chmod +x /Mediatheke/startup.sh

# Run startup script when the container launches
CMD ["/Mediatheke/startup.sh"]