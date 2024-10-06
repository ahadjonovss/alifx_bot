import os
from telegram import Update
from telegram.ext import ConversationHandler, MessageHandler, filters, CommandHandler
from gpt import send_to_gpt
from short_commands.newversion.general import handle_auto_generation_response

# Define states for the changelog conversation
VERSION_INPUT, CHANGELOG_INPUT, CHANGELOG_CONFIRMATION, ADD_MORE_CHANGES, AUTO_GENERATE = range(5)


# Function to load example changelog from a file
def load_example_changelog():
    example_path = os.path.join('data', 'changelog')  # Adjust path as necessary
    try:
        with open(example_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return "Example changelog not found."


# /changelog command: Step 1 - Ask for version number
async def changelog_start(update: Update, context):
    await update.message.reply_text("What is the version number?")
    return VERSION_INPUT


# /changelog: Step 2 - Ask for version changes
async def version_received(update: Update, context):
    context.user_data['version'] = update.message.text
    await update.message.reply_text("What changes did you make in this version?")
    return CHANGELOG_INPUT


# /changelog: Step 3 - Confirm changes
async def changelog_received(update: Update, context):
    # Initialize the changelog list if not already present
    if 'changelog' not in context.user_data:
        context.user_data['changelog'] = ""

    # Append the new changes to the existing changelog
    context.user_data['changelog'] += f"\n- {update.message.text}"

    await update.message.reply_text(
        f"Got it! For version {context.user_data['version']}, you made the following changes:\n\n{context.user_data['changelog']}\n\nDo you want to add more changes or finish? (send 'add' to add more changes or 'finish' to complete the changelog.)"
    )
    return ADD_MORE_CHANGES


# /changelog: Step 4 - Handle adding more changes or finishing the changelog
async def add_more_changes(update: Update, context):
    if update.message.text.lower() == 'add':
        await update.message.reply_text("What additional changes would you like to add?")
        return CHANGELOG_INPUT  # Go back to input changes
    elif update.message.text.lower() == 'finish':
        # Ask for confirmation
        await update.message.reply_text(
            f"Is that correct?\n\nYour changes:\n{context.user_data['changelog']}\n\nYour version: {context.user_data['version']}\n\nReply 'yes' to confirm or 'no' to modify."
        )
        return CHANGELOG_CONFIRMATION
    else:
        await update.message.reply_text(
            "Invalid input. Please send 'add' to add changes or 'finish' to finalize the changelog."
        )
        return ADD_MORE_CHANGES  # Stay in the same state for further input


# /changelog: Step 5 - Confirm and create the changelog
async def changelog_confirmation(update: Update, context):
    if update.message.text.lower() == 'yes':
        await update.message.reply_text("Creating changelog is in process...")
        # Generate the changelog using GPT
        changelog = context.user_data['changelog']
        version = context.user_data['version']
        example_changelog = load_example_changelog()  # Load the example changelog
        prompt = f"Generate a changelog for version {version} with the following changes:\n\n{changelog}\n\nHere is an example of a changelog:\n\n{example_changelog}"

        changelog_output = await send_to_gpt(prompt, update)
        if changelog_output:
            await update.message.reply_text(f"Here's your changelog:\n\n{changelog_output}")
        else:
            await update.message.reply_text(
                "Sorry, there was an error generating the changelog. Please try again later."
            )

        # Ask if user wants to auto-generate "What's New" text
        await update.message.reply_text("Do you want to auto-generate 'What's New' text? (yes/no)")
        return AUTO_GENERATE  # Transition to the auto-generation state
    else:
        await update.message.reply_text("Let's try again with the /changelog command.")
        return ConversationHandler.END


# Handle the "What's New" text auto-generation after generating the changelog
async def auto_generate_whats_new(update: Update, context):
    if update.message.text.lower() == 'yes':
        version = context.user_data['version']
        changes = context.user_data['changelog'].splitlines()  # Split changes into a list if needed

        # Call the method from newversion to generate "What's New" text
        whats_new_output = await handle_auto_generation_response(update,version, changes)
        if whats_new_output:
            await update.message.reply_text(f"Here's your 'What's New' texts:")
            await update.message.reply_text(whats_new_output['whats_new_ios'])
            await update.message.reply_text(whats_new_output['whats_new_android'])
            await update.message.reply_text("Let's try again with the /newversion command.")
        else:
            await update.message.reply_text("There was an error generating 'What's New' text. Please try again later.")
    else:
        await update.message.reply_text("No problem! If you need anything else, just type /changelog.")

    return ConversationHandler.END


# Cancel the conversation
async def cancel(update: Update, context):
    await update.message.reply_text('Operation canceled.')
    return ConversationHandler.END


# Conversation handler for /changelog
changelog_handler = ConversationHandler(
    entry_points=[CommandHandler('changelog', changelog_start)],
    states={
        VERSION_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, version_received)],
        CHANGELOG_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, changelog_received)],
        CHANGELOG_CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, changelog_confirmation)],
        ADD_MORE_CHANGES: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_more_changes)],
        AUTO_GENERATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, auto_generate_whats_new)],  # Use auto-generation
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
