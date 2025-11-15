#!/usr/bin/env python3
"""
AWS-Hosted Discord Bot for Oil Price Monitoring
Runs 24/7 and monitors oil prices from Airline Club API.
"""

import os
import sys
import logging
import asyncio
from typing import Optional, Dict, Any
import discord
from discord.ext import commands, tasks
import requests

from database import BotDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')
DISCORD_USER_ID = os.getenv('DISCORD_USER_ID')
API_URL = os.getenv('API_URL', 'https://v2.airline-club.com/oil-prices')
DEFAULT_THRESHOLD = float(os.getenv('OIL_PRICE_THRESHOLD', '55'))
DEFAULT_INTERVAL = int(os.getenv('CHECK_INTERVAL_MINUTES', '10'))

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents, help_command=None)

# Database
db = BotDatabase('bot_data.db')


def fetch_oil_prices() -> Optional[Dict[str, Any]]:
    """Fetch current oil prices from the Airline Club API."""
    try:
        logger.info(f"Fetching oil prices from {API_URL}")
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not isinstance(data, list) or len(data) == 0:
            logger.error("Invalid or empty price data received")
            return None
        
        # Get the most recent price (last item in the array)
        latest_entry = data[-1]
        current_price = latest_entry.get('price')
        current_cycle = latest_entry.get('cycle')
        
        if current_price is None or current_cycle is None:
            logger.error("Invalid price data format")
            return None
        
        return {
            'price': float(current_price),
            'cycle': int(current_cycle)
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch oil prices: {e}")
        return None
    except (ValueError, KeyError) as e:
        logger.error(f"Failed to parse price data: {e}")
        return None


@bot.event
async def on_ready():
    """Event handler for when the bot is ready."""
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Bot is in {len(bot.guilds)} guild(s)')
    
    # Initialize database with env defaults if not set
    state = db.get_state()
    if state['oil_price_threshold'] is None or state['oil_price_threshold'] == 55.0:
        db.set_threshold(DEFAULT_THRESHOLD)
    if state['check_interval_minutes'] is None or state['check_interval_minutes'] == 10:
        db.set_interval(DEFAULT_INTERVAL)
    if state['user_id_to_ping'] is None and DISCORD_USER_ID:
        db.set_user_id(DISCORD_USER_ID)
    
    # Start monitoring loop
    if not monitor_oil_prices.is_running():
        interval = db.get_interval()
        monitor_oil_prices.change_interval(minutes=interval)
        monitor_oil_prices.start()
        logger.info(f"Started monitoring loop with {interval} minute interval")


@bot.event
async def on_command_error(ctx, error):
    """Handle command errors."""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Unknown command. Use `$help` to see available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument. Use `$help` for usage information.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"❌ Invalid argument. Please check your input.")
    else:
        logger.error(f"Command error: {error}")
        await ctx.send(f"❌ An error occurred: {str(error)}")


@tasks.loop(minutes=10)
async def monitor_oil_prices():
    """Background task that monitors oil prices and sends updates."""
    try:
        # Fetch current price data
        price_data = fetch_oil_prices()
        if not price_data:
            logger.warning("Failed to fetch price data in monitoring loop")
            return
        
        current_price = price_data['price']
        current_cycle = price_data['cycle']
        
        # Get state from database
        state = db.get_state()
        threshold = state['oil_price_threshold']
        last_cycle = state['last_cycle']
        
        # Update price info in database
        db.update_price_info(current_cycle, current_price)
        
        # Check if this is a new cycle
        is_new_cycle = last_cycle is None or current_cycle != last_cycle
        
        if not is_new_cycle:
            logger.debug(f"Still on cycle {current_cycle}, skipping update")
            return
        
        # Get the channel to post updates
        channel_id = DISCORD_CHANNEL_ID
        if not channel_id:
            logger.warning("DISCORD_CHANNEL_ID not set, cannot send updates")
            return
        
        try:
            channel = bot.get_channel(int(channel_id))
            if not channel:
                logger.error(f"Could not find channel with ID {channel_id}")
                return
        except ValueError:
            logger.error(f"Invalid DISCORD_CHANNEL_ID: {channel_id}")
            return
        
        # Check if contract is active
        is_contract_active = db.is_contract_active(current_cycle)
        contract_end_cycle = db.get_contract_end_cycle()
        
        # Determine if price is above or below threshold
        is_above_threshold = current_price >= threshold
        has_been_pinged = db.has_been_pinged()
        
        # Smart alert logic
        should_ping = False
        if not is_above_threshold and not is_contract_active and not has_been_pinged:
            # Price is below threshold, no active contract, and haven't pinged yet
            should_ping = True
            db.set_pinged_state(True)
            logger.info(f"Will ping user - price below threshold for the first time")
        elif is_above_threshold and has_been_pinged:
            # Price went back above threshold, reset ping state
            db.set_pinged_state(False)
            logger.info("Price back above threshold, reset ping state")
        
        # Build status message
        status_icon = "✅" if is_above_threshold else "⚠️"
        status_text = f"Above threshold (${threshold:.2f})" if is_above_threshold else f"Below threshold (${threshold:.2f})"
        
        # Compact status message
        message_parts = [
            f"🛢️ **Cycle {current_cycle}** | **Price: ${current_price:.2f}** | **Status: {status_icon} {status_text}**"
        ]
        
        # Add contract info if active
        if is_contract_active:
            cycles_remaining = contract_end_cycle - current_cycle
            message_parts.append(f"📝 Contract active: {cycles_remaining} cycles remaining (ends cycle {contract_end_cycle})")
        
        # Add ping if needed
        user_id = state['user_id_to_ping']
        if should_ping and user_id:
            message = f"<@{user_id}>\n" + "\n".join(message_parts)
        else:
            message = "\n".join(message_parts)
        
        # Send the message
        await channel.send(message)
        logger.info(f"Sent cycle update: Cycle {current_cycle}, Price ${current_price:.2f}, Pinged: {should_ping}")
        
    except Exception as e:
        logger.error(f"Error in monitoring loop: {e}", exc_info=True)


@bot.command(name='contract')
async def register_contract(ctx, cycles: int):
    """
    Register a contract to avoid pings for a certain number of cycles.
    Usage: $contract <cycles>
    Example: $contract 52
    """
    try:
        if cycles <= 0:
            await ctx.send("❌ Number of cycles must be positive.")
            return
        
        # Fetch current oil price and cycle
        price_data = fetch_oil_prices()
        if not price_data:
            await ctx.send("❌ Failed to fetch current oil price data. Please try again later.")
            return
        
        current_cycle = price_data['cycle']
        contract_end_cycle = current_cycle + cycles
        
        # Update database
        db.set_contract(contract_end_cycle)
        db.update_price_info(current_cycle, price_data['price'])
        
        # Send confirmation
        embed = discord.Embed(
            title="✅ Contract Registered!",
            description=f"You won't be pinged until cycle {contract_end_cycle} ({cycles} cycles from now)",
            color=discord.Color.green()
        )
        embed.add_field(name="Current Cycle", value=str(current_cycle), inline=True)
        embed.add_field(name="Contract End Cycle", value=str(contract_end_cycle), inline=True)
        embed.add_field(name="Cycles Remaining", value=str(cycles), inline=True)
        embed.set_footer(text="Airline Club Oil Price Bot")
        
        await ctx.send(embed=embed)
        logger.info(f"Contract registered by {ctx.author}: {cycles} cycles until cycle {contract_end_cycle}")
        
    except ValueError:
        await ctx.send("❌ Invalid number of cycles. Please provide a valid integer.")
    except Exception as e:
        logger.error(f"Error in register_contract: {e}")
        await ctx.send("❌ An error occurred while registering the contract.")


@bot.command(name='status')
async def show_status(ctx):
    """
    Show current oil price, cycle, and contract status.
    Usage: $status
    """
    try:
        # Fetch current oil price and cycle
        price_data = fetch_oil_prices()
        if not price_data:
            await ctx.send("❌ Failed to fetch current oil price data. Please try again later.")
            return
        
        current_price = price_data['price']
        current_cycle = price_data['cycle']
        
        # Get state from database
        state = db.get_state()
        contract_end_cycle = state['contract_end_cycle']
        threshold = state['oil_price_threshold']
        interval = state['check_interval_minutes']
        
        # Create status embed
        embed = discord.Embed(
            title="🛢️ Oil Price Status",
            color=discord.Color.blue()
        )
        embed.add_field(name="Current Cycle", value=str(current_cycle), inline=True)
        embed.add_field(name="Current Price", value=f"${current_price:.2f}", inline=True)
        embed.add_field(name="Threshold", value=f"${threshold:.2f}", inline=True)
        embed.add_field(name="Check Interval", value=f"{interval} minutes", inline=True)
        
        # Add contract information if active
        if contract_end_cycle is not None and current_cycle < contract_end_cycle:
            cycles_remaining = contract_end_cycle - current_cycle
            embed.add_field(
                name="Contract Status",
                value=f"✅ Active until cycle {contract_end_cycle} ({cycles_remaining} cycles remaining)",
                inline=False
            )
        else:
            embed.add_field(
                name="Contract Status",
                value="❌ No active contract",
                inline=False
            )
        
        # Price status indicator
        if current_price < threshold:
            price_status = f"⚠️ Below threshold (by ${threshold - current_price:.2f})"
        else:
            price_status = f"✅ Above threshold (by ${current_price - threshold:.2f})"
        
        embed.add_field(name="Price Status", value=price_status, inline=False)
        
        # Example compact status message
        status_icon = "✅" if current_price >= threshold else "⚠️"
        example = f"🛢️ Cycle {current_cycle} | Price: ${current_price:.2f} | Status: {status_icon}"
        if contract_end_cycle and current_cycle < contract_end_cycle:
            example += f" | Contract expires: Cycle {contract_end_cycle}"
        embed.add_field(name="Compact Status Example", value=example, inline=False)
        
        embed.set_footer(text="Airline Club Oil Price Bot")
        
        await ctx.send(embed=embed)
        logger.info(f"Status requested by {ctx.author}")
        
    except Exception as e:
        logger.error(f"Error in show_status: {e}")
        await ctx.send("❌ An error occurred while fetching status.")


@bot.command(name='clear')
async def clear_contract(ctx):
    """
    Clear any active contract.
    Usage: $clear
    """
    try:
        state = db.get_state()
        had_contract = state['contract_end_cycle'] is not None
        
        db.clear_contract()
        
        if had_contract:
            embed = discord.Embed(
                title="✅ Contract Cleared",
                description="Your contract has been removed. You will now receive price alerts normally.",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="ℹ️ No Active Contract",
                description="You don't have an active contract to clear.",
                color=discord.Color.blue()
            )
        
        embed.set_footer(text="Airline Club Oil Price Bot")
        await ctx.send(embed=embed)
        logger.info(f"Contract cleared by {ctx.author}")
        
    except Exception as e:
        logger.error(f"Error in clear_contract: {e}")
        await ctx.send("❌ An error occurred while clearing the contract.")


@bot.command(name='threshold')
async def set_threshold(ctx, price: float):
    """
    Set alert threshold price.
    Usage: $threshold <price>
    Example: $threshold 60
    """
    try:
        if price <= 0:
            await ctx.send("❌ Threshold price must be positive.")
            return
        
        db.set_threshold(price)
        
        embed = discord.Embed(
            title="✅ Threshold Updated",
            description=f"Alert threshold has been set to **${price:.2f}**",
            color=discord.Color.green()
        )
        embed.add_field(
            name="What this means",
            value=f"You will be alerted when oil price drops below ${price:.2f}",
            inline=False
        )
        embed.set_footer(text="Airline Club Oil Price Bot")
        
        await ctx.send(embed=embed)
        logger.info(f"Threshold set to ${price:.2f} by {ctx.author}")
        
    except ValueError:
        await ctx.send("❌ Invalid price. Please provide a valid number.")
    except Exception as e:
        logger.error(f"Error in set_threshold: {e}")
        await ctx.send("❌ An error occurred while setting the threshold.")


@bot.command(name='interval')
async def set_interval(ctx, minutes: int):
    """
    Set check interval in minutes.
    Usage: $interval <minutes>
    Example: $interval 5
    """
    try:
        if minutes < 1:
            await ctx.send("❌ Interval must be at least 1 minute.")
            return
        
        if minutes > 60:
            await ctx.send("⚠️ Warning: Setting interval to more than 60 minutes may result in missing price changes.")
        
        db.set_interval(minutes)
        
        # Restart monitoring loop with new interval
        if monitor_oil_prices.is_running():
            monitor_oil_prices.cancel()
        monitor_oil_prices.change_interval(minutes=minutes)
        monitor_oil_prices.start()
        
        embed = discord.Embed(
            title="✅ Check Interval Updated",
            description=f"Bot will now check prices every **{minutes} minute(s)**",
            color=discord.Color.green()
        )
        embed.add_field(
            name="What this means",
            value=f"The bot will poll the API every {minutes} minute(s) for new price data",
            inline=False
        )
        embed.set_footer(text="Airline Club Oil Price Bot")
        
        await ctx.send(embed=embed)
        logger.info(f"Check interval set to {minutes} minutes by {ctx.author}")
        
    except ValueError:
        await ctx.send("❌ Invalid interval. Please provide a valid integer.")
    except Exception as e:
        logger.error(f"Error in set_interval: {e}")
        await ctx.send("❌ An error occurred while setting the interval.")


@bot.command(name='help')
async def show_help(ctx):
    """
    Show available commands and their usage.
    Usage: $help
    """
    embed = discord.Embed(
        title="🤖 Oil Price Bot Commands",
        description="AWS-hosted bot for 24/7 oil price monitoring",
        color=discord.Color.gold()
    )
    
    embed.add_field(
        name="$contract <cycles>",
        value="Register a contract to pause alerts for specified cycles.\n"
              "Example: `$contract 52`",
        inline=False
    )
    
    embed.add_field(
        name="$status",
        value="Show current oil price, cycle, threshold, and contract status.\n"
              "Example: `$status`",
        inline=False
    )
    
    embed.add_field(
        name="$clear",
        value="Clear any active contract and resume normal alerts.\n"
              "Example: `$clear`",
        inline=False
    )
    
    embed.add_field(
        name="$threshold <price>",
        value="Set the alert threshold price (default: $55).\n"
              "Example: `$threshold 60`",
        inline=False
    )
    
    embed.add_field(
        name="$interval <minutes>",
        value="Set how often to check prices (default: 10 minutes).\n"
              "Example: `$interval 5`",
        inline=False
    )
    
    embed.add_field(
        name="$help",
        value="Show this help message.\n"
              "Example: `$help`",
        inline=False
    )
    
    embed.set_footer(text="Airline Club Oil Price Bot | Running on AWS")
    await ctx.send(embed=embed)
    logger.info(f"Help requested by {ctx.author}")


def main():
    """Main execution function."""
    logger.info("Starting AWS-Hosted Oil Price Discord Bot")
    
    # Validate configuration
    if not DISCORD_BOT_TOKEN:
        logger.error("DISCORD_BOT_TOKEN environment variable is not set")
        sys.exit(1)
    
    if not DISCORD_CHANNEL_ID:
        logger.error("DISCORD_CHANNEL_ID environment variable is not set")
        logger.error("The bot needs a channel ID to post automatic updates")
        sys.exit(1)
    
    if not DISCORD_USER_ID:
        logger.warning("DISCORD_USER_ID not set. Bot will not ping users in alerts.")
    
    logger.info(f"Configuration loaded:")
    logger.info(f"  - API URL: {API_URL}")
    logger.info(f"  - Default Threshold: ${DEFAULT_THRESHOLD}")
    logger.info(f"  - Default Interval: {DEFAULT_INTERVAL} minutes")
    logger.info(f"  - Channel ID: {DISCORD_CHANNEL_ID}")
    
    # Run the bot
    try:
        bot.run(DISCORD_BOT_TOKEN)
    except discord.LoginFailure:
        logger.error("Invalid bot token. Please check your DISCORD_BOT_TOKEN.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
