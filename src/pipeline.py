from pdf_utils import load_pdf_from_path, extract_pdf_pages
from chunking import chunk_pages
from retrieval import (
    OUTDOOR_KEYWORDS,
    CLIMATE_KEYWORDS,
    ENERGY_KEYWORDS,
    retrieve_top_chunks
)
from rubrics import OUTDOOR_RUBRIC, CLIMATE_RUBRIC, ENERGY_RUBRIC
from scoring import build_prompt, call_model_json


def score_fmp_pdf(pdf_path: str):
    pdf_bytes = load_pdf_from_path(pdf_path)
    pages = extract_pdf_pages(pdf_bytes)
    chunks = chunk_pages(pages)

    outdoor_chunks = retrieve_top_chunks(chunks, OUTDOOR_KEYWORDS, top_k=8)
    climate_chunks = retrieve_top_chunks(chunks, CLIMATE_KEYWORDS, top_k=8)
    energy_chunks = retrieve_top_chunks(chunks, ENERGY_KEYWORDS, top_k=8)

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
        "outdoor": outdoor,
        "climate": climate,
        "energy": energy,
        "total_score": total_score,
        "num_pages": len(pages),
        "num_chunks": len(chunks),
        "retrieved_chunks": {
            "outdoor": outdoor_chunks,
            "climate": climate_chunks,
            "energy": energy_chunks
        }
    }