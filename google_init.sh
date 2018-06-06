#!/bin/bash

#project_id=sampleo-206319
#key_file=/auth/googleauth.json

gcloud auth activate-service-account --key-file=/auth/google-service-account-key.json
gcloud config set project $GOOGLE_PROJECT_ID
