#!/bin/bash

echo "🚀 Test de l'application déployée"
echo "=================================="

APP_URL="http://localhost:5002"
AUTH_HEADER="Authorization: Bearer jenkins_test_api_2024"

echo "1. Test API Status"
curl -s "$APP_URL/" | jq '.'

echo -e "\n2. Test Health Check"
curl -s "$APP_URL/health" | jq '.'

echo -e "\n3. Test Upload/Download complet"
echo "Pipeline test file content" > pipeline_test.txt

# Upload
echo "📤 Upload..."
UPLOAD_RESPONSE=$(curl -s -X POST -H "$AUTH_HEADER" -F "file=@pipeline_test.txt" "$APP_URL/upload")
echo "$UPLOAD_RESPONSE" | jq '.'

FILE_ID=$(echo "$UPLOAD_RESPONSE" | jq -r '.file_id')
echo "📁 File ID: $FILE_ID"

# Download
echo -e "\n📥 Download..."
curl -s -H "$AUTH_HEADER" -o "pipeline_downloaded.txt" "$APP_URL/download/$FILE_ID"

# Vérification intégrité
echo -e "\n🔍 Vérification intégrité:"
ORIGINAL_HASH=$(sha256sum pipeline_test.txt | cut -d' ' -f1)
DOWNLOADED_HASH=$(sha256sum pipeline_downloaded.txt | cut -d' ' -f1)

echo "Original:   $ORIGINAL_HASH"
echo "Downloaded: $DOWNLOADED_HASH"

if [[ "$ORIGINAL_HASH" == "$DOWNLOADED_HASH" ]]; then
    echo "✅ Intégrité OK!"
else
    echo "❌ Intégrité KO!"
fi

# Nettoyage
rm -f pipeline_test.txt pipeline_downloaded.txt

echo -e "\n🎉 Tests post-pipeline terminés!"
