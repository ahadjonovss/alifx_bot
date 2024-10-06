import os
from telegram import Update
from telegram.ext import ConversationHandler, MessageHandler, filters, CommandHandler

from lib.short_commands.newversion.android import generate_android_log
from lib.short_commands.newversion.ios import generate_ios_log

# Define states for the new version conversation
VERSION_INPUT, NEWVERSION_INPUT, ADD_MORE_CHANGES, NEWVERSION_CONFIRMATION = range(4)


# Auto-generate What's New function


# /newversion command: Step 1 - Ask for version number
async def newversion_start(update: Update, context):
    await update.message.reply_text("What is the version number?")
    return VERSION_INPUT


# /newversion: Step 2 - Ask for new version changes
async def version_received(update: Update, context):
    context.user_data['version'] = update.message.text  # Store the version number
    await update.message.reply_text("What changes did you make for the new version?")
    return NEWVERSION_INPUT


# /newversion: Step 3 - Confirm changes and ask for more changes or finish
async def newversion_received(update: Update, context):
    if 'newversion' not in context.user_data:
        context.user_data['newversion'] = []

    # Append the new change
    context.user_data['newversion'].append(update.message.text)

    # Joining changes outside of the f-string to avoid syntax errors
    changes = "\n".join(context.user_data['newversion'])

    await update.message.reply_text(
        f"Got it! The changes you've added are:\n\n{changes}\n\nDo you want to add more changes or finish? (Type 'add' to add more changes or 'finish' to complete the log.)"
    )

    return ADD_MORE_CHANGES


# /newversion: Step 4 - Handle adding more changes or finishing the new version log
async def add_more_changes(update: Update, context):
    if update.message.text.lower() == 'add':
        await update.message.reply_text("What additional changes would you like to add?")
        return NEWVERSION_INPUT  # Go back to input changes
    elif update.message.text.lower() == 'finish':
        # Ask for confirmation
        newversion_changes = "\n".join(context.user_data['newversion'])
        await update.message.reply_text(
            f"Is that correct?\n\nYour changes:\n{newversion_changes}\n\nReply 'yes' to confirm or 'no' to modify."
        )
        return NEWVERSION_CONFIRMATION
    else:
        await update.message.reply_text(
            "Invalid input. Please type 'add' to add more changes or 'finish' to finalize the log.")
        return ADD_MORE_CHANGES  # Stay in the same state for further input


# /newversion: Step 5 - Confirm and generate new version logs for both platforms
async def newversion_confirmation(update: Update, context):
    if update.message.text.lower() == 'yes':
        newversion = "\n".join(context.user_data['newversion'])
        version = context.user_data.get('version', '1.0')  # Get the version number
        await update.message.reply_text(f"🔄Generation is in process...")
        # Generate logs for both platforms
        ios_log_output = await generate_ios_log(version, newversion, update)
        android_log_output = ''
        if len(ios_log_output) > 500:
            android_log_output = await generate_android_log(ios_log_output, update)
        else:
            android_log_output = ios_log_output

        if ios_log_output:
            await update.message.reply_text(f"Here's your Ios log:")
            await update.message.reply_text(ios_log_output)

        if android_log_output:
            await update.message.reply_text(f"Here's your Android log:")
            await update.message.reply_text(android_log_output)

        await update.message.reply_text("Thank you! The new version logs have been created.")
    else:
        await update.message.reply_text("Let's try again with the /newversion command.")
    return ConversationHandler.END


async def handle_auto_generation_response(update: Update, version: str, changes: str):
    """
    Automatically generates 'What's New' texts for both iOS and Android platforms using GPT.

    Args:
    - version (str): The version number for the release.
    - changes (str): The changes made in the current version.

    Returns:
    - dict: A dictionary containing 'whats_new_ios' and 'whats_new_android' strings.
    """
    try:
        await update.message.reply_text(f"🔄Generation is in process...")
        # Call the iOS method to generate 'What's New' for iOS
        whats_new_ios = await generate_ios_log(version, changes, update)
    except Exception as e:
        print(f"Error generating iOS What's New: {e}")
        whats_new_ios = "Error generating iOS 'What's New'. Please try again later."

    try:
        whats_new_android = ''
        if len(whats_new_ios) > 500:
            whats_new_android = await generate_android_log(whats_new_ios, update)
        else:
            whats_new_android = whats_new_ios

    except Exception as e:
        print(f"Error generating Android What's New: {e}")
        whats_new_android = "Error generating Android 'What's New'. Please try again later."

    # Return the generated texts as a dictionary
    return {
        'whats_new_ios': whats_new_ios,
        'whats_new_android': whats_new_android
    }


# Cancel the conversation
async def cancel(update: Update, context):
    await update.message.reply_text('Operation canceled.')
    return ConversationHandler.END


# Conversation handler for /newversion
newversion_handler = ConversationHandler(
    entry_points=[CommandHandler('newversion', newversion_start)],
    states={
        VERSION_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, version_received)],
        NEWVERSION_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, newversion_received)],
        ADD_MORE_CHANGES: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_more_changes)],
        NEWVERSION_CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, newversion_confirmation)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
