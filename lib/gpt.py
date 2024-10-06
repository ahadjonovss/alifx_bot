import openai
import asyncio
from telegram import Update

async def send_to_gpt(prompt: str, update: Update):
    retries = 5  # Number of retries
    delay = 1  # Initial delay in seconds

    for attempt in range(retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message['content']
        except openai.error.RateLimitError:
            if attempt < retries - 1:
                await update.message.reply_text("Rate limit exceeded. Retrying...")
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                await update.message.reply_text("I am currently experiencing high demand. Please try again later.")
                return None
        except Exception as e:
            await update.message.reply_text(f"An error occurred: {str(e)}")
            return None
