export PROJECT=##YOUR PROJECT NAME HERE##
export REGION=us-central1

#live for streaming transcription, offline for offline transcription
export TYPE=live 

## for offline mode, provide a text file with a list of GCS URLs in the form gs://bucket_name/filename 
## or for live mode, provide a single-channel WAV file encoded at 11025 Hz

export FILE=input.txt

gcloud auth application-default login
gcloud auth application-default set-quota-project $PROJECT

gcloud config set project $PROJECT
gcloud services enable speech.googleapis.com

## TO CONFIGURE AND RUN PYTHON SCRIPT AUTOMATICALLY,
## UNCOMMENT THESE LINES
# virtualenv gcp-speech
# source gcp-speech/bin/activate
# pip install -r requirements.txt
# python3 ./transcribe.py $TYPE 
