"""
Main entry point for Division 2 Elevator Bot.
Loads configuration and starts the bot.
"""

import sys
import logging
import argparse
import yaml
from pathlib import Path

from elevator_bot import ElevatorBot


def setup_logging(log_level: str = "INFO", log_file: str = None):
    """
    Setup logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file to write logs to
    """
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def load_config(config_path: str = "config.yaml") -> dict:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to config file

    Returns:
        Configuration dictionary
    """
    config_file = Path(config_path)

    if not config_file.exists():
        logging.error(f"Config file not found: {config_path}")
        sys.exit(1)

    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    logging.info(f"Loaded configuration from {config_path}")
    return config


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Division 2 Elevator Bot - Accessibility Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run with default config
  python main.py --debug            # Run in debug mode
  python main.py --config my.yaml   # Use custom config file

Controls:
  Ctrl+C                            # Stop the bot

This bot is designed for accessibility purposes to assist disabled players.
        """
    )

    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode with visualization'
    )

    parser.add_argument(
        '--log-file',
        type=str,
        help='Optional log file path'
    )

    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level, args.log_file)

    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("Division 2 Elevator Bot")
    logger.info("Accessibility Automation Tool")
    logger.info("=" * 60)

    # Load configuration
    try:
        config = load_config(args.config)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)

    # Override debug setting if command line flag is set
    if args.debug:
        config['debug']['enabled'] = True
        logger.info("Debug mode enabled")

    # Create and start bot
    try:
        logger.info("Initializing bot...")
        bot = ElevatorBot(config)

        logger.info("Bot initialized successfully")
        logger.info("Press Ctrl+C to stop the bot")
        logger.info("-" * 60)

        # Start the bot
        bot.start()

    except KeyboardInterrupt:
        logger.info("\nBot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

    logger.info("Bot shutdown complete")


if __name__ == "__main__":
    main()
