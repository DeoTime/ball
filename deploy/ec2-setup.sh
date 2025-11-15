#!/bin/bash
# EC2 Setup Script for Oil Price Discord Bot
# This script sets up the bot on an AWS EC2 instance (Amazon Linux 2 or Ubuntu)

set -e

echo "========================================"
echo "Oil Price Discord Bot - EC2 Setup"
echo "========================================"
echo ""

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "Cannot detect OS. Please install manually."
    exit 1
fi

echo "Detected OS: $OS"
echo ""

# Update system
echo "Updating system packages..."
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    sudo apt-get update
    sudo apt-get upgrade -y
elif [ "$OS" = "amzn" ] || [ "$OS" = "rhel" ] || [ "$OS" = "centos" ]; then
    sudo yum update -y
fi

# Install Python 3.11 and git
echo "Installing Python 3.11 and git..."
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    sudo apt-get install -y python3.11 python3.11-venv python3-pip git
elif [ "$OS" = "amzn" ]; then
    sudo yum install -y python3.11 python3.11-pip git
fi

# Clone repository (or use existing if already cloned)
echo "Setting up application directory..."
if [ ! -d "$HOME/oil-price-bot" ]; then
    cd $HOME
    git clone https://github.com/DeoTime/ball.git oil-price-bot
    cd oil-price-bot
else
    cd $HOME/oil-price-bot
    git pull
fi

# Create virtual environment
echo "Creating Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo ""
    echo "========================================"
    echo "IMPORTANT: Configure your .env file"
    echo "========================================"
    echo "Please edit $HOME/oil-price-bot/.env and set:"
    echo "  - DISCORD_BOT_TOKEN"
    echo "  - DISCORD_CHANNEL_ID"
    echo "  - DISCORD_USER_ID"
    echo ""
    echo "After editing, run: sudo systemctl start oil-price-bot"
    echo ""
    read -p "Press Enter to open editor (nano) or Ctrl+C to exit and edit manually..."
    nano .env
fi

# Install systemd service
echo "Installing systemd service..."
sudo cp deploy/bot.service /etc/systemd/system/oil-price-bot.service

# Update service file with current user and path
sudo sed -i "s|User=ubuntu|User=$USER|g" /etc/systemd/system/oil-price-bot.service
sudo sed -i "s|WorkingDirectory=/home/ubuntu/oil-price-bot|WorkingDirectory=$HOME/oil-price-bot|g" /etc/systemd/system/oil-price-bot.service
sudo sed -i "s|/home/ubuntu/oil-price-bot/venv/bin/python|$HOME/oil-price-bot/venv/bin/python|g" /etc/systemd/system/oil-price-bot.service

# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable oil-price-bot

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Verify your .env configuration: nano $HOME/oil-price-bot/.env"
echo "2. Start the bot: sudo systemctl start oil-price-bot"
echo "3. Check status: sudo systemctl status oil-price-bot"
echo "4. View logs: sudo journalctl -u oil-price-bot -f"
echo ""
echo "The bot will automatically start on system reboot."
echo ""
