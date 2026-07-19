

import json
from tools.references.refdata import ReferenceComponent

remove = (ReferenceComponent.URL_ABSTRACT, ReferenceComponent.URL_DIRECT)   # We did not test for these.
COMPONENTS = [str(c) for c in ReferenceComponent if c not in remove]

def gen_result(response):
    result = dict.fromkeys(["model", "style"] + ["REFERENCE"] + list(COMPONENTS))
    result["model"], result["style"] = response["model"], response["citation_style"]
    return result

# This script makes this data:
# - <refID>_answer.json 
# - <refID>_accuracy.json 
# - <refID>_confidence.json
# - <refID>_reasoning.json

# maybe to include if needed
# - citation_mutations      Mutations applied to a given reference 
# - citation_components     Components within a given reference (final styled, presented to LLM)
# - citation_severities     Calculated severity levels of a styled reference (by it's combined mutations)

dataset, ref_responses = None, None
with open("set.json", "r") as f: 
    dataset = json.load(f)
with open("all.json", "r") as f: 
    ref_responses = json.load(f)

# Arrangement of results (to be easily csv'd):
# { ref: [{ model:<model>, style:<style>, <criteria>:<accuracy> }] }

log_errored = []

OUTDIR = "./out"

for refID, responses in ref_responses.items():
    errored = False
    answer, accuracy, confidence, reasoning = [[None]*len(responses) for i in range(4)]
    for i, response in enumerate(responses):
        answer[i], accuracy[i], confidence[i], reasoning[i] = [gen_result(response) for i in range(4)]
        # For each reference component
        for component in COMPONENTS:
            try:
                answer[i][component] = response["content"][component]["validity"]
                accuracy[i][component] = response["content"][component]["validity"] == dataset[refID]["mut_severity"]["component"][component][0] if dataset[refID]["mut_severity"]["component"][component] else None  # If this is NULL, then the component never existed within the source reference or by a mutation.
                confidence[i][component] = response["content"][component]["validity_confidence"]
                reasoning[i][component] = response["content"][component]["reasoning"]
            except Exception as e: 
                errored = True
                offender = f"{refID}_{response["model"]}"
                print(f"{offender} has a malformed or missing response for component '{component}': ", e)
                if offender not in log_errored: log_errored.append(offender)
        # A entire reference
        try:
            answer[i]["REFERENCE"] = response["content"]["REFERENCE"]["validity"]
            accuracy[i]["REFERENCE"] = response["content"]["REFERENCE"]["validity"] == dataset[refID]["mut_severity"]["holistic"]["format"][response["citation_style"]]["score"][0]
            confidence[i]["REFERENCE"] = response["content"]["REFERENCE"]["validity_confidence"]
            reasoning[i]["REFERENCE"] = response["content"]["REFERENCE"]["reasoning"]
        except Exception as e: 
            errored = True
            offender = f"{refID}_{response["model"]}"
            print(f"{offender} has a malformed or missing response for holistic 'REFERENCE' criterion: ", e)
            if offender not in log_errored: log_errored.append(offender)

    outdir = OUTDIR
    if errored: outdir += "/errored"

    with open(f"{outdir}/{refID}_answer.json", "x") as f:
        json.dump(answer, f, indent=2)
    with open(f"{outdir}/{refID}_accuracy.json", "x") as f:
        json.dump(accuracy, f, indent=2)
    with open(f"{outdir}/{refID}_confidence.json", "x") as f:
        json.dump(confidence, f, indent=2)
    with open(f"{outdir}/{refID}_reasoning.json", "x") as f:
        json.dump(reasoning, f, indent=2)

print("Total Errored: ", f"{len(log_errored)}/{len(ref_responses)}")
print(*[f" - {e}\n" for e in log_errored], sep="")
