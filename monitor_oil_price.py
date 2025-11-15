#!/usr/bin/env python3
"""
Oil Price Monitor for Airline Club
Monitors oil prices and sends Discord notifications when prices drop below threshold.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Configuration
API_ENDPOINT = "https://v2.airline-club.com/oil-prices"

# State file to track last alert and contracts
# Can be overridden via environment variable to share with Discord bot
STATE_FILE = os.getenv('STATE_FILE_PATH', '/tmp/oil_price_bot_state.json')


def load_state() -> Dict[str, Any]:
    """Load the last alerted state from file."""
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
    """Save the current state to file."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        logger.error(f"Could not save state file: {e}")


def fetch_oil_prices() -> Optional[list]:
    """Fetch oil prices from the Airline Club API."""
    try:
        logger.info(f"Fetching oil prices from {API_ENDPOINT}")
        response = requests.get(API_ENDPOINT, timeout=10)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Successfully fetched {len(data)} price entries")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch oil prices: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        return None


def send_discord_notification(
    webhook_url: str,
    user_id: str,
    price: float,
    cycle: int,
    threshold: float
) -> bool:
    """Send a Discord notification via webhook."""
    try:
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        # Create the message with user ping
        message = {
            "content": f"<@{user_id}>",
            "embeds": [{
                "title": "⚠️ Oil Price Alert!",
                "description": f"Oil price has dropped below your threshold!",
                "color": 15158332,  # Red color
                "fields": [
                    {
                        "name": "Current Price",
                        "value": f"${price:.2f}",
                        "inline": True
                    },
                    {
                        "name": "Threshold",
                        "value": f"${threshold:.2f}",
                        "inline": True
                    },
                    {
                        "name": "Cycle",
                        "value": str(cycle),
                        "inline": True
                    },
                    {
                        "name": "Timestamp",
                        "value": timestamp,
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "Airline Club Oil Price Monitor"
                }
            }]
        }
        
        logger.info(f"Sending Discord notification for price ${price:.2f}")
        response = requests.post(
            webhook_url,
            json=message,
            timeout=10
        )
        response.raise_for_status()
        logger.info("Discord notification sent successfully")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Discord notification: {e}")
        return False


def is_contract_active(current_cycle: int, state: Dict[str, Any]) -> bool:
    """Check if a contract is currently active."""
    contract_end_cycle = state.get('contract_end_cycle')
    
    if contract_end_cycle is None:
        return False
    
    return current_cycle < contract_end_cycle


def should_alert(current_price: float, current_cycle: int, threshold: float, state: Dict[str, Any]) -> bool:
    """Determine if an alert should be sent."""
    # Check if contract is active
    if is_contract_active(current_cycle, state):
        contract_end_cycle = state.get('contract_end_cycle')
        cycles_remaining = contract_end_cycle - current_cycle
        logger.info(f"Contract is active until cycle {contract_end_cycle} ({cycles_remaining} cycles remaining), suppressing alert")
        return False
    
    last_alerted_price = state.get('last_alerted_price')
    
    # Alert if price is below threshold
    if current_price >= threshold:
        logger.info(f"Price ${current_price:.2f} is above threshold ${threshold:.2f}, no alert needed")
        return False
    
    # If we've never alerted, send alert
    if last_alerted_price is None:
        logger.info(f"First time below threshold, sending alert")
        return True
    
    # If price has dropped further since last alert, send new alert
    if current_price < last_alerted_price:
        logger.info(f"Price has dropped from ${last_alerted_price:.2f} to ${current_price:.2f}, sending alert")
        return True
    
    # If price was below threshold and stayed below, don't spam
    logger.info(f"Price ${current_price:.2f} still below threshold but no significant change from last alert")
    return False


def main():
    """Main execution function."""
    logger.info("Starting Oil Price Monitor")
    
    # Get configuration from environment variables
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    user_id = os.getenv('DISCORD_USER_ID')
    threshold_str = os.getenv('OIL_PRICE_THRESHOLD', '55')
    
    # Validate configuration
    if not webhook_url:
        logger.error("DISCORD_WEBHOOK_URL environment variable is not set")
        sys.exit(1)
    
    if not user_id:
        logger.error("DISCORD_USER_ID environment variable is not set")
        sys.exit(1)
    
    try:
        threshold = float(threshold_str)
    except ValueError:
        logger.error(f"Invalid OIL_PRICE_THRESHOLD value: {threshold_str}")
        sys.exit(1)
    
    logger.info(f"Configuration: threshold=${threshold:.2f}")
    
    # Load previous state
    state = load_state()
    
    # Fetch current oil prices
    price_data = fetch_oil_prices()
    if not price_data:
        logger.error("Failed to fetch oil prices, exiting")
        sys.exit(1)
    
    if not isinstance(price_data, list) or len(price_data) == 0:
        logger.error("Invalid or empty price data received")
        sys.exit(1)
    
    # Get the most recent price (last item in the array)
    latest_entry = price_data[-1]
    current_price = latest_entry.get('price')
    current_cycle = latest_entry.get('cycle')
    
    if current_price is None or current_cycle is None:
        logger.error("Invalid price data format")
        sys.exit(1)
    
    logger.info(f"Latest price: ${current_price:.2f} (cycle {current_cycle})")
    
    # Update last known price and cycle in state
    state['last_price'] = current_price
    state['last_cycle'] = current_cycle
    
    # Check if we should send an alert
    if should_alert(current_price, current_cycle, threshold, state):
        success = send_discord_notification(
            webhook_url,
            user_id,
            current_price,
            current_cycle,
            threshold
        )
        
        if success:
            # Update state with the price we just alerted about
            state['last_alerted_price'] = current_price
            state['last_alerted_cycle'] = current_cycle
            state['last_alerted_timestamp'] = datetime.utcnow().isoformat()
            save_state(state)
            logger.info("State updated successfully")
    else:
        # If price is back above threshold, clear the last alerted price
        if current_price >= threshold and state.get('last_alerted_price') is not None:
            logger.info("Price is back above threshold, clearing alert state")
            state['last_alerted_price'] = None
        # Save state to persist last_price and last_cycle
        save_state(state)
    
    logger.info("Oil Price Monitor completed successfully")


if __name__ == "__main__":
    main()
