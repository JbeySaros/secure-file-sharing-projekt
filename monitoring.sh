#!/bin/bash

echo "📊 Secure File Sharing - Monitoring Dashboard"
echo "============================================="

# Status Jenkins
echo "🏗️ Jenkins Status:"
curl -s http://localhost:8080/api/json | jq '.mode, .numExecutors' 2>/dev/null || echo "Jenkins non accessible"

# Status Application
echo -e "\n🚀 Application Status:"
if curl -f -s http://localhost:5002/health > /dev/null; then
    echo "✅ Application en ligne"
    curl -s http://localhost:5002/health | jq '.status' 2>/dev/null
else
    echo "❌ Application hors ligne"
fi

# Docker containers
echo -e "\n🐳 Docker Containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# DockerHub images
echo -e "\n📦 Recent DockerHub builds:"
echo "Vérifiez: https://hub.docker.com/r/votre-username/secure-file-sharing/tags"

# Espace disque
echo -e "\n💾 Disk Usage:"
df -h /var/lib/jenkins /var/lib/docker 2>/dev/null || echo "Dossiers Jenkins/Docker non trouvés"

echo -e "\n🎯 Quick Actions:"
echo "- Jenkins: http://localhost:8080"
echo "- Application: http://localhost:5002"
echo "- DockerHub: https://hub.docker.com/r/votre-username/secure-file-sharing"
