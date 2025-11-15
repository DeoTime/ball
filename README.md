# Airline Club Oil Price Monitor 🛢️

A GitHub Actions bot that monitors oil prices from the [Airline Club](https://www.airline-club.com/) API and sends Discord notifications when prices drop below your defined threshold. Now with an interactive Discord bot for contract management!

## Features

- 🔄 Automated monitoring using GitHub Actions (runs every 10 minutes by default)
- 🤖 **NEW: Discord bot with interactive commands** - manage contracts directly from Discord
- 📝 **NEW: Contract-based alerts** - register contracts to pause alerts for a specified number of cycles
- 📉 Configurable price threshold alerts
- 💬 Discord notifications with user mentions
- 🔔 Smart alerting - avoids duplicate notifications for the same price level
- ⚙️ Easy configuration via GitHub Secrets and Variables
- 📊 Detailed logging for debugging

## Quick Links

- **[Discord Bot Setup →](discord-bot/README.md)** - Set up the interactive Discord bot for contract management
- **GitHub Actions Setup** - See below for automated monitoring setup

## Setup Instructions

### 1. Fork or Clone This Repository

Fork this repository to your GitHub account or clone it to create your own instance.

### 2. Configure Discord Webhook

To receive notifications in Discord, you need to create a webhook:

1. Open your Discord server
2. Go to Server Settings → Integrations → Webhooks
3. Click "New Webhook" or "Create Webhook"
4. Choose the channel where you want to receive notifications
5. Copy the webhook URL (it looks like: `https://discord.com/api/webhooks/...`)

### 3. Get Your Discord User ID

To be mentioned in notifications:

1. Enable Developer Mode in Discord (User Settings → Advanced → Developer Mode)
2. Right-click on your username in any channel
3. Click "Copy User ID"
4. This will copy your User ID (a long number like `123456789012345678`)

### 4. Configure GitHub Secrets

Navigate to your repository's Settings → Secrets and variables → Actions:

#### Create the following **Secrets**:

- **`DISCORD_WEBHOOK_URL`**: Your Discord webhook URL from step 2
- **`DISCORD_USER_ID`**: Your Discord user ID from step 3

To add a secret:
1. Click "New repository secret"
2. Enter the name and value
3. Click "Add secret"

### 5. Configure GitHub Variables (Optional)

Navigate to your repository's Settings → Secrets and variables → Actions → Variables tab:

#### Create the following **Variables** (optional, uses defaults if not set):

- **`OIL_PRICE_THRESHOLD`**: The price threshold for alerts (default: `55`)
  - Alerts will be sent when the oil price drops **below** this value
  - Example: Set to `50` to get alerts when price drops below $50

To add a variable:
1. Click "New repository variable"
2. Enter the name and value
3. Click "Add variable"

### 6. Enable GitHub Actions

If GitHub Actions is not already enabled:

1. Go to the "Actions" tab in your repository
2. Click the green button to enable workflows
3. The workflow will now run automatically every 10 minutes

### 7. (Optional) Set Up Discord Bot

For interactive contract management, you can set up the Discord bot:

1. Follow the [Discord Bot Setup Guide](discord-bot/README.md)
2. The bot allows you to:
   - Register contracts with `$contract <cycles>` to pause alerts
   - Check status with `$status` to see current prices and contract info
   - Clear contracts with `$clear` to resume normal alerts
   - Get help with `$help`

The Discord bot and GitHub Actions workflow share state, so contracts registered via the bot will be respected by the automated monitoring system.

## How It Works

1. **Scheduled Monitoring**: The GitHub Actions workflow runs every 10 minutes (configurable)
2. **API Query**: The script fetches current oil prices from `https://v2.airline-club.com/oil-prices`
3. **Price Check**: Compares the latest price against your threshold
4. **Contract Check**: Checks if you have an active contract (set via Discord bot) that should suppress alerts
5. **Smart Alerting**: 
   - Sends notification when price first drops below threshold
   - Sends notification when price drops further
   - Avoids duplicate notifications for the same price level
   - Resets when price goes back above threshold
   - Respects active contracts and suppresses alerts until contract expires
6. **Discord Notification**: Sends a formatted message with price details and mentions you

## Manual Triggering

You can manually trigger a check at any time:

1. Go to the "Actions" tab in your repository
2. Select "Monitor Oil Price" workflow
3. Click "Run workflow" button
4. Click the green "Run workflow" button in the dropdown

## Customizing Check Interval

To change how often the bot checks prices:

1. Edit `.github/workflows/monitor-oil-price.yml`
2. Modify the cron schedule line:
   ```yaml
   schedule:
     - cron: '*/10 * * * *'  # Every 10 minutes
   ```

Common cron patterns:
- Every 5 minutes: `*/5 * * * *`
- Every 15 minutes: `*/15 * * * *`
- Every 30 minutes: `*/30 * * * *`
- Every hour: `0 * * * *`
- Every 6 hours: `0 */6 * * *`

**Note**: GitHub Actions has usage limits. Free accounts get 2,000 minutes/month. Each check takes ~1 minute, so running every 10 minutes uses about 4,320 minutes/month. Consider running less frequently or upgrade your plan.

## Example Notification

When oil prices drop below your threshold, you'll receive a Discord notification like this:

```
@YourUsername
⚠️ Oil Price Alert!
Oil price has dropped below your threshold!

Current Price: $52.50
Threshold: $55.00
Cycle: 56419
Timestamp: 2025-11-15 00:45:00 UTC

Airline Club Oil Price Monitor
```

## Monitoring and Debugging

To check if the bot is working:

1. Go to the "Actions" tab in your repository
2. Click on the latest "Monitor Oil Price" workflow run
3. Click on the "monitor" job to see detailed logs
4. Expand the "Run oil price monitor" step to see execution details

The logs will show:
- API fetch status
- Current price and cycle
- Whether an alert was sent
- Any errors encountered

## Troubleshooting

### No notifications received

1. **Check secrets**: Verify `DISCORD_WEBHOOK_URL` and `DISCORD_USER_ID` are set correctly
2. **Check workflow runs**: Go to Actions tab and check for errors
3. **Check price**: The current price might be above your threshold
4. **Check webhook**: Test your Discord webhook URL using a tool like curl or Postman

### Workflow not running automatically

1. **Enable Actions**: Make sure GitHub Actions is enabled for your repository
2. **Check schedule**: Verify the cron schedule in the workflow file
3. **Repository activity**: GitHub may disable workflows if repository is inactive for 60 days

### Multiple notifications for the same price

This shouldn't happen due to the smart alerting logic. If it does:
1. Check the workflow logs
2. Ensure the state file is persisting between runs
3. Open an issue with the logs

## API Data Format

The Airline Club API returns data in this format:

```json
[
  {"price": 70.1, "cycle": 56417},
  {"price": 70.1, "cycle": 56418},
  {"price": 69.11, "cycle": 56419}
]
```

The bot uses the **last entry** in the array (most recent price).

## Files

- `monitor_oil_price.py`: Main Python script that monitors prices and sends notifications
- `.github/workflows/monitor-oil-price.yml`: GitHub Actions workflow configuration
- `requirements.txt`: Python dependencies

## License

This project is provided as-is for personal use. Feel free to modify and adapt it to your needs.

## Contributing

Feel free to open issues or submit pull requests with improvements!

## Disclaimer

This bot is not affiliated with Airline Club. Use at your own discretion. Be mindful of API rate limits and GitHub Actions usage limits.
