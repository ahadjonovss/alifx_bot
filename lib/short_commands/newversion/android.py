# short_commands/newversion/android.py
from lib.gpt import send_to_gpt
from lib.short_commands.newversion.generator import generate_new_version_prompt


async def generate_android_log(text,update):
    prompt = (
        "Reduce the character count of the text to 500 or fewer without changing its meaning. "
        "Minimize the number of words while ensuring that the starting and ending sections of the text remain "
        "unchanged."
    )

    return await send_to_gpt(prompt, update)
