# short_commands/newversion/android.py
from gpt import send_to_gpt

from lib.short_commands.newversion.generator import generate_new_version_prompt


async def generate_ios_log(version, changes, update):
    prompt = generate_new_version_prompt(4000,changes,version)
    return await send_to_gpt(prompt, update)
