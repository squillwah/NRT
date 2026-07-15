import json
import random
from enum import StrEnum
from tools.references.refdata import ReferenceComponent
    
# PMC Citing Medicine Guide
# https://www.ncbi.nlm.nih.gov/books/NBK7256/

# Vancouver / NLM
# PubMed
# AMA                                # Standards
# ICMJE                              # AMA
# Nature                             # Vancouver
# Cell Press                         # NLM
# Science (AAAS)                     # APA
# PNAS                               
# Elsevier Vancouver                 # Journal Variations
# Springer Nature                    # Nature
# Wiley                              # Science
# eLife                              # Elsevier
# Oxford University Press            # Springer
# ACS (biochemistry journals)
# IEEE

class FormatStyle(StrEnum):
    APA = "apa"
    HARVARD = "harvard"
    VANCOUVER = "vancouver"
    #ELSEVIER  = "elsevier",
    #NATURE    = "nature",
    #OXFORD    = "oxford",
    #SPRINGER  = "springer",
    #CSE       = "cse",

class CitationElement(StrEnum):
    AUTHORS          = "authors"
    TITLE            = "title"
    JOURNAL_NAME     = "journal_name"
    PUBLICATION_DATE = "publication_date"
    JOURNAL_META     = "journal_meta"   # Comprises volume, issue, pages/elocator
    IDENTIFIERS      = "identifiers"    # DOI or other database IDs

check_none = lambda e, end: f"{e}{end}" if e else "" # To not include anything if component is ommitted.

# Functions which build each element of a citation. Configurable.
class ElementBuilder: 
    def authors(authors, *, etal, etal_apa=False, etal_harvard=False, etal_threshold, delim_authors, delim_initials, delim_lastfirst, initialize, initialize_periods, penultimate_and):       # Some lasts will already be initialized, but may lack periods.
        if authors is None or len(authors) == 0: return None     # Checks for omission mutations

        names = [(a["l"], a["f"]) for a in authors]
        ea = etal_threshold is not None and len(names) > etal_threshold
        if ea: names = names[:etal_threshold] + ([names[-1]] if etal_apa else []) # APA etal mode appends the absolute final author.
        # Transform 'names' into list of author name strings as configured.
        for i, (last, firsts) in enumerate(names):
            if initialize and firsts:    # Not all have first names to be initialized.
                firsts = [i[0].upper()+("." if initialize_periods else "") for i in firsts.split()] # Will we ever get empty from split?    #@TODO Sometimes author lastnames are hyphened, so split at hyphen?
                firsts = delim_initials.join(firsts)
            names[i] = delim_lastfirst.join((last, firsts)) if firsts else last     # Condition avoids trailing ' ' when no first names.
        # Etalify 
        if len(names) > 1:
            if penultimate_and and not ea:
                names = delim_authors.join(names[:-1]) + penultimate_and + names[-1]
            elif ea:
                if etal_apa: names = delim_authors.join(names[:-1]) + etal + names[-1]  # Smith, J., ... Jane, M.
                elif etal_harvard: names = names[0] + etal  # <first only> et al
                else: names = delim_authors.join(names) + etal
            else:
                names = delim_authors.join(names)
        else: names = names[0]
        return names

    def title(title, quotes):
        if title is None or not title: return None

        return f"'{title}'" if quotes else title

    def journal_name(names, abbreviate):
        if names is None: return None
        
        return names["short"] if abbreviate else names["full"]

    def journal_meta(vol, iss, page, elocator, styler):
        if all(m is None for m in (vol, iss, page, elocator)): return None

        return styler(vol=vol, iss=iss, page=page, elocator=elocator)  # "stylers" are fstring template functions

    def publication_date(pub, epub, styler):   
        if all(d is None for d in (pub, epub)): return None

        return styler(pub=pub, epub=epub)

    def identifiers(doi, pmid, pmcid, styler): 
        if all(i is None for i in (doi, pmid, pmcid)): return None

        return styler(doi=doi, pmid=pmid, pmcid=pmcid)
   
    # Wrappers around builder methods for unified interface associated with element type constants.
    _ELEMENT_MAP = {
        CitationElement.TITLE:            lambda ref, conf: ElementBuilder.title(ref["title"], **conf),
        CitationElement.AUTHORS:          lambda ref, conf: ElementBuilder.authors(ref["authors"], **conf),
        CitationElement.JOURNAL_NAME:     lambda ref, conf: ElementBuilder.journal_name(ref["journal"]["name"], **conf),
        CitationElement.JOURNAL_META:     lambda ref, conf: ElementBuilder.journal_meta(vol=ref["journal"]["volume"], iss=ref["journal"]["issue"], page=ref["journal"]["page"], elocator=ref["journal"]["elocator"], **conf),
        CitationElement.PUBLICATION_DATE: lambda ref, conf: ElementBuilder.publication_date(pub=ref["pub"], epub=ref["epub"], **conf),   # Might be cleaner to nest pub/epub under 'date' instead of flat. Same with identifiers? who cares
        CitationElement.IDENTIFIERS:      lambda ref, conf: ElementBuilder.identifiers(doi=ref["doi"], pmid=ref["pmid"], pmcid=ref["pmcid"], **conf)
    }
   
    # Returns reference to lambdas which call builder functions.
    @classmethod
    def build(cls, element): 
        return cls._ELEMENT_MAP[element]

class Formats:
    # Citations consist of the six CitationElements.
    # ElementBuilder constructs elements, given the reference data source and a builder configuration dict.

    # Formats uses ElementBuilder to create elements configured for a given format. 
    # Formats.ElementStylers are used to customize some ElementBuilder components in place of a config dict. They're basically fstring templates, with some extra conditions for missing components.

    # _LAYOUT defines where how and which CitationElements are included within a particular citation format.
    # _STYLE_CONFIG defines the ElementBuilder configs and stylers to apply to each component for a particular format.

    class ElementStylers:
        # Helper for {y:2015 m:12 d:25} -> 2015 Dec 25
        _MONTHS = { 1:  "Jan", 2:  "Feb", 3:  "Mar",
                    4:  "Apr", 5:  "May", 6:  "Jun",
                    7:  "Jul", 8:  "Aug", 9:  "Sep",
                    10: "Oct", 11: "Nov", 12: "Dec" }
        @classmethod
        def _monthify_date(cls, date):
            styled = ""
            if date["y"]:
                styled = str(date["y"])
                if date["m"]:
                    styled += " " + cls._MONTHS[date["m"]]
                    if date["d"]:
                        styled += " " + str(date["d"])
            return styled
        
        # Vancouver Stylers
        # vol(iss):<page/elocator>
        def vancouver_journal_meta(**metadata):
            vol, iss, page, elocator = [metadata[part] for part in ("vol", "iss", "page", "elocator")]
            styled = ""
            styled += str(vol) if vol else ""
            styled += f"({iss})" if iss else ""
            if page["start"] and page["end"]:
                styled += f":{page["start"]}-{page["end"]}"
            elif page["start"] or page["end"]:
                styled += f":{page["start"] if page["start"] else page["end"]}"
            if elocator:
                styled += f":{elocator}"
            return styled if styled else None   # ! Return None when styled elements are empty. This signals not to include anything (avoiding double periods and strangeness)
        # year month day
        @classmethod
        def vancouver_publication_date(cls, **pubdates):
            pub, epub = [pubdates[p] for p in ("pub", "epub")]
            date = pub if pub["y"] else epub
            date = cls._monthify_date(date)
            return date if date else None
        def vancouver_identifiers(**idents):
            doi = idents["doi"]
            return f"Available from: doi:{doi["prefix"]}/{doi["suffix"]}" if doi else None# Maybe vancouver just shouldn't do DOI? Or it should do URLs instead? Variation needed...
       
        # APA Stylers
        # vol(iss), <page/elocator>
        def apa_journal_meta(**metadata):
            vol, iss, page, elocator = [metadata[part] for part in ("vol", "iss", "page", "elocator")]
            styled = ""
            styled += str(vol) if vol else ""
            styled += f"({iss})" if iss else ""
            if page["start"] and page["end"]:
                styled += f", {page["start"]}-{page["end"]}"
            elif page["start"] or page["end"]:
                styled += f", {page["start"] if page["start"] else page["end"]}"
            if elocator:
                styled += f", {elocator}"
            return styled if styled else None
        # (year)
        def apa_publication_date(**pubdates):
            pub, epub = [pubdates[p] for p in ("pub", "epub")]
            return f"({pub["y"]})" if pub["y"] else f"({epub["y"]})" if epub["y"] else None
        def apa_identifiers(**idents):
            doi = idents["doi"] # We've never encountered a reference without a DOI in the RIS. How would this break if it's absent?
            return f"https://doi.org/{doi["prefix"]}/{doi["suffix"]}" if doi is not None else None

        # Harvard Stylers
        # vol(iss), pp. <page-page>
        def harvard_journal_meta(**metadata):
            vol, iss, page, elocator = [metadata[part] for part in ("vol", "iss", "page", "elocator")]
            styled = ""
            styled += str(vol) if vol else ""
            styled += f"({iss})" if iss else ""
            if page["start"] and page["end"]:
                styled += f", pp. {page["start"]}-{page["end"]}"
            elif page["start"] or page["end"]:
                styled += f", pp. {page["start"] if page["start"] else page["end"]}"
            if elocator:
                styled += f", article {elocator}"
            return styled if styled else None
        @classmethod
        def harvard_publication_date(cls, **pubdates):
            pub, epub = [pubdates[p] for p in ("pub", "epub")]
            date = pub if pub["y"] else epub
            date = cls._monthify_date(date)
            return f"({date})" if date else None
        def harvard_identifiers(**idents):
            doi = idents["doi"] # We've never encountered a reference without a DOI in the RIS. How would this break if it's absent?
            return f"Available at: doi:{doi["prefix"]}/{doi["suffix"]}" if doi else None

    # Ordering/combining of rendered citation elements      # This is probabaly where the omission checking would come in?
    def _layout_vancouver(authors, title, journal_name, publication_date, journal_meta, identifiers):   # ! Argument names should match CitationElement strings (so unwrapped CitationElement: "element" dicts can be used)
        # authors. title. jname. pubdate;jmeta. identifiers
        au = check_none(authors, ". ") 
        ti = check_none(title, ". ")
        jn = check_none(journal_name, ". ")             # return f"{H(authors, ". ")}{H(title, ". ")}{H(journal_name, ". ")}{H(publication_date, ";")}{H(journal_meta, ". ")}{H(identifiers, "")}"
        pd = check_none(publication_date, ";")
        jm = check_none(journal_meta, ". ")
        ids = check_none(identifiers, "")
        return au+ti+jn+pd+jm+ids
    
    def _layout_apa(authors, title, journal_name, publication_date, journal_meta, identifiers):
        # authors pubdate. title. jname, jmeta. identifiers
        au = check_none(authors, " ") 
        ti = check_none(title, ". ")
        jn = check_none(journal_name, ", ")
        pd = check_none(publication_date, ". ")
        jm = check_none(journal_meta, ". ")
        ids = check_none(identifiers, "")
        return au+pd+ti+jn+jm+ids
    
    def _layout_harvard(authors, title, journal_name, publication_date, journal_meta, identifiers):
        # authors. pubdate title, jname, jmeta. identifiers.
        
        au = check_none(authors, ". ") 
        ti = check_none(title, ". ")
        jn = check_none(journal_name, ", ")
        pd = check_none(publication_date, " ")
        jm = check_none(journal_meta, ". ")
        ids = check_none(identifiers, ".")
        return au+pd+ti+jn+jm+ids
    #return f"{authors} {publication_date}. {title}. {journal_name}, {journal_meta}. {identifiers}"
    
    _LAYOUT = {
        FormatStyle.VANCOUVER: _layout_vancouver,
        FormatStyle.APA: _layout_apa,
        FormatStyle.HARVARD: _layout_harvard
    }

    # Styling configuration of citation elements
    _STYLE_CONFIG = {
        # https://auckland.libguides.com/vancouver/journal-article
        FormatStyle.VANCOUVER: {
            CitationElement.AUTHORS: {
                "etal": ", et al",              # Include comma at start if desired.    ", et al" or " et al"
                "etal_threshold": 6,
                "delim_authors": ", ",
                "delim_initials": "",
                "delim_lastfirst": " ",
                "initialize": True,
                "initialize_periods": False,
                "penultimate_and": "",          # Include comma at start for oxford comma. ", and " or " & " or ", & "  etc.
            },
            CitationElement.TITLE:            { "quotes": False },
            CitationElement.JOURNAL_NAME:     { "abbreviate": True },
            CitationElement.JOURNAL_META:     { "styler": ElementStylers.vancouver_journal_meta },
            CitationElement.PUBLICATION_DATE: { "styler": ElementStylers.vancouver_publication_date },
            CitationElement.IDENTIFIERS:      { "styler": ElementStylers.vancouver_identifiers }
        },
        FormatStyle.APA: {
            CitationElement.AUTHORS: {
                "etal": ", ... ",
                "etal_apa": True,               # Appends ... <final_author> instead of an et al. 
                "etal_threshold": 20,
                "delim_authors": ", ",
                "delim_initials": " ",
                "delim_lastfirst": ", ",
                "initialize": True,
                "initialize_periods": True,
                "penultimate_and": " & ",       # Include comma at start for oxford comma. ", and " or " & " or ", & "  etc.

            },
            CitationElement.TITLE:            { "quotes": False },
            CitationElement.JOURNAL_NAME:     { "abbreviate": False },
            CitationElement.JOURNAL_META:     { "styler": ElementStylers.apa_journal_meta },
            CitationElement.PUBLICATION_DATE: { "styler": ElementStylers.apa_publication_date },
            CitationElement.IDENTIFIERS:      { "styler": ElementStylers.apa_identifiers }
        },
        FormatStyle.HARVARD: {
            CitationElement.AUTHORS: {
                "etal": " et al",
                "etal_harvard": True,           # Cuts the et al down to the first author only.
                "etal_threshold": 3,
                "delim_authors": ", ",
                "delim_initials": "",
                "delim_lastfirst": ", ",
                "initialize": True,
                "initialize_periods": True,
                "penultimate_and": " and ",       # Include comma at start for oxford comma. ", and " or " & " or ", & "  etc.

            },
            CitationElement.TITLE:            { "quotes": True },
            CitationElement.JOURNAL_NAME:     { "abbreviate": False },
            CitationElement.JOURNAL_META:     { "styler": ElementStylers.harvard_journal_meta },
            CitationElement.PUBLICATION_DATE: { "styler": ElementStylers.harvard_publication_date },
            CitationElement.IDENTIFIERS:      { "styler": ElementStylers.harvard_identifiers }
        }
    }

    # Defining which components are present by default inside a given format.
    # Has no effect on the rendering of the format. 
    # Is ANDed database COMPONENTS array, for accurate absent component marking.
    _FORMAT_REFERENCE_COMPONENTS = {
        FormatStyle.VANCOUVER: {
            ReferenceComponent.AUTHORS          : True,
            ReferenceComponent.TITLE            : True,
            ReferenceComponent.JOURNAL_NAME     : True,
            ReferenceComponent.JOURNAL_VOLUME   : True,
            ReferenceComponent.JOURNAL_ISSUE    : True,
            ReferenceComponent.JOURNAL_PAGE     : True,
            ReferenceComponent.ELOCATOR         : True,
            ReferenceComponent.PUBLICATION_DATE : True,
            ReferenceComponent.DOI              : True,
            ReferenceComponent.URL_ABSTRACT     : False,
            ReferenceComponent.URL_DIRECT       : False,
            ReferenceComponent.PMCID            : False,
            ReferenceComponent.PMID             : False
        },
        FormatStyle.APA: {
            ReferenceComponent.AUTHORS          : True,
            ReferenceComponent.TITLE            : True,
            ReferenceComponent.JOURNAL_NAME     : True,
            ReferenceComponent.JOURNAL_VOLUME   : True,
            ReferenceComponent.JOURNAL_ISSUE    : True,
            ReferenceComponent.JOURNAL_PAGE     : True,
            ReferenceComponent.ELOCATOR         : True,
            ReferenceComponent.PUBLICATION_DATE : True,
            ReferenceComponent.DOI              : True,
            ReferenceComponent.URL_ABSTRACT     : False,
            ReferenceComponent.URL_DIRECT       : False,
            ReferenceComponent.PMCID            : False,
            ReferenceComponent.PMID             : False
        },
        FormatStyle.HARVARD: {
            ReferenceComponent.AUTHORS          : True,
            ReferenceComponent.TITLE            : True,
            ReferenceComponent.JOURNAL_NAME     : True,
            ReferenceComponent.JOURNAL_VOLUME   : True,
            ReferenceComponent.JOURNAL_ISSUE    : True,
            ReferenceComponent.JOURNAL_PAGE     : True,
            ReferenceComponent.ELOCATOR         : True,
            ReferenceComponent.PUBLICATION_DATE : True,
            ReferenceComponent.DOI              : True,
            ReferenceComponent.URL_ABSTRACT     : False,
            ReferenceComponent.URL_DIRECT       : False,
            ReferenceComponent.PMCID            : False,
            ReferenceComponent.PMID             : False
        }
    }

    # For omissions, just mark them in the dataset. Make sure to set it false in REFERENCES metacomponent.
    # Omission are handled before this, by setting the ds element to None. Any missing components are caught and not added here.

    # Return dict of formatted reference and bools for the components contained.
    @classmethod
    def build(cls, refdata, has_component, style):
        print(refdata)
        # Build each CitationElement according to style
        elements = {
            element: ElementBuilder.build(element)(refdata, cls._STYLE_CONFIG[style][element]) for element in CitationElement
        }
        # Determine contained components
        has_components = {
            rc: (cls._FORMAT_REFERENCE_COMPONENTS[style][rc] and has_component[rc]) for rc in cls._FORMAT_REFERENCE_COMPONENTS[style]
        }
        # Combine elements according to style
        citation = cls._LAYOUT[style](**elements)

        return {
            "citation": citation,
            "has_component": has_components
        }

    @classmethod
    def build_all(cls, refdata, has_component):
        return {style: cls.build(refdata, has_component, style) for style in FormatStyle}

if __name__ == "__main__":
    import h
    refs = h.read_json("refset.json", intkeys=True)
#    Formats.build(refs[88]["data"], FormatStyle.VANCOUVER)
    #print(Formats.build(refs[88]["data"], FormatStyle.APA))
    #print(Formats.build(refs[88]["data"], FormatStyle.HARVARD))
    #print(Formats.build(refs[88]["data"], FormatStyle.VANCOUVER))
    print()
    print(Formats.build_all(refs[88]["data"]))
    for r in refs:
        print(Formats.build_all(refs[r]["data"]))

    #Formats._authorize(ass, **Formats._STYLE_CONFIGS[FormatStyle.VANCOUVER]["authors"])

