#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <version>"
    exit 1
fi

VERSION=$1
ARCHIVE_NAME="vega_ai_src-${VERSION}.tar.gz"
RELEASE_DIR="release"

mkdir -p "$RELEASE_DIR"

tar -czvf "$RELEASE_DIR/$ARCHIVE_NAME" src docker-compose.yml README.md Dockerfile .gitignore .env.example

echo "✅ Created $RELEASE_DIR/$ARCHIVE_NAME"

