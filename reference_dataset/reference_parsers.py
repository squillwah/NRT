

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

    # Could we use RegEx?

def compose_ama(ref): pass
    # The reverse of decompose

def decompose_apa(ref): pass
def compose_apa(ref): pass

def decompose_mla(ref): pass
def compose_mla(ref): pass

def decompose_nlm(ref): pass
def compose_nlm(ref): pass


#jref = decompose_ama(the_string)
ref = decompose_apa(the_string)

def swap_authors(ref):
    swap(ref["authors"])
    return ref

apa = compose_apa(ref)

def mangle_title(ref, settings):
    for i in range(times):
        introduce_typo(ref["title"], random_point, random_type)
main():
    # 200 single
    for i in 200:
        random_mutation(ref)
    # 300 multi

