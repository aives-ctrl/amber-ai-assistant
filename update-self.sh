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

# Copy updated config files to workspace
echo "📁 Updating configuration files..."
cp config/* "$WORKSPACE_DIR/"

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