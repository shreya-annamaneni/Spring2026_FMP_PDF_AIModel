from config import CHUNK_PAGES, CHUNK_OVERLAP


def format_pages_text(pages):
    return "\n".join(
        [f"[Page {p['page_num']}] {p['text']}" for p in pages if p["text"]]
    ).strip()


def chunk_pages(pages, chunk_pages_n=CHUNK_PAGES, overlap=CHUNK_OVERLAP):
    chunks = []
    step = max(1, chunk_pages_n - overlap)

    for start_idx in range(0, len(pages), step):
        selected = pages[start_idx:start_idx + chunk_pages_n]
        if not selected:
            continue

        text = format_pages_text(selected)

        if not text:
            continue

        chunks.append({
            "chunk_id": f"chunk_{len(chunks)+1}",
            "start_page": selected[0]["page_num"],
            "end_page": selected[-1]["page_num"],
            "text": text
        })

    return chunks


def chunk_pages_with_parents(
    pages,
    child_pages=CHUNK_PAGES,
    child_overlap=CHUNK_OVERLAP,
    parent_radius=3
):
    chunks = []
    step = max(1, child_pages - child_overlap)

    for start_idx in range(0, len(pages), step):
        child = pages[start_idx:start_idx + child_pages]
        if not child:
            continue

        child_text = format_pages_text(child)
        if not child_text:
            continue

        parent_start_idx = max(0, start_idx - parent_radius)
        parent_end_idx = min(len(pages), start_idx + child_pages + parent_radius)
        parent = pages[parent_start_idx:parent_end_idx]
        parent_text = format_pages_text(parent)

        chunks.append({
            "chunk_id": f"chunk_{len(chunks)+1}",
            "child_start_page": child[0]["page_num"],
            "child_end_page": child[-1]["page_num"],
            "child_text": child_text,
            "parent_start_page": parent[0]["page_num"],
            "parent_end_page": parent[-1]["page_num"],
            "parent_text": parent_text
        })

    return chunks
