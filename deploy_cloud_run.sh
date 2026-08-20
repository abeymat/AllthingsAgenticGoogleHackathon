#!/usr/bin/env bash
# Automated Google Cloud Run Deployment Script for NexusDev AI

set -e

# Load environment variables if .env exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

GCP_PROJECT="${GCP_PROJECT_ID:-nexusdev-ai-project}"
REGION="${GCP_LOCATION:-us-central1}"
SERVICE_NAME="nexusdev-ai-backend"
IMAGE_NAME="gcr.io/${GCP_PROJECT}/${SERVICE_NAME}:latest"

echo "========================================================"
echo " Deploying NexusDev AI to Google Cloud Run"
echo " Project ID : ${GCP_PROJECT}"
echo " Region     : ${REGION}"
echo " Service    : ${SERVICE_NAME}"
echo "========================================================"

# Step 1: Set GCP Project
gcloud config set project "${GCP_PROJECT}"

# Step 2: Build Container Image using Google Cloud Build
echo "[1/3] Building Container Image via Google Cloud Build..."
gcloud builds submit --config=backend/Dockerfile --tag "${IMAGE_NAME}" . || \
gcloud builds submit --tag "${IMAGE_NAME}" -f backend/Dockerfile .

# Step 3: Deploy Container to Cloud Run
echo "[2/3] Deploying Container to Google Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
    --image "${IMAGE_NAME}" \
    --platform managed \
    --region "${REGION}" \
    --allow-unauthenticated \
    --set-env-vars "GCP_PROJECT_ID=${GCP_PROJECT},JIRA_DOMAIN=${JIRA_DOMAIN},JIRA_PROJECT_KEY=${JIRA_PROJECT_KEY}"

# Step 4: Output Deployed URL
echo "[3/3] Deployment Complete!"
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --platform managed --region "${REGION}" --format 'value(status.url)')
echo "========================================================"
echo " 🎉 NexusDev AI is LIVE on Google Cloud Run:"
echo " 🌐 ${SERVICE_URL}"
echo "========================================================"
