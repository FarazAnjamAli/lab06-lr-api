#!/usr/bin/env bash
# One-time setup for an Ubuntu 22.04 / 24.04 EC2 instance: Java 21 + Jenkins LTS + Docker (+ compose plugin)
# Run with:  bash ec2-setup.sh
set -e

echo ">>> Java 21"
sudo apt update
sudo apt install -y fontconfig openjdk-21-jre curl git

echo ">>> Jenkins LTS"
sudo mkdir -p /etc/apt/keyrings
sudo wget -O /etc/apt/keyrings/jenkins-keyring.asc \
  https://pkg.jenkins.io/debian-stable/jenkins.io-2026.key
echo "deb [signed-by=/etc/apt/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/" \
  | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt update
sudo apt install -y jenkins

echo ">>> Docker Engine + docker compose plugin"
curl -fsSL https://get.docker.com | sudo sh

echo ">>> Let Jenkins (and ubuntu user) run docker without sudo"
sudo usermod -aG docker jenkins
sudo usermod -aG docker ubuntu
sudo systemctl enable --now docker jenkins
sudo systemctl restart jenkins

echo ""
docker --version || true
sudo docker compose version
echo ""
echo "Jenkins initial admin password:"
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
echo ""
echo "Open http://<EC2_PUBLIC_IP>:8080  (log out/in of SSH so 'ubuntu' picks up the docker group)"
