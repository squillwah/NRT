
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
    
    _LOGOUT(f"\n {time.strftime(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))}\n")

def close_log(): 
    global _LOGFILE, _LOGOUT
    if _LOGFILE: 
        log("Closing log file.")
        _LOGOUT = print
        _LOGFILE.close()
        _LOGFILE = None

def log(*messages, delim=" ", t="log"):
    # Can redirect these to a file later.
    messages = delim.join([str(m) for m in messages])
    if t in ("log", "l"):   t = "> "
    elif t in ("sup", "s"): t = "  "
    elif t in ("err", "e"): t = "! "
    elif t in ("hed", "h"): 
        t = "=== "
        messages = messages + " ==="
    
    _LOGOUT(f"[{time.strftime("%H:%M:%S", time.localtime())}] {t}{messages}")

def mkdir(name, timestamp=False):
    #d = Path(f"{name}_{int(time.time())}" if timestamp else name)
    d, i = Path(name), 0
    while d.exists(): 
        i = i + 1
        d = Path(f"{name}{i}")
    d.mkdir()
    return d

def write_json(data, filename, access="w"):
    with open(filename, access, buffering=1) as file:
        try: json.dump(data, file, indent=2)
        except Exception as e:
            log(f"JSON conversion failed\n\n{e}\n, writing plaintext...", t="e")
            file.write(data)

def read_json(filename, intkeys=False):
    data = None
    o_hook = (lambda d: {(int(k) if k.isdigit() else k): v for k, v in d.items()}) if intkeys else None
    with open(f"{filename}", "r") as f: data = json.load(f, object_hook=o_hook)
    return data
