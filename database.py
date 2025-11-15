#!/usr/bin/env python3
"""
SQLite Database Handler for Oil Price Bot
Manages persistent state for the Discord bot.
"""

import sqlite3
import logging
from typing import Optional, Dict, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class BotDatabase:
    """Handles all database operations for the oil price bot."""
    
    def __init__(self, db_path: str = "bot_data.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize database schema."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create state table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bot_state (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    last_pinged_below_threshold BOOLEAN DEFAULT 0,
                    contract_end_cycle INTEGER,
                    oil_price_threshold REAL DEFAULT 55.0,
                    check_interval_minutes INTEGER DEFAULT 10,
                    user_id_to_ping TEXT,
                    last_cycle INTEGER,
                    last_price REAL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert default state if not exists
            cursor.execute("""
                INSERT OR IGNORE INTO bot_state (id) VALUES (1)
            """)
            
            logger.info(f"Database initialized at {self.db_path}")
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current bot state."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bot_state WHERE id = 1")
            row = cursor.fetchone()
            
            if row:
                return {
                    'last_pinged_below_threshold': bool(row['last_pinged_below_threshold']),
                    'contract_end_cycle': row['contract_end_cycle'],
                    'oil_price_threshold': row['oil_price_threshold'],
                    'check_interval_minutes': row['check_interval_minutes'],
                    'user_id_to_ping': row['user_id_to_ping'],
                    'last_cycle': row['last_cycle'],
                    'last_price': row['last_price']
                }
            
            # Return defaults if no state found
            return {
                'last_pinged_below_threshold': False,
                'contract_end_cycle': None,
                'oil_price_threshold': 55.0,
                'check_interval_minutes': 10,
                'user_id_to_ping': None,
                'last_cycle': None,
                'last_price': None
            }
    
    def update_state(self, **kwargs):
        """Update bot state with provided fields."""
        if not kwargs:
            return
        
        # Build SET clause
        set_parts = []
        values = []
        for key, value in kwargs.items():
            set_parts.append(f"{key} = ?")
            values.append(value)
        
        # Add timestamp update
        set_parts.append("last_updated = CURRENT_TIMESTAMP")
        
        query = f"UPDATE bot_state SET {', '.join(set_parts)} WHERE id = 1"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            logger.debug(f"Updated state: {kwargs}")
    
    def set_contract(self, end_cycle: int):
        """Set a contract end cycle."""
        self.update_state(contract_end_cycle=end_cycle)
        logger.info(f"Contract set to end at cycle {end_cycle}")
    
    def clear_contract(self):
        """Clear any active contract."""
        self.update_state(contract_end_cycle=None)
        logger.info("Contract cleared")
    
    def get_contract_end_cycle(self) -> Optional[int]:
        """Get the contract end cycle if one is active."""
        state = self.get_state()
        return state['contract_end_cycle']
    
    def set_threshold(self, threshold: float):
        """Set the oil price threshold."""
        self.update_state(oil_price_threshold=threshold)
        logger.info(f"Threshold set to ${threshold:.2f}")
    
    def get_threshold(self) -> float:
        """Get the current threshold."""
        state = self.get_state()
        return state['oil_price_threshold']
    
    def set_interval(self, minutes: int):
        """Set the check interval in minutes."""
        self.update_state(check_interval_minutes=minutes)
        logger.info(f"Check interval set to {minutes} minutes")
    
    def get_interval(self) -> int:
        """Get the check interval in minutes."""
        state = self.get_state()
        return state['check_interval_minutes']
    
    def set_user_id(self, user_id: str):
        """Set the user ID to ping."""
        self.update_state(user_id_to_ping=user_id)
        logger.info(f"User ID set to {user_id}")
    
    def get_user_id(self) -> Optional[str]:
        """Get the user ID to ping."""
        state = self.get_state()
        return state['user_id_to_ping']
    
    def update_price_info(self, cycle: int, price: float):
        """Update the last known cycle and price."""
        self.update_state(last_cycle=cycle, last_price=price)
    
    def set_pinged_state(self, pinged: bool):
        """Set whether we've pinged for current below-threshold condition."""
        self.update_state(last_pinged_below_threshold=pinged)
    
    def has_been_pinged(self) -> bool:
        """Check if user has been pinged for current below-threshold condition."""
        state = self.get_state()
        return state['last_pinged_below_threshold']
    
    def is_contract_active(self, current_cycle: int) -> bool:
        """Check if a contract is currently active."""
        end_cycle = self.get_contract_end_cycle()
        if end_cycle is None:
            return False
        return current_cycle < end_cycle
