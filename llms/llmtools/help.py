
import json

# General Script Functions

def log(*messages, t="log"):
    # Can redirect these to a file later.
    messages = " ".join([str(m) for m in messages])
    if t in ("log", "l"):
        print(f">> {messages}")
    elif t in ("sup", "s"):
        print(f"||  {messages}")
    elif t in ("err", "e"):
        print(f"!! {messages}")
    else:
        print(f"{t}{messages}")

def write_json(data, filename, access="w"):
    with open(filename, access) as file:
        try: json.dump(data, file, indent=2)
        except:
            log(f"JSON conversion failed\n\n{e}\n, writing plaintext...", t="e")
            file.write(data)
