from pdf_utils import load_pdf_from_path, extract_pdf_pages
from chunking import chunk_pages_with_parents
from retrieval import (
    OUTDOOR_WEIGHTED_KEYWORDS,
    CLIMATE_WEIGHTED_KEYWORDS,
    ENERGY_WEIGHTED_KEYWORDS,
    OUTDOOR_BONUS_GROUPS,
    CLIMATE_BONUS_GROUPS,
    ENERGY_BONUS_GROUPS,
    retrieve_top_parent_chunks
)
from rubrics import OUTDOOR_RUBRIC, CLIMATE_RUBRIC, ENERGY_RUBRIC
from scoring import build_prompt, call_model_json


def score_fmp_pdf(pdf_path: str):
    pdf_bytes = load_pdf_from_path(pdf_path)
    pages = extract_pdf_pages(pdf_bytes)
    chunks = chunk_pages_with_parents(pages)

    outdoor_chunks = retrieve_top_parent_chunks(
        chunks,
        OUTDOOR_WEIGHTED_KEYWORDS,
        top_k=8,
        bonus_groups=OUTDOOR_BONUS_GROUPS
    )
    climate_chunks = retrieve_top_parent_chunks(
        chunks,
        CLIMATE_WEIGHTED_KEYWORDS,
        top_k=8,
        bonus_groups=CLIMATE_BONUS_GROUPS
    )
    energy_chunks = retrieve_top_parent_chunks(
        chunks,
        ENERGY_WEIGHTED_KEYWORDS,
        top_k=8,
        bonus_groups=ENERGY_BONUS_GROUPS
    )

    outdoor = call_model_json(
        build_prompt(
            section_name="Outdoor Spaces and Campus Greening",
            rubric_text=OUTDOOR_RUBRIC,
            selected_chunks=outdoor_chunks,
            allow_zero=False
        )
    )

    climate = call_model_json(
        build_prompt(
            section_name="Climate Risk and Mitigation",
            rubric_text=CLIMATE_RUBRIC,
            selected_chunks=climate_chunks,
            allow_zero=True
        )
    )

    energy = call_model_json(
        build_prompt(
            section_name="Energy Efficiency and Resilience",
            rubric_text=ENERGY_RUBRIC,
            selected_chunks=energy_chunks,
            allow_zero=False
        )
    )

    total_score = int(outdoor["score"]) + int(climate["score"]) + int(energy["score"])

    return {
        "mode": "parent_context",
        "outdoor": outdoor,
        "climate": climate,
        "energy": energy,
        "total_score": total_score,
        "num_pages": len(pages),
        "num_child_chunks": len(chunks),
        "retrieved_chunks": {
            "outdoor": outdoor_chunks,
            "climate": climate_chunks,
            "energy": energy_chunks
        }
    }
