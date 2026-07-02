from typing import Any, Dict
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=""
)

schema: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "author": {
            "type": "string",
            "enum": ["Verified", "Metadata Error", "Serious Metadata Error", "Plausible Fabricated", "Needs Human Review"],
            "description": "Verification status of author name(s) and attribution"
        },
        "confidence_author": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "description": "Confidence score (0-100) for the author verification"
        },
        "article_title": {
            "type": "string",
            "enum": ["Verified", "Metadata Error", "Serious Metadata Error", "Plausible Fabricated", "Needs Human Review"],
            "description": "Verification status of article title and attribution"
        },
        "confidence_article_title": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "description": "Confidence score (0-100) for the title verification"
        },
        "journal": {
            "type": "string",
            "enum": ["Verified", "Metadata Error", "Serious Metadata Error", "Plausible Fabricated", "Needs Human Review"],
            "description": "Verification status of the journal name and indexing"
        },
        "confidence_journal": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "description": "Confidence score (0-100) for the journal verification"
        },
        "publish_date": {
            "type": "string",
            "enum": ["Verified", "Metadata Error", "Serious Metadata Error", "Plausible Fabricated", "Needs Human Review"],
            "description": "Verification status of publication date accuracy"
        },
        "confidence_of_the_publish_date": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "description": "Confidence score (0-100) for the citation's publishing date verification"
        },
        "author_order": {
            "type": "string",
            "enum": ["Verified", "Metadata Error", "Serious Metadata Error", "Plausible Fabricated", "Needs Human Review"],
            "description": "Whether the author order matches the original source"
        },
        "confidence_of_the_author_order": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "description": "Confidence score (0-100) for the citation's author order verification"
        },
        "publisher": {
            "type": "string",
            "enum": ["Verified", "Metadata Error", "Serious Metadata Error", "Plausible Fabricated", "Needs Human Review"],
            "description": "Verification status of publisher name and imprint"
        },
        "confidence_of_the_publisher": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "description": "Confidence score (0-100) for the citation's publisher verification"
        },
        "overall": {
            "type": "string",
            "enum": ["Verified", "Metadata Error", "Serious Metadata Error", "Plausible Fabricated", "Needs Human Review"],
            "description": "Overall assessment of the citation's authenticity"
        },
        "confidence_overall": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "description": "Confidence score (0-100) for the overall assessment"
        }
    },
    "required": [
        "overall", "confidence_overall", "author", "journal", "publish_date",
        "author_order", "publisher", "confidence_of_the_publisher",
        "confidence_of_the_author_order", "confidence_journal",
        "confidence_of_the_publish_date", "confidence_author",
        "confidence_article_title", "article_title"
    ],
    "additionalProperties": False
}

prompt = (
    "The date is 2026/06/28. You are a biomedical references verifier. "
    "Assess each component and examine the reference as a whole. "
    "Adhere to the strict structure response JSON schema. \n\n"
    "=== CATEGORIES & DEFINITIONS ===\n"
    "1. Verified: The article exists, and the title plus key metadata match the database record. - Minor formatting differences are acceptable.\n"
    "2. Metadata Error: The article exists, but one or more fields are wrong, incomplete, abbreviated, or formatted differently. - The article can still be confidently identified.\n"
    "3. Serious Metadata error: The title or other major fields are wrong, but the DOI or PMID correctly points to a real article. - Not fabricated if the DOI/PMID identifies a real article.\n"
    "4. Plausible fabricated: The claimed title cannot be matched to any real article after reasonable search. - Real authors, real journals, or plausible topics are not enough to prove the article exists.\n"
    "5. needs human review: The evidence is mixed, weak, or ambiguous. - Use this when there are partial title matches, missing/conflicting DOI or PMID, or multiple possible matches.\n"
    "\n=== CITATION TO VALIDATE ===\n"
    "\n Here is the reference:\n Kearney PM, McCarthy M, Rengarajan S, O'Keeffe LM, Avery K, Chan AW, Devane D, "
    "Davies G, Gale C, Hemkens LG, Juszczak E, Kwakkenbos L, Langan SM, Lugg-Widger F, Moher D, Schmidt M, "
    "Thabane L, Thombs BD, Toader AM, Watkins A, Farrin AJ, Zwarenstein M, Sydes MR, Williamson PR, Markham S. "
    "Reporting of Cohort and Routinely Collected Data in Randomised Controlled Trial Protocols (SPIRIT-ROUTINE): "
    "extension checklist with explanation and elaboration. BMJ. 2026;393:. doi:10.1136/bmj-2025-087095"
)

response = client.responses.create(
    model="openai/gpt-4.1",
    input=prompt,
    tools=[
        {
            "type": "openrouter:web_search",
            "parameters": {
                "engine": "auto",
                "max_results": 3
            }
        }
    ],
    text={
        "format": {
            "type": "json_schema",
            "name": "news_summary",
            "schema": schema,
            "strict": True
        }
    }
)

print(response)
print("\n\n")
print(response.output_text)
