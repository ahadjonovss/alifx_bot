import os


def load_example_whats_new():
    example_path = os.path.join('data', 'whatsnew')  # Adjust path as necessary
    try:
        with open(example_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return "Example changelog not found."


def generate_new_version_prompt(charCount,changes,version):
    example = load_example_whats_new()
    return (
        f"Generate a changelog for version {version} with these changes: {changes}. "
        f"Follow the style of the provided example: {example}. The total character count must be under {charCount}. Every changes"
        f"must be provided with short description like examole and must say thanks in the end."
        "Ensure the format starts and ends like the example. Keep it simple, do not add any extra words and opinions "
        "and don't mix the data from the changes with the example.But response must start and and like example. "
        "Emojis are allowed on the left side"
    )