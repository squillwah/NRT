
import json
import time
from pathlib import Path

# General Script Functions

_LOGFILE = None
_LOGOUT = print

def open_log(filename, keep_print=True):
    global _LOGFILE, _LOGOUT
    _LOGFILE = open(filename, "a", buffering=1)
    writer = lambda msg: _LOGFILE.write(msg+"\n")
    if keep_print: _LOGOUT = lambda msg: [f(msg) for f in (writer, print)]
    else: _LOGOUT = writer

def close_log(): 
    if _LOGFILE: _LOGFILE.close()

def log(*messages, delim=" ", t="log"):
    # Can redirect these to a file later.
    messages = delim.join([str(m) for m in messages])
    if t in ("log", "l"):   t = ">> "
    elif t in ("sup", "s"): t = "|| "
    elif t in ("err", "e"): t = "!! "
    
    _LOGOUT(f"{t}{messages}")

def mkdir(name, timestamp=False):
    d = Path(f"{name}_{int(time.time())}" if timestamp else name)
    d.mkdir()
    return d

def write_json(data, filename, access="w"):
    with open(filename, access) as file:
        try: json.dump(data, file, indent=2)
        except:
            log(f"JSON conversion failed\n\n{e}\n, writing plaintext...", t="e")
            file.write(data)

def read_json(filename):
    data = None
    with open(f"{filename}", "r") as f: data = json.load(f)
    return data
