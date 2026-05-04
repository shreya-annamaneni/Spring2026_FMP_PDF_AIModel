import json
import re
from openai import OpenAI
from config import OPENAI_API_KEY, MODEL_NAME

client = OpenAI(api_key=OPENAI_API_KEY)


def build_prompt(section_name: str, rubric_text: str, selected_chunks, allow_zero: bool = False):
    chunk_text = "\n\n".join(
        [
            f"{c['chunk_id']} | pages {c['start_page']}-{c['end_page']} | retrieval_score={c.get('retrieval_score', 0)}\n{c['text']}"
            for c in selected_chunks
        ]
    )

    score_range = "0,1,2,3,4" if allow_zero else "1,2,3,4"

    return f"""
You are scoring one section of a California school district Facilities Master Plan.

SECTION:
{section_name}

RUBRIC:
{rubric_text}

OBJECTIVITY RULES:
- Use only the provided text chunks.
- Synthesize across all provided chunks before assigning a score.
- Do not assume anything that is not clearly supported by the text.
- Be conservative with vague aspirational language.
- Broad mission language alone does not count as strong evidence.
- Passing mention should score lower than developed planning.
- Districtwide data, concrete strategies, and repeated integration across the plan should score higher.
- If evidence is thin, generic, or unclear, choose the lower reasonable score.

OUTPUT RULES:
- Return valid JSON only.
- Do not include markdown or code fences.
- Use double quotes for all JSON strings.
- Escape any quotes inside strings.
- Keep evidence_text short and paraphrased.
- Do not copy long quotations from the document.
- Keep reasoning to 2-4 short sentences.

TASK:
1. Read all chunks for this section.
2. Assign one score from: {score_range}
3. Cite the strongest evidence across the chunks.
4. Explain why the overall evidence fits the rubric.
5. Explain what is missing for the next higher score. If already at the top score, return "N/A".

Return exactly this JSON:
{{
  "section": "{section_name}",
  "score": 0,
  "confidence": "low",
  "reasoning": "Short explanation of why this score fits the rubric.",
  "evidence": [
    {{
      "chunk_id": "chunk_1",
      "pages": "1-2",
      "evidence_text": "Short paraphrase only"
    }}
  ],
  "missing_for_next_score": "What would be needed for the next higher score, or N/A if already at the maximum."
}}

TEXT CHUNKS:
{chunk_text}
""".strip()


def clean_json_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```json", "", text).strip()
    text = re.sub(r"^```", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    return text


def try_parse_json(text: str):
    return json.loads(clean_json_text(text))


def repair_json_with_model(bad_output: str) -> dict:
    repair_prompt = f"""
Convert the following malformed output into valid JSON only.
Do not change the meaning.
Do not add markdown fences.

Malformed output:
{bad_output}
""".strip()

    response = client.responses.create(
        model=MODEL_NAME,
        input=repair_prompt
    )

    repaired_text = clean_json_text(response.output_text)
    return json.loads(repaired_text)


def call_model_json(prompt: str):
    response = client.responses.create(
        model=MODEL_NAME,
        input=prompt
    )

    raw_text = response.output_text

    try:
        return try_parse_json(raw_text)
    except json.JSONDecodeError:
        return repair_json_with_model(raw_text)