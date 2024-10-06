def load_keys(filename):
    keys = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                name, value = line.strip().split('=')
                keys[name] = value
    except FileNotFoundError:
        print(f"Error: The file {filename} was not found.")
    print("Loaded keys:", keys)  # Debug: Print loaded keys
    return keys
