
# Reference builders

_MONTHMAP = {"01": "Jan", "02": "Feb", "03": "Mar",
             "04": "Apr", "05": "May", "06": "Jun",
             "07": "Jul", "08": "Aug", "09": "Sep",
             "10": "Oct", "11": "Nov", "12": "Dec"}
FORMATS = ("ama", "apa", "mla", "nlm") # @todo: Add more. Journal specific ones.

# Create the author string, formatted in ama, apa, mla, or nlm.
#  Could break this down further into pieces like 'initialize last' and 'etalize' or whatever
def build_ref_authors(author_list, style):
    # Initial spacing, initial period, last/first spacing, et al threshold, et al count, et al spacing, initialize firsts, list ampersand.
    isp, ipe, lfsp, eat, eac, easp, initials, ampersand = "!", "!", "!", 1, 1, "!", False, False
    match style:
        case "ama": isp, ipe, lfsp, eat, eac, easp, initials, ampersand = "",    "",    " ",    7,      3,      ", ",   True,   False
        case "apa": isp, ipe, lfsp, eat, eac, easp, initials, ampersand = " ",   ".",   ", ",   None,   None,   None,   True,   True
        case "mla": isp, ipe, lfsp, eat, eac, easp, initials, ampersand = "",    "",    ", ",   2,      1,      " ",    False,  False
        case "nlm": isp, ipe, lfsp, eat, eac, easp, initials, ampersand = "",    "",    " ",    None,   None,   None,   True,   False
    author_string = ""
    formatted_names = []
    for auth in author_list:
        #last, firsts = (a := auth.split(", ", 1)) + [""]*(2-len(a))    @ FIX cause we split authors at RIS parse now
        last, firsts = auth["l"], auth["f"]
        if initials: firsts = isp.join([c+ipe for c in firsts if c.isupper()])
        formatted_names.append(lfsp.join((last, firsts)).strip())
    if not eat or len(author_list) < eat:
        if ampersand: formatted_names[-1] = "& " + formatted_names[-1]
        author_string = ", ".join(formatted_names)
    else: author_string = ", ".join(formatted_names[0:eac]) + easp + "et al"
    return author_string

# Build a reference in the given style.
# Right now, only AMA matches completely. @todo: even more, looking at journals themselves.
def build_ref(refdata, style):
    authors = build_ref_authors(refdata["authors"], style)
    title = refdata["title"]
    jname = refdata["journal"]["name"]["short"]
    jnamef = refdata["journal"]["name"]["full"]
    jyear = refdata["pub"]["y"]
    jissue = f"{refdata["journal"]["volume"]}({refdata["journal"]["issue"]})"
    jpages = f"{refdata["journal"]["page"]["start"]}-{refdata["journal"]["page"]["end"]}"
    doi = refdata["doi"]

    reference = ""
    match style:
        case "ama": reference = f"{authors}. {title}. {jname}. {jyear};{jissue}:{jpages}. doi:{doi}"
        case "apa": reference = f"{authors}. ({jyear}). {title}. {jnamef}, {jissue}:{jpages}. https://doi.org/{doi}"
        case "mla": reference = f"{authors}. {title}. {jnamef} vol. {jyear};{jissue}:{jpages}. doi:{doi}"
        case "nlm": reference = f"{authors}. {title}. {jname}. {jyear};{jissue}:{jpages}. doi:{doi}"                    # !!! NOTE: Not all RIS data comes with Epub data. In that case, don't incldue it. Do always include both Pub and EPub in nls though.
    return reference

# Builds reference in all styles, returning dict of {reference style : reference string}. 
def bake_formats(ref_data, *, v=False):
    if v: print(f"Baking {len(FORMATS)} reference formats for {ref_data["pmcid"]}...")
    formats = {f: build_ref(ref_data, f) for f in FORMATS}
    return formats





#    print(refs[0]["ama"]["orig"])
#
#    print()
#    bads = []
#    for r, d in zip(refs, refdata):
#        orig = r["ama"]["orig"]
#        reco = build_ref(d, "ama")
#        print(orig)
#        print(reco)
#        print(orig == reco)
#        if (orig != reco): bads.append((orig, reco))
#    print("---")
#    for o, r in bads:
#        print(o)
#        print(r)
#        print()
#        #print(build_ama_authors(d["authors"]))
#
#    print("\n\n\n\n")
#    print((a := refs[0]["ama"]["orig"])[0:a.find("Deviations")])
#    print(build_ref_authors(refdata[0]["authors"], "ama"))
#    print()
#    print((a := refs[0]["apa"]["orig"])[0:a.find("Deviations")])
#    print(build_ref_authors(refdata[0]["authors"], "apa"))
#    print()
#    print((a := refs[0]["mla"]["orig"])[0:a.find("Deviations")])
#    print(build_ref_authors(refdata[0]["authors"], "mla"))
#    print()
#    print((a := refs[0]["nlm"]["orig"])[0:a.find("Deviations")])
#    print(build_ref_authors(refdata[0]["authors"], "nlm"))
#


