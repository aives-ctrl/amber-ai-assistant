#!/bin/bash

# Amber AI Assistant Self-Update Script
# This script updates Amber's configuration from the GitHub repository

set -e

REPO_DIR="/Users/amberives/amber-ai-assistant"
WORKSPACE_DIR="/Users/amberives/.openclaw/workspace"

echo "🔄 Updating Amber from GitHub..."

# Navigate to repo directory
cd "$REPO_DIR"

# Pull latest changes
echo "📥 Pulling latest changes from GitHub..."
git pull origin main

# Backup current config (optional safety measure)
BACKUP_DIR="$WORKSPACE_DIR/backup-$(date +%Y%m%d-%H%M%S)"
echo "💾 Creating backup at $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"
cp -r "$WORKSPACE_DIR"/{SOUL.md,MEMORY.md,AGENTS.md,TOOLS.md,IDENTITY.md,HEARTBEAT.md,USER.md,email.md,calendar.md,communications.md,follow-up.md,follow-up-tracker.md} "$BACKUP_DIR/" 2>/dev/null || true

# Dynamic files that Amber owns at runtime -- NEVER overwrite these
SKIP_FILES="follow-up-tracker.md"

# Copy updated config files to workspace, skipping dynamic working files
echo "Updating configuration files..."
for f in config/*; do
    filename=$(basename "$f")
    # Skip dynamic files that Amber owns at runtime
    skip=false
    for sf in $SKIP_FILES; do
        if [ "$filename" = "$sf" ]; then
            skip=true
            break
        fi
    done
    if [ "$skip" = true ]; then
        echo "  SKIPPED $filename (dynamic working file, Amber owns this at runtime)"
        continue
    fi
    cp "$f" "$WORKSPACE_DIR/"
    echo "  Updated $filename"
done

# Copy updated scripts if they exist
if [ -d "scripts" ] && [ "$(ls -A scripts)" ]; then
    echo "🔧 Updating scripts..."
    cp -r scripts/* "$WORKSPACE_DIR/scripts/"
fi

# Copy updated skills if they exist
if [ -d "skills" ] && [ "$(ls -A skills)" ]; then
    echo "🎯 Updating skills..."
    mkdir -p "$WORKSPACE_DIR/skills"
    cp -r skills/* "$WORKSPACE_DIR/skills/"
fi

echo "✅ Update complete! Amber has been updated with the latest configuration."
echo "📂 Backup created at: $BACKUP_DIR"
echo ""
echo "🔄 Note: You may need to restart the OpenClaw session to pick up all changes."