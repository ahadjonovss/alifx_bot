import logging
from bot import start_bot

if __name__ == "__main__":
    # Log all errors
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    start_bot()
