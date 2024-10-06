from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler
from lib.gpt import send_to_gpt

# Define states for the conversation
CHANGELOG_INPUT, CHANGELOG_CONFIRMATION, NEWVERSION_INPUT, NEWVERSION_CONFIRMATION = range(4)


# Start Command Handler
async def start(update: Update, context):
    await update.message.reply_text(
        "Hello! I'm a changelog bot. You can use /changelog or /newversion short_commands to create version logs.")


# /changelog command: Step 1 - Ask for version changes
async def changelog_start(update: Update, context):
    await update.message.reply_text("What changes did you make in this version?")
    return CHANGELOG_INPUT


# /changelog: Step 2 - Confirm changes
async def changelog_received(update: Update, context):
    context.user_data['changelog'] = update.message.text
    await update.message.reply_text(
        f"Got it! You made the following changes:\n\n{update.message.text}\n\nIs this correct? (yes/no)")
    return CHANGELOG_CONFIRMATION


# /changelog: Step 3 - Confirm and generate changelog
async def changelog_confirmation(update: Update, context):
    if update.message.text.lower() == 'yes':
        changelog = context.user_data['changelog']
        prompt = f"Generate a changelog for the following changes: {changelog}"
        changelog_output = await send_to_gpt(prompt, update)
        if changelog_output:
            await update.message.reply_text(f"Here's your changelog:\n\n{changelog_output}")
    else:
        await update.message.reply_text("Let's try again with the /changelog command.")
    return ConversationHandler.END


# /newversion command: Step 1 - Ask for new version changes
async def newversion_start(update: Update, context):
    await update.message.reply_text("What changes did you make for the new version?")
    return NEWVERSION_INPUT


# /newversion: Step 2 - Confirm changes
async def newversion_received(update: Update, context):
    context.user_data['newversion'] = update.message.text
    await update.message.reply_text(
        f"Got it! The changes for the new version are:\n\n{update.message.text}\n\nIs this correct? (yes/no)")
    return NEWVERSION_CONFIRMATION


# /newversion: Step 3 - Confirm and generate new version log
async def newversion_confirmation(update: Update, context):
    if update.message.text.lower() == 'yes':
        newversion = context.user_data['newversion']
        prompt = f"Generate a log for the new version with the following changes: {newversion}"
        newversion_output = await send_to_gpt(prompt, update)
        if newversion_output:
            await update.message.reply_text(f"Here's your new version log:\n\n{newversion_output}")
    else:
        await update.message.reply_text("Let's try again with the /newversion command.")
    return ConversationHandler.END


# Cancel the conversation
async def cancel(update: Update, context):
    await update.message.reply_text('Operation canceled.')
    return ConversationHandler.END


# Conversation handlers for /changelog and /newversion
changelog_handler = ConversationHandler(
    entry_points=[CommandHandler('changelog', changelog_start)],
    states={
        CHANGELOG_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, changelog_received)],
        CHANGELOG_CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, changelog_confirmation)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

newversion_handler = ConversationHandler(
    entry_points=[CommandHandler('newversion', newversion_start)],
    states={
        NEWVERSION_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, newversion_received)],
        NEWVERSION_CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, newversion_confirmation)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
