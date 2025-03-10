#!/usr/bin/env bash
# exit on error
set -o errexit

# Install system dependencies
apt-get update
apt-get install -y portaudio19-dev python3-pyaudio

# Install specific PyAudio wheel for Linux
pip install --no-cache-dir --platform manylinux2014_x86_64 --only-binary=:all: pyaudio

# Install other requirements
pip install -r requirements.txt 