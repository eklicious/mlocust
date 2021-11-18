# Start with a base Python 3.8.2 image
FROM python:3.8.2

WORKDIR /mlocust

ENV PATH "$PATH:/mlocust/google-cloud-sdk/bin"

# Add the external tasks directory into /tasks
# ADD locust-tasks /locust-tasks
copy . .

# Install the required dependencies via pip
RUN pip install -r requirements.txt

# Expose the required Flask port
EXPOSE 5000 

# Set script to be executable
RUN chmod 755 run.sh

# Start Flask with all pre-requisites
ENTRYPOINT [ "bash", "run.sh" ] 
