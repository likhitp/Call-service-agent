#!/usr/bin/env bash
# exit on error
set -o errexit

# Install system dependencies
apt-get update
apt-get install -y portaudio19-dev python3-pyaudio

# Install Python dependencies
pip install -r requirements.txt 