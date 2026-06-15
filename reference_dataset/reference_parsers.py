

# There is the choice between eight functions or two with some format specific argument.
# If the logic overlaps a lot, just two would be more concise.


# Takes reference string and returns some standard representation for versitile mangling.
# Compose does the reverse.

# Alternatively, we could try to use the RIS shit as our standard format, and just build each format from scratch with that.
# We would probably make some subtle mistakes and it'd be hard to match 100% with the real references completely. 

# Global patterns:
# - Authors always first.

# Which parts are irrecoverably different?
# - Et al vs full list

def decompose_ama(ref):
    # Patterns of AMA:
    # - "Authors. Title. Journal. JournalYear;Volume:Page/Elocator. Published Year Mon Da. doi"
    # - All author names listed
    #   - last[full]+SPACE+first[initial]+(COMMA+SPACE+repeat)+PERIOD
    #   - no periods on initials, no spacing between multiple initials
    # 

    # The standard format should be a map something like:
    # {"authors": ["", "", ""], # What to do for et al? A single element list or break convention with a plain string?
    #   "title": "",
    #   "published": "", # Could be broken down further, into month day year
    #   "journal": "",   # Would there be a seperate journal date from publishing date?
    #   "volume": "",
    #   "page": "",
    #   "doi": ""}
    # The tricky part is deciding on a structure which works for all formats, so we don't need to write multiple procedures for each one permutation.

def compose_ama(ref): pass
    # The reverse of decompose

def decompose_apa(ref): pass
def compose_apa(ref): pass

def decompose_mla(ref): pass
def compose_mla(ref): pass

def decompose_nlm(ref): pass
def compose_nlm(ref): pass




