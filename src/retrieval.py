OUTDOOR_KEYWORDS = [
    "outdoor learning",
    "outdoor classroom",
    "schoolyard",
    "greening",
    "green space",
    "shade",
    "shade structure",
    "tree",
    "trees",
    "canopy",
    "garden",
    "rain garden",
    "bioswale",
    "bioswales",
    "stormwater",
    "permeable",
    "landscaping",
    "surface type",
    "grass",
    "asphalt",
    "playground",
    "field",
    "wellness",
    "environmental literacy"
]

OUTDOOR_WEIGHTED_KEYWORDS = {
    "outdoor learning": 4,
    "outdoor classroom": 4,
    "schoolyard greening": 5,
    "tree canopy": 5,
    "canopy cover": 5,
    "urban heat island": 5,
    "heat island": 4,
    "rain garden": 4,
    "bioswale": 4,
    "bioswales": 4,
    "permeable": 3,
    "stormwater": 3,
    "green space": 3,
    "environmental literacy": 3,
    "sustainable landscaping": 3,
    "shade structure": 3,
    "shade": 1,
    "tree": 1,
    "trees": 1,
    "garden": 1,
    "landscaping": 1,
    "playground": 1,
    "field": 1,
    "grass": 1,
    "asphalt": 1,
    "wellness": 1
}

CLIMATE_KEYWORDS = [
    "climate",
    "climate risk",
    "climate resilience",
    "climate readiness",
    "resilience",
    "heat",
    "extreme heat",
    "heat wave",
    "wildfire",
    "wildfire smoke",
    "smoke",
    "flood",
    "flooding",
    "storm",
    "storms",
    "drought",
    "sea level rise",
    "power shutoff",
    "public safety power shutoff",
    "hazard",
    "vulnerable",
    "vulnerability",
    "adaptation",
    "cool roof",
    "air filtration",
    "stormwater",
    "rainwater catchment",
    "defensible space",
    "shade",
    "tree planting",
    "resilience hub"
]

CLIMATE_WEIGHTED_KEYWORDS = {
    "climate resilience": 5,
    "climate readiness": 5,
    "climate risk": 5,
    "extreme heat": 5,
    "heat wave": 4,
    "wildfire smoke": 5,
    "sea level rise": 5,
    "public safety power shutoff": 5,
    "power shutoff": 4,
    "flood risk": 4,
    "flooding": 3,
    "drought": 3,
    "vulnerability": 4,
    "vulnerable": 3,
    "adaptation": 4,
    "mitigation": 3,
    "resilience hub": 4,
    "air filtration": 3,
    "cool roof": 3,
    "defensible space": 3,
    "rainwater catchment": 3,
    "stormwater": 2,
    "climate": 2,
    "resilience": 1,
    "heat": 1,
    "wildfire": 1,
    "smoke": 1,
    "flood": 1,
    "storm": 1,
    "storms": 1,
    "hazard": 1,
    "shade": 1
}

ENERGY_KEYWORDS = [
    "energy",
    "energy efficiency",
    "energy resilience",
    "electrification",
    "decarbonization",
    "title 24",
    "zero net energy",
    "zne",
    "dsa",
    "solar",
    "photovoltaic",
    "battery",
    "storage",
    "microgrid",
    "hvac",
    "heat pump",
    "led",
    "lighting",
    "renewable",
    "natural gas",
    "boiler",
    "electric water heater",
    "induction",
    "utility data",
    "kwh",
    "therms",
    "operating costs",
    "backup power",
    "power outage"
]

ENERGY_WEIGHTED_KEYWORDS = {
    "title 24": 5,
    "zero net energy": 5,
    "zne": 4,
    "electrification": 5,
    "decarbonization": 5,
    "microgrid": 5,
    "battery storage": 5,
    "solar plus storage": 5,
    "energy resilience": 4,
    "energy efficiency": 3,
    "energy use intensity": 5,
    "utility data": 4,
    "kwh": 3,
    "therms": 3,
    "heat pump": 4,
    "renewable": 3,
    "photovoltaic": 3,
    "backup power": 3,
    "power outage": 3,
    "natural gas": 3,
    "electric water heater": 3,
    "induction": 3,
    "operating costs": 2,
    "dsa": 2,
    "solar": 2,
    "battery": 2,
    "storage": 1,
    "hvac": 1,
    "led": 1,
    "lighting": 1,
    "energy": 1,
    "electrical": 1,
    "boiler": 1
}

OUTDOOR_BONUS_GROUPS = [
    ("shade", "heat"),
    ("shade", "outdoor learning"),
    ("tree", "canopy"),
    ("stormwater", "permeable"),
    ("garden", "outdoor classroom")
]

CLIMATE_BONUS_GROUPS = [
    ("extreme heat", "shade"),
    ("flooding", "vulnerable"),
    ("climate", "risk"),
    ("climate", "resilience"),
    ("wildfire", "smoke"),
    ("power shutoff", "resilience")
]

ENERGY_BONUS_GROUPS = [
    ("solar", "battery"),
    ("solar", "resilience"),
    ("title 24", "zero net energy"),
    ("electrification", "decarbonization"),
    ("energy", "operating costs"),
    ("backup power", "power outage")
]


def page_blocks(text):
    blocks = {}
    current_page = None
    current_lines = []

    for line in text.splitlines():
        if line.startswith("[Page "):
            if current_page is not None:
                blocks[current_page] = "\n".join(current_lines).strip()
            page_num = line.split("]", 1)[0].replace("[Page ", "")
            current_page = int(page_num)
            current_lines = [line]
        elif current_page is not None:
            current_lines.append(line)

    if current_page is not None:
        blocks[current_page] = "\n".join(current_lines).strip()

    return blocks


def combine_page_blocks(page_text_by_num):
    return "\n".join(
        page_text_by_num[page_num]
        for page_num in sorted(page_text_by_num)
    ).strip()



def keyword_count(text: str, keywords):
    lower = text.lower()
    total = 0
    for kw in keywords:
        total += lower.count(kw.lower())
    return total


def weighted_keyword_score(text: str, weighted_keywords, bonus_groups=None):
    lower = text.lower()
    matched_terms = {}
    base_score = 0

    for term, weight in weighted_keywords.items():
        count = lower.count(term.lower())
        if count:
            matched_terms[term] = count * weight
            base_score += count * weight

    bonus_score = 0
    for group in bonus_groups or []:
        if all(term.lower() in lower for term in group):
            bonus_score += 3

    matched_weights = [
        weighted_keywords[term]
        for term in matched_terms
    ]
    penalty_score = 0
    if matched_weights and max(matched_weights) <= 1 and len(matched_terms) <= 3:
        penalty_score = 2

    return {
        "retrieval_score": max(0, base_score + bonus_score - penalty_score),
        "base_score": base_score,
        "bonus_score": bonus_score,
        "penalty_score": penalty_score,
        "matched_terms": matched_terms
    }


def retrieve_top_chunks(chunks, keywords, top_k=8):
    scored = []
    for chunk in chunks:
        score = keyword_count(chunk["text"], keywords)
        item = dict(chunk)
        item["retrieval_score"] = score
        scored.append(item)

    scored.sort(key=lambda x: x["retrieval_score"], reverse=True)
    positive = [c for c in scored if c["retrieval_score"] > 0]

    return positive[:top_k] if positive else scored[:top_k]


def merge_parent_chunks(retrieved_chunks):
    if not retrieved_chunks:
        return []

    ordered = sorted(
        retrieved_chunks,
        key=lambda c: (c["parent_start_page"], c["parent_end_page"])
    )
    merged = []

    for chunk in ordered:
        if not merged or chunk["parent_start_page"] > merged[-1]["end_page"] + 1:
            merged.append({
                "chunk_id": f"parent_{len(merged)+1}",
                "start_page": chunk["parent_start_page"],
                "end_page": chunk["parent_end_page"],
                "text": chunk["parent_text"],
                "page_text_by_num": page_blocks(chunk["parent_text"]),
                "retrieval_score": chunk["retrieval_score"],
                "source_child_chunks": [chunk["chunk_id"]],
                "retrieval_diagnostics": [chunk["retrieval_diagnostics"]]
            })
            continue

        current = merged[-1]
        current["end_page"] = max(current["end_page"], chunk["parent_end_page"])
        current["page_text_by_num"].update(page_blocks(chunk["parent_text"]))
        current["text"] = combine_page_blocks(current["page_text_by_num"])
        current["retrieval_score"] += chunk["retrieval_score"]
        current["source_child_chunks"].append(chunk["chunk_id"])
        current["retrieval_diagnostics"].append(chunk["retrieval_diagnostics"])

    for idx, chunk in enumerate(merged, start=1):
        chunk["chunk_id"] = f"parent_{idx}"
        chunk.pop("page_text_by_num", None)

    return merged


def retrieve_top_parent_chunks(
    chunks,
    weighted_keywords,
    top_k=8,
    bonus_groups=None,
    max_parent_chunks=6
):
    scored = []
    for chunk in chunks:
        diagnostics = weighted_keyword_score(
            chunk["child_text"],
            weighted_keywords,
            bonus_groups=bonus_groups
        )
        item = dict(chunk)
        item["retrieval_score"] = diagnostics["retrieval_score"]
        item["retrieval_diagnostics"] = {
            "child_chunk_id": chunk["chunk_id"],
            "child_pages": f"{chunk['child_start_page']}-{chunk['child_end_page']}",
            **diagnostics
        }
        scored.append(item)

    scored.sort(key=lambda x: x["retrieval_score"], reverse=True)
    positive = [c for c in scored if c["retrieval_score"] > 0]
    top_children = positive[:top_k] if positive else scored[:top_k]
    merged = merge_parent_chunks(top_children)
    merged.sort(key=lambda x: x["retrieval_score"], reverse=True)
    return merged[:max_parent_chunks]
