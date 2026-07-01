from schemas import ProtoSchemas
from orouterapi import openrouter, parse_response, trytryagain
import json
import time

# Groundwork for scaling.

# Testing two references against two models. 
# Save results into matrix.

# ! To @consider: should files be references and columns models, or vice versa? What is our z?

if __name__ == "__main__":
    refs = [
        "Penner M, Zwaigenbaum L, Piroddi N, Park S, Minhas RS, Singal D. Advances in supporting development in autistic children and youth. BMJ. 2026;393:e086562. Published 2026 Jun 10. doi:10.1136/bmj-2025-086562",
        "Volk, R. J., Lewis, K. B., Smith, M., Carley, M., Barry, M. J., Bekker, H. L., H\u00e4rter, M., Hoffmann, T., McCaffery, K., Pignone, M., Steffensen, K. D., Sepucha, K., Thompson, R., Trevena, L., van der Weijden, T., Witteman, H. O., & Stacey, D. (2026). Updated International Patient Decision Aid Standards (IPDAS version 5.0): modified Delphi, evidence informed consensus process. BMJ (Clinical research ed.), 393, e088116. https://doi.org/10.1136/bmj-2025-088116"
    ]
    models = [
        "nvidia/nemotron-3-super-120b-a12b:free",
        "openai/gpt-oss-20b:free"
    ]

    # Classify all components. Will trim this according to per reference specifics at some point (avoid confusion / forced hallucination)
    classify = {
        "author":       ProtoSchemas.realfakeconfidence("the author list"),
        "author_order": ProtoSchemas.realfakeconfidence("the order of the author list"),
        "title":        ProtoSchemas.realfakeconfidence("the article title"),
        "journal":      ProtoSchemas.realfakeconfidence("the journal"),
        "vol":          ProtoSchemas.realfakeconfidence("the journal volume"),
        "iss":          ProtoSchemas.realfakeconfidence("the journal issue"),
        "page":         ProtoSchemas.realfakeconfidence("the page number"),
        "elocator":     ProtoSchemas.realfakeconfidence("the elocator"),
        "date":         ProtoSchemas.realfakeconfidence("the publishing date"),
        "doi":          ProtoSchemas.realfakeconfidence("the doi"),
        "pmid":         ProtoSchemas.realfakeconfidence("the pmid"),
        "pmcid":        ProtoSchemas.realfakeconfidence("the pmcid"),
        "REFERENCE":    ProtoSchemas.realfakeconfidence("the reference")
    }
    schema = ProtoSchemas.make_schema(classify)

    responses = []
    data = []
    for i, ref in enumerate(refs):
        print(f"starting reference {i}")
        data.append({ "reference": ref })
        for model in models:
            print(f"starting model {model}")
            r = parse_response(trytryagain(openrouter, {"model": model, "ref": ref, "schema": schema}))   # Call openrouter, retry three times if code != 200, then parse into {request, response_text, response_json, content} dict.
            responses.append(r)
            data[i][model] = r["content"]
            print("done")
            time.sleep(1)

    with open("multiout_responses.json", "w") as file:
        try: json.dump(responses, file, indent=2)
        except: file.write(responses)

    with open("multiout_data.json", "w") as file:
        try: json.dump(data, file, indent=2)
        except: file.write(data)





