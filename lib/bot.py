import openai
from telegram.ext import ApplicationBuilder, CommandHandler
from utils import load_keys
from short_commands.changelog import changelog_handler
from short_commands.newversion.general import newversion_handler

# Load keys from the correct path
keys_path = './data/keys'  # Update with the absolute path
keys = load_keys(keys_path)

# Initialize OpenAI API key and Telegram bot token
openai.api_key = keys.get("OPENAI_API_KEY")
telegram_bot_token = keys.get("TELEGRAM_BOT_TOKEN")


def start_bot():
    # Check if API keys are loaded
    if not openai.api_key or not telegram_bot_token:
        print("Error: OpenAI API key or Telegram bot token not set.")
        return

    # Set up the Telegram bot
    app = ApplicationBuilder().token(telegram_bot_token).build()

    # Register handlers
    app.add_handler(CommandHandler("start", lambda update, context: update.message.reply_text(
        "Hello! I'm a changelog bot. You can use /changelog or /newversion short_commands to create version logs.")))
    app.add_handler(changelog_handler)
    app.add_handler(newversion_handler)

    # Start the bot
    print("Bot is running...")
    app.run_polling()
