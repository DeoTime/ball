# Discord Bot for Oil Price Monitoring 🤖

A Discord bot that allows you to manage oil price monitoring contracts through chat commands. This bot works alongside the GitHub Actions monitoring workflow to provide intelligent contract-based alerting.

## Features

- 🎮 **Interactive Commands**: Control your monitoring preferences through Discord commands
- 📝 **Contract Management**: Register contracts to pause alerts for a specific number of cycles
- 📊 **Real-time Status**: Check current oil prices and contract status anytime
- 🔗 **Integration**: Seamlessly integrates with the GitHub Actions monitoring workflow
- 💾 **Persistent State**: Shares state with the monitoring workflow for coordinated alerts

## Commands

### `$contract <cycles>`
Register a contract to pause price alerts for a specified number of cycles.

**Example:**
```
$contract 52
```
**Response:**
```
✅ Contract Registered!
You won't be pinged until cycle 56569 (52 cycles from now)

Current Cycle: 56517
Contract End Cycle: 56569
Cycles Remaining: 52
```

### `$status`
Display current oil price, cycle, and contract status.

**Example:**
```
$status
```
**Response:**
```
🛢️ Oil Price Status

Current Cycle: 56517
Current Price: $53.76
Price Threshold: $55.00
Contract Status: ✅ Active
Contract Expires: Cycle 56569 (52 cycles remaining)
Price Status: ⚠️ Below threshold (by $1.24)
```

### `$clear`
Clear any active contract and resume normal price alerts.

**Example:**
```
$clear
```
**Response:**
```
✅ Contract Cleared
Your contract has been removed. You will now receive price alerts normally.
```

### `$help`
Display a list of all available commands and their usage.

**Example:**
```
$help
```

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- A Discord account
- A Discord server where you have admin permissions

### Step 1: Create a Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name (e.g., "Oil Price Bot")
3. Go to the "Bot" section in the left sidebar
4. Click "Add Bot" and confirm
5. Under the bot's username, click "Reset Token" and copy the token (you'll need this later)
6. Enable the following **Privileged Gateway Intents**:
   - ✅ Message Content Intent
7. Go to the "OAuth2" → "URL Generator" section
8. Select the following scopes:
   - ✅ `bot`
9. Select the following bot permissions:
   - ✅ Send Messages
   - ✅ Send Messages in Threads
   - ✅ Embed Links
   - ✅ Read Message History
   - ✅ Read Messages/View Channels
10. Copy the generated URL at the bottom and open it in your browser
11. Select your Discord server and authorize the bot

### Step 2: Set Up Environment Variables

Create a `.env` file in the `discord-bot` directory or set environment variables:

```bash
# Required
DISCORD_BOT_TOKEN=your_bot_token_here

# Optional - for integration with monitoring alerts
DISCORD_WEBHOOK_URL=your_webhook_url_here
DISCORD_USER_ID=your_discord_user_id_here
OIL_PRICE_THRESHOLD=55

# Optional - custom state file location
STATE_FILE_PATH=/tmp/oil_price_bot_state.json
```

**Getting your Discord User ID:**
1. Enable Developer Mode in Discord (User Settings → Advanced → Developer Mode)
2. Right-click on your username in any channel
3. Click "Copy User ID"

### Step 3: Install Dependencies

```bash
cd discord-bot
pip install -r requirements.txt
```

### Step 4: Run the Bot Locally

```bash
cd discord-bot
python bot.py
```

The bot should now be online in your Discord server!

## Deployment Options

For the bot to work 24/7, it needs to run on a server. Here are some free options:

### Option 1: Replit (Easiest)

1. Go to [Replit](https://replit.com/)
2. Create a new Repl and import this repository
3. Set environment variables in the "Secrets" tab:
   - `DISCORD_BOT_TOKEN`
   - `DISCORD_WEBHOOK_URL`
   - `DISCORD_USER_ID`
   - `OIL_PRICE_THRESHOLD`
4. Create a `.replit` file:
   ```toml
   run = "python discord-bot/bot.py"
   ```
5. Click "Run"
6. Consider using [UptimeRobot](https://uptimerobot.com/) to ping your Repl and keep it alive

### Option 2: Railway.app

1. Go to [Railway.app](https://railway.app/)
2. Create a new project and connect your GitHub repository
3. Set environment variables in the project settings
4. Deploy from the `discord-bot` directory
5. Railway provides free tier with $5 monthly credit

### Option 3: Fly.io

1. Install the [Fly CLI](https://fly.io/docs/hands-on/install-flyctl/)
2. Create a `Dockerfile` in the `discord-bot` directory:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY bot.py .
   CMD ["python", "bot.py"]
   ```
3. Run:
   ```bash
   fly launch
   fly secrets set DISCORD_BOT_TOKEN=your_token_here
   fly deploy
   ```

### Option 4: Local Server / VPS

If you have a server or Raspberry Pi running 24/7:

1. Clone the repository
2. Set up environment variables
3. Install dependencies
4. Run the bot with a process manager like `systemd` or `pm2`

**Example systemd service file** (`/etc/systemd/system/oil-price-bot.service`):
```ini
[Unit]
Description=Oil Price Discord Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/ball/discord-bot
Environment="DISCORD_BOT_TOKEN=your_token_here"
Environment="DISCORD_WEBHOOK_URL=your_webhook_url"
Environment="DISCORD_USER_ID=your_user_id"
Environment="OIL_PRICE_THRESHOLD=55"
ExecStart=/usr/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable oil-price-bot
sudo systemctl start oil-price-bot
```

## Integration with GitHub Actions

The Discord bot shares state with the GitHub Actions monitoring workflow through a shared JSON state file. This allows:

1. **Contract-based Alerts**: When you register a contract via the bot, the GitHub Actions workflow will respect it and not send alerts until the contract expires
2. **Coordinated State**: Both systems update the same state file to track contracts and alert history

### State File Format

The shared state file (`oil_price_bot_state.json`) contains:

```json
{
  "contract_end_cycle": 56569,
  "last_alerted_price": 53.76,
  "last_cycle": 56517,
  "last_price": 53.76
}
```

### How It Works

1. **Bot Sets Contract**: When you use `$contract 52`, the bot fetches the current cycle and stores `contract_end_cycle` in the state file
2. **Workflow Checks Contract**: The GitHub Actions workflow reads the state file and checks if the current cycle is less than `contract_end_cycle`
3. **Alerts Suppressed**: If a contract is active, the workflow will not send alerts even if the price is below the threshold
4. **Contract Expires**: Once the current cycle reaches or exceeds `contract_end_cycle`, normal alerting resumes

## State File Location

By default, the state file is stored at `/tmp/oil_price_bot_state.json`. You can customize this location using the `STATE_FILE_PATH` environment variable.

**Important Notes:**
- For local deployment, make sure both the bot and GitHub Actions can access the same state file
- For cloud deployment, consider using a shared storage solution like:
  - GitHub Gists API (accessible from both bot and Actions)
  - A simple key-value store (Redis, etc.)
  - Cloud storage (S3, Google Cloud Storage with signed URLs)
  - A lightweight database (SQLite, PostgreSQL, etc.)

## Troubleshooting

### Bot doesn't respond to commands

1. **Check bot is online**: Look for the bot in your server's member list (should show as online)
2. **Check permissions**: Ensure the bot has permission to read and send messages in the channel
3. **Check Message Content Intent**: Verify that "Message Content Intent" is enabled in the Discord Developer Portal
4. **Check logs**: Look at the bot's console output for errors

### "Failed to fetch oil price data" error

1. **Check internet connection**: The bot needs internet access to reach the Airline Club API
2. **Check API status**: Visit `https://v2.airline-club.com/oil-prices` in your browser to ensure it's working
3. **Check firewall**: Ensure your hosting environment allows outbound HTTPS requests

### Bot disconnects frequently

1. **Check hosting**: Free hosting services may have limitations on uptime
2. **Use a keep-alive service**: Services like UptimeRobot can ping your bot to keep it awake
3. **Check logs**: Look for error messages indicating why the bot is disconnecting

### State not syncing with GitHub Actions

1. **Check state file path**: Ensure both the bot and the workflow are using the same `STATE_FILE_PATH`
2. **Check file permissions**: Ensure both processes can read and write to the state file
3. **Check state file location**: If deploying the bot remotely, you'll need a shared storage solution

## Security Best Practices

1. **Never commit tokens**: Keep your `DISCORD_BOT_TOKEN` secret and never commit it to Git
2. **Use environment variables**: Always use environment variables or a `.env` file for sensitive data
3. **Restrict bot permissions**: Only give the bot the minimum permissions it needs
4. **Regularly rotate tokens**: Periodically reset your bot token for security

## Contributing

Feel free to open issues or submit pull requests with improvements!

## License

This project is provided as-is for personal use. Feel free to modify and adapt it to your needs.
