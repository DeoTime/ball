#!/usr/bin/env python3
"""
Discord Bot for Oil Price Monitoring
Provides commands to manage oil price contracts and check status.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import discord
from discord.ext import commands
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Configuration
API_ENDPOINT = "https://v2.airline-club.com/oil-prices"

# State file path (can be overridden via environment variable)
STATE_FILE = os.getenv('STATE_FILE_PATH', '/tmp/oil_price_bot_state.json')

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents, help_command=None)


def load_state() -> Dict[str, Any]:
    """Load the bot state from file."""
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load state file: {e}")
    return {
        'contract_end_cycle': None,
        'last_alerted_price': None,
        'last_cycle': None,
        'last_price': None
    }


def save_state(state: Dict[str, Any]) -> None:
    """Save the bot state to file."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
        logger.info(f"State saved to {STATE_FILE}")
    except Exception as e:
        logger.error(f"Could not save state file: {e}")


def fetch_oil_prices() -> Optional[Dict[str, Any]]:
    """Fetch current oil prices from the Airline Club API."""
    try:
        logger.info(f"Fetching oil prices from {API_ENDPOINT}")
        response = requests.get(API_ENDPOINT, timeout=10)
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
            'price': current_price,
            'cycle': current_cycle
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch oil prices: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        return None


@bot.event
async def on_ready():
    """Event handler for when the bot is ready."""
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Bot is in {len(bot.guilds)} guild(s)')
    logger.info(f'State file location: {STATE_FILE}')


@bot.event
async def on_command_error(ctx, error):
    """Handle command errors."""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Unknown command. Use `$help` to see available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument. Use `$help` for usage information.")
    else:
        logger.error(f"Command error: {error}")
        await ctx.send(f"❌ An error occurred: {str(error)}")


@bot.command(name='contract')
async def register_contract(ctx, cycles: int):
    """
    Register a contract to avoid pings for a certain number of cycles.
    Usage: $contract <cycles>
    Example: $contract 52
    """
    try:
        # Validate input
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
        
        # Load and update state
        state = load_state()
        state['contract_end_cycle'] = contract_end_cycle
        state['last_cycle'] = current_cycle
        state['last_price'] = price_data['price']
        save_state(state)
        
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
        
        # Load state
        state = load_state()
        contract_end_cycle = state.get('contract_end_cycle')
        threshold = float(os.getenv('OIL_PRICE_THRESHOLD', '55'))
        
        # Create status embed
        embed = discord.Embed(
            title="🛢️ Oil Price Status",
            color=discord.Color.blue()
        )
        embed.add_field(name="Current Cycle", value=str(current_cycle), inline=True)
        embed.add_field(name="Current Price", value=f"${current_price:.2f}", inline=True)
        embed.add_field(name="Price Threshold", value=f"${threshold:.2f}", inline=True)
        
        # Add contract information if active
        if contract_end_cycle is not None and current_cycle < contract_end_cycle:
            cycles_remaining = contract_end_cycle - current_cycle
            embed.add_field(
                name="Contract Status",
                value=f"✅ Active",
                inline=False
            )
            embed.add_field(
                name="Contract Expires",
                value=f"Cycle {contract_end_cycle} ({cycles_remaining} cycles remaining)",
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
        # Load and update state
        state = load_state()
        had_contract = state.get('contract_end_cycle') is not None
        
        state['contract_end_cycle'] = None
        save_state(state)
        
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


@bot.command(name='help')
async def show_help(ctx):
    """
    Show available commands and their usage.
    Usage: $help
    """
    embed = discord.Embed(
        title="🤖 Oil Price Bot Commands",
        description="Manage your oil price monitoring contracts and check status",
        color=discord.Color.gold()
    )
    
    embed.add_field(
        name="$contract <cycles>",
        value="Register a contract to pause alerts for a specified number of cycles.\n"
              "Example: `$contract 52`",
        inline=False
    )
    
    embed.add_field(
        name="$status",
        value="Show current oil price, cycle, and contract status.\n"
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
        name="$help",
        value="Show this help message.\n"
              "Example: `$help`",
        inline=False
    )
    
    embed.set_footer(text="Airline Club Oil Price Bot")
    await ctx.send(embed=embed)
    logger.info(f"Help requested by {ctx.author}")


def main():
    """Main execution function."""
    logger.info("Starting Discord Oil Price Bot")
    
    # Get bot token from environment
    bot_token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not bot_token:
        logger.error("DISCORD_BOT_TOKEN environment variable is not set")
        sys.exit(1)
    
    # Validate other configuration
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    if not webhook_url:
        logger.warning("DISCORD_WEBHOOK_URL not set. Monitoring alerts may not work.")
    
    threshold = os.getenv('OIL_PRICE_THRESHOLD', '55')
    logger.info(f"Configuration: threshold=${threshold}, state_file={STATE_FILE}")
    
    # Run the bot
    try:
        bot.run(bot_token)
    except discord.LoginFailure:
        logger.error("Invalid bot token. Please check your DISCORD_BOT_TOKEN.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
