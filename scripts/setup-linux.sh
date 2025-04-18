#!/bin/bash

ENV_NAME="FinsightAI"
PYTHON_VERSION="3.12"

# Install the required dependencies
sudo apt-get update
sudo apt-get install -y curl make

# Get the latest version of Docker
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
$(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install the latest version of Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Enable and start Docker service
sudo systemctl enable docker
sudo usermod -aG docker "$USER"

# Download images for the required services
docker compose build

# Install the latest version of Astral
sudo curl -Ls https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# Refresh shell environment
hash -r

# Install the required Python version and create a virtual environment
uv python install $PYTHON_VERSION
uv venv --prompt=$ENV_NAME --python=$PYTHON_VERSION

# Install the required packages
uv sync

# Set up the crawler dependencies
uv run crawl4ai-setup

# Change permissions for the current directory
chmod -R 777 .