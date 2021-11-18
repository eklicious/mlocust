#!/bin/bash

# Download the gcloud sdk and install
curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-365.0.0-linux-x86_64.tar.gz
tar -xvzf google-cloud-sdk-365.0.0-linux-x86_64.tar.gz
./google-cloud-sdk/install.sh --usage-reporting false --quiet

# Download and install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Authenticate our gcloud client
gcloud auth activate-service-account nlp-250@mside-287120.iam.gserviceaccount.com --key-file=mside-287120-8abbcf9c3ce8.json

# Set the gcloud project for our client
gcloud config set project mside-287120

# Now we should be able to run the flask app
flask run --host=0.0.0.0
