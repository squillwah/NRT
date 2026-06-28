
# The structure of our respones.

# What do we want out of our LLMs?
#  - Holistic
#    - Is this references real or fake? (Yes/No)                (Should we use more precise wording? Authentic vs Fabricated, Trustworthy vs Suspicious?) We could do a small trial with each, to see how results compare. @todo: Experiment. 
#    - How real is this reference, as a percentage?             (Kind of same as confidence score. We should be thinking precisely about the wording, how will our framing affect their outputs? Other wordings could be 'how authentic is this reference 0-100', etc.)
#    - What classification does this reference fall under?      (If we're doing the classification thing. Even still, we need to better define them cause Pan's preliminaries are fuzzy.
#  - Component-wise
#    - Is this <component> (authors, title, etc.) real or fake? (Should we use the word 'hallucinated', or does that carry too much baggage?)
#    - How likely is it that this component is real (0-100)?

# This would yield an output of one binary (Y/N) classification and one continuous (%) probability of authenticty for each component and the ref as a whole.        (@Consider: it will be interesting to see how the sum of component-wise classifications/predictions compares to the holistic. Is there consistency or is it all made up?) 

# ! The difference between confidence scores and a real/fake gradient would be to what the value is relating.
# A confidence score would represent how much the LLM thinks it's answer is right (I am 95% confident that my assesment <real/fake> of this <reference/component> is correct!)
# Whereas the ends of a real/fake score would remain consistent between each response (The chance that this <reference/component> is real is 95%.)

# !!! Positive or negative logic? Should we be doing "True"/100% for real, or "True"/100% for fabricated?

# More documentation on structured outputs:
# https://developers.openai.com/api/docs/guides/structured-outputs
# https://json-schema.org/docs

def protoschema_verify(thing):   #, *, override_binary=None, override_continuous=None):     Could do a thing like this if it becomes needed to alter the prompts.
    return {
        "type": "object",
        "properties": {
            "binary": {
                "type": "boolean",
                "description": f"True if {thing} is real."          # Or 'False if this is <fabricated/hallucinated>'?, 'True if this is authentic'? What do we mean by "real"? How much of "real"'s interpretation do we want to leave up to the LLM?          How about just "correct"?
            },
            "continuous": {
                "type": "number",
                "minimum": 0,   # 0-1 avoids confusion of 0.99 vs 99 
                "maximum": 1,
                "description": f"The percent probability that {thing} is real." # Is 'probability' the right framing?
            }
        },
        "required": ["binary", "continuous"],
        "additionalProperties": False
    }
def protoschema_classify(thing):
    return {
        "type": "object",
        "properties": {
            "class": {
                "type": "string",
                "enum": ["Verified", "Metadata Error", "Serious Metadata Error", "Plausible Fabricated", "Needs Human Review"],     # !!! An important question: How much of the JSON schema can the chatbot "see" at once? Will the context of other properties in the schema have an effect? By precedence?
                "description": f"Classification of {thing}."
            },
            "confidence": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": f"Percentage of confidence in the classification of {thing}."
            }
        },
        "required": ["class", "confidence"],
        "additionalProperties": False
    }

# Order of elements in schema follows order of lists and strings in lists.
def gen_schema(verify, classify):
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "citation_validation",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    f"{thing}_v": protoschema_verify(verify[thing]) for thing in verify         # Using thing names as labels.
                } | {
                    f"{thing}_c": protoschema_classify(classify[thing]) for thing in classify
                },
                "required": [f"{thing}_v" for thing in verify] + [f"{thing}_c" for thing in classify],
                "additionalProperties": False
            }
        }
    }

