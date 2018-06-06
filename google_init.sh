#!/bin/bash

# e.g., /auth/google-service-account-key.json
key_file=$1

# parse google_project_id from the key itself
GOOGLE_PROJECT_ID=$(python -c "import json; f = open('$key_file','r'); key = json.load(f); print(key['project_id']); f.close()")

gcloud auth activate-service-account --key-file=$key_file
gcloud config set project $GOOGLE_PROJECT_ID
