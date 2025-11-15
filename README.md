# Airline Club Oil Price Monitor 🛢️

A standalone Discord bot that runs 24/7 on AWS, monitoring oil prices from the [Airline Club](https://www.airline-club.com/) API and sending smart notifications when prices drop below your threshold.

## Features

- 🤖 **24/7 Discord Bot** - Runs continuously on AWS (EC2, ECS, or any server)
- 🔄 **Automatic Monitoring** - Polls oil prices every 10 minutes (configurable)
- 📝 **Contract Management** - Register contracts to pause alerts for specified cycles
- 💬 **Interactive Commands** - Full control through Discord chat commands
- 🔔 **Smart Alerts** - Intelligent ping logic to avoid spam
- 💾 **SQLite Database** - Local state management
- 📊 **Compact Status Updates** - Get updates every cycle
- ⚙️ **Easy Configuration** - Simple environment variables
- 🚀 **Quick Deployment** - Get running on AWS in under 10 minutes

## Quick Start

### Prerequisites

- Discord account and server with admin permissions
- AWS account (or any server/VPS)
- Python 3.11+ (for local testing)

### Step 1: Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" → name it "Oil Price Bot"
3. Go to "Bot" section → Click "Add Bot"
4. Copy the bot token (you'll need this later)
5. Enable **Message Content Intent** under Privileged Gateway Intents
6. Go to OAuth2 → URL Generator:
   - Select scope: `bot`
   - Select permissions: Send Messages, Embed Links, Read Messages
7. Copy the generated URL and invite the bot to your server

### Step 2: Get Discord IDs

**Channel ID** (where bot posts updates):
1. Enable Developer Mode (User Settings → Advanced → Developer Mode)
2. Right-click on the channel → Copy Channel ID

**User ID** (who gets pinged):
1. Right-click on your username → Copy User ID

### Step 3: Configure Environment

Create a `.env` file with your configuration:

```bash
DISCORD_BOT_TOKEN=your_bot_token_here
DISCORD_CHANNEL_ID=your_channel_id_here
DISCORD_USER_ID=your_user_id_here
OIL_PRICE_THRESHOLD=55
CHECK_INTERVAL_MINUTES=10
```

### Step 4: Deploy to AWS EC2 (Recommended)

The easiest way to run the bot 24/7:

1. **Launch EC2 Instance**:
   - AMI: Amazon Linux 2023 or Ubuntu 22.04
   - Instance type: t2.micro (free tier eligible)
   - Configure Security Group: Allow SSH (port 22)
   - Launch and download key pair

2. **Connect to Instance**:
   ```bash
   ssh -i your-key.pem ec2-user@your-instance-ip
   # or for Ubuntu: ubuntu@your-instance-ip
   ```

3. **Run Setup Script**:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/DeoTime/ball/main/deploy/ec2-setup.sh | bash
   ```

4. **Configure Environment**:
   ```bash
   cd ~/oil-price-bot
   nano .env  # Add your Discord credentials
   ```

5. **Start the Bot**:
   ```bash
   sudo systemctl start oil-price-bot
   sudo systemctl status oil-price-bot
   ```

That's it! Your bot is now running 24/7.

### Alternative: Docker Deployment

If you prefer Docker:

```bash
# Build the image
docker build -t oil-price-bot .

# Run the container
docker run -d \
  --name oil-price-bot \
  --restart unless-stopped \
  -e DISCORD_BOT_TOKEN=your_token \
  -e DISCORD_CHANNEL_ID=your_channel_id \
  -e DISCORD_USER_ID=your_user_id \
  -v $(pwd)/data:/data \
  oil-price-bot
```

### Alternative: Local Testing

For development or testing:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DISCORD_BOT_TOKEN=your_token
export DISCORD_CHANNEL_ID=your_channel_id
export DISCORD_USER_ID=your_user_id

# Run the bot
python bot.py
```

## Bot Commands

### `$contract <cycles>`
Register a contract to pause alerts for X cycles.

```
$contract 52
```
Response: `✅ Contract registered! You won't be pinged until cycle 56569 (52 cycles from now)`

### `$status`
Show current oil price, cycle, threshold, and contract status.

```
$status
```
Response: Shows cycle, price, threshold, check interval, contract status, and compact status example.

### `$clear`
Clear any active contract.

```
$clear
```
Response: `✅ Contract cleared. You will now receive price alerts normally.`

### `$threshold <price>`
Set the alert threshold (default: $55).

```
$threshold 60
```
Response: `✅ Threshold updated to $60.00`

### `$interval <minutes>`
Set how often to check prices (default: 10 minutes).

```
$interval 5
```
Response: `✅ Check interval updated to 5 minutes`

### `$help`
Show all available commands.

```
$help
```

## How It Works

### Automatic Monitoring Loop

1. **Background Task**: Runs every X minutes (configurable via `$interval`)
2. **API Polling**: Fetches current prices from `https://v2.airline-club.com/oil-prices`
3. **Cycle Detection**: Only sends updates when a new cycle is detected
4. **Contract Check**: Respects active contracts (won't ping during contract)
5. **Smart Alerting**: 
   - First time below threshold → Ping user
   - Still below threshold → Send updates without ping
   - Back above threshold → Reset ping state
   - During contract → No pings, but still send updates
6. **Compact Updates**: Posts status every cycle in the format:
   ```
   🛢️ Cycle 56517 | Price: $53.76 | Status: ⚠️ Below threshold ($55.00)
   📝 Contract active: 52 cycles remaining (ends cycle 56569)
   ```

### Smart Alert Logic

The bot uses intelligent ping management:

- **First Alert**: When price drops below threshold for the first time, you get pinged
- **Subsequent Updates**: If price stays below, you get updates without pings
- **Price Recovery**: When price goes back above threshold, ping state resets
- **Contract Protection**: During active contracts, no pings but status updates continue

### Database State

The bot uses SQLite to store:
- `last_pinged_below_threshold`: Whether user has been pinged for current low-price condition
- `contract_end_cycle`: End cycle for active contract (NULL if none)
- `oil_price_threshold`: Current alert threshold (default: 55)
- `check_interval_minutes`: How often to poll API (default: 10)
- `user_id_to_ping`: Discord user ID for mentions
- `last_cycle`: Last known cycle number
- `last_price`: Last known oil price

## Example Updates

### Regular Cycle Update (Above Threshold)
```
🛢️ Cycle 56517 | Price: $57.23 | Status: ✅ Above threshold ($55.00)
```

### Price Below Threshold (First Time - With Ping)
```
@YourUsername
🛢️ Cycle 56518 | Price: $53.76 | Status: ⚠️ Below threshold ($55.00)
```

### Price Still Below Threshold (No Ping)
```
🛢️ Cycle 56519 | Price: $52.10 | Status: ⚠️ Below threshold ($55.00)
```

### With Active Contract
```
🛢️ Cycle 56520 | Price: $51.50 | Status: ⚠️ Below threshold ($55.00)
📝 Contract active: 49 cycles remaining (ends cycle 56569)
```

## Managing Your Bot

### Check Bot Status
```bash
sudo systemctl status oil-price-bot
```

### View Real-time Logs
```bash
sudo journalctl -u oil-price-bot -f
```

### Restart Bot
```bash
sudo systemctl restart oil-price-bot
```

### Stop Bot
```bash
sudo systemctl stop oil-price-bot
```

### Update Bot
```bash
cd ~/oil-price-bot
git pull
sudo systemctl restart oil-price-bot
```

## Troubleshooting

### Bot doesn't connect to Discord

1. **Check token**: Verify `DISCORD_BOT_TOKEN` is correct in `.env`
2. **Check bot permissions**: Ensure bot has necessary permissions in Discord
3. **Check logs**: Run `sudo journalctl -u oil-price-bot -f` to see error messages
4. **Verify intents**: Make sure Message Content Intent is enabled in Developer Portal

### No status updates in channel

1. **Check channel ID**: Verify `DISCORD_CHANNEL_ID` is correct
2. **Check bot permissions**: Ensure bot can read and send messages in the channel
3. **Check if bot is online**: Look for the bot in your server's member list
4. **Check logs**: Look for errors in `journalctl -u oil-price-bot -f`

### Not getting pinged on alerts

1. **Check user ID**: Verify `DISCORD_USER_ID` is set correctly in `.env`
2. **Check threshold**: Current price might be above your threshold
3. **Check contract**: You might have an active contract (use `$status` to check)
4. **Check ping state**: Bot might have already pinged you (wait for price to go above threshold)

### Bot crashes or restarts frequently

1. **Check RAM**: t2.micro has 1GB RAM, might need t2.small if running other services
2. **Check logs**: `journalctl -u oil-price-bot --since "1 hour ago"`
3. **Check internet**: Verify EC2 instance has internet access
4. **Check API**: Visit `https://v2.airline-club.com/oil-prices` to ensure it's working

### Database errors

1. **Check permissions**: Ensure bot can write to database file
2. **Check disk space**: Run `df -h` to check available space
3. **Reset database**: Stop bot, delete `bot_data.db`, restart bot (will lose state)

### Commands not working

1. **Check prefix**: Commands must start with `$` (e.g., `$help`)
2. **Check permissions**: Bot needs to read messages in the channel
3. **Check Message Content Intent**: Must be enabled in Discord Developer Portal
4. **Try in different channel**: Some channels might have permission issues

## API Information

### Endpoint
```
https://v2.airline-club.com/oil-prices
```

### Response Format
```json
[
  {"price": 70.1, "cycle": 56417},
  {"price": 70.1, "cycle": 56418},
  {"price": 69.11, "cycle": 56419}
]
```

The bot uses the **last entry** in the array (most recent price/cycle).

### Rate Limiting
- Default check interval: 10 minutes (configurable)
- Be respectful of the API
- Minimum recommended interval: 5 minutes

## AWS Cost Estimate

### Free Tier (First 12 Months)
- **EC2 t2.micro**: 750 hours/month (enough for 24/7)
- **Storage**: 30 GB EBS (bot uses ~100MB)
- **Data Transfer**: 15 GB outbound (bot uses minimal bandwidth)
- **Total**: **$0/month** ✅

### After Free Tier
- **EC2 t2.micro**: ~$8.50/month
- **EBS Storage**: ~$3/month for 30GB
- **Data Transfer**: ~$1/month
- **Total**: ~$12.50/month

### Cost Optimization Tips
- Use EC2 Spot Instances for ~70% savings (not guaranteed uptime)
- Use AWS Lightsail ($3.50/month for 512MB RAM)
- Use free tier alternatives: Railway ($5 credit/month), Fly.io (3 shared VMs free)

## Project Structure

```
/
  bot.py                 # Main Discord bot with monitoring loop
  database.py            # SQLite database handler
  requirements.txt       # Python dependencies (discord.py, requests)
  Dockerfile            # Docker container configuration
  .env.example          # Environment variables template
  README.md             # This file - deployment and usage guide
  deploy/
    ec2-setup.sh        # Automated EC2 deployment script
    bot.service         # systemd service file for auto-restart
```

## Security Best Practices

1. **Never commit secrets**: Keep `.env` file out of git (already in `.gitignore`)
2. **Use environment variables**: Never hardcode tokens in code
3. **Restrict bot permissions**: Only grant necessary Discord permissions
4. **Secure your EC2**: Use security groups to limit SSH access
5. **Regular updates**: Keep dependencies updated (`pip install -r requirements.txt --upgrade`)
6. **Monitor logs**: Regularly check logs for suspicious activity

## Contributing

Feel free to open issues or submit pull requests!

## License

This project is provided as-is for personal use. Feel free to modify and adapt it to your needs.

## Disclaimer

This bot is not affiliated with Airline Club. Use at your own discretion. Be respectful of API rate limits.
