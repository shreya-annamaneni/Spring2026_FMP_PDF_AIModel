import os
import json
import pandas as pd
from pipeline import score_fmp_pdf

TEST_FMPS = [
    {
        "district_name": "Anaheim Elementary",
        "pdf_path": "data/pdfs/AnaheimElementary.pdf",
    },
    {
        "district_name": "Antioch Unified",
        "pdf_path": "data/pdfs/AntiochUnified.pdf",
    },
    {
        "district_name": "Belmont-RedwoodShores Elementary",
        "pdf_path": "data/pdfs/Belmont-RedwoodShoresElementary.pdf",
    },
    {
        "district_name": "Castro Valley Unified",
        "pdf_path": "data/pdfs/CastroValleyUnified.pdf",
    },
    {
        "district_name": "El Dorado Union High",
        "pdf_path": "data/pdfs/ElDoradoUnionHigh.pdf",
    },
    {
        "district_name": "Lompoc Unified",
        "pdf_path": "data/pdfs/LompocUnified.pdf",
    },
    {
        "district_name": "Marysville Joint Unified",
        "pdf_path": "data/pdfs/MarysvilleJointUnified.pdf",
    },
    {
        "district_name": "Menlo Park",
        "pdf_path": "data/pdfs/MenloPark.pdf",
    },
    {
        "district_name": "Moraga Elementary",
        "pdf_path": "data/pdfs/MoragaElementary.pdf",
    },
    {
        "district_name": "Mother Lode Union Elementary",
        "pdf_path": "data/pdfs/MotherLodeUnionElementary.pdf",
    },
    {
        "district_name": "Oakland Unified",
        "pdf_path": "data/pdfs/OaklandUnified.pdf",
    },
    {
        "district_name": "Roseville City Elementary",
        "pdf_path": "data/pdfs/RosevilleCityElementary.pdf",
    },
    {
        "district_name": "Santa Rosa Elementary",
        "pdf_path": "data/pdfs/SantaRosaElementary.pdf",
    },
    {
        "district_name": "Tahoe-Truckee Unified",
        "pdf_path": "data/pdfs/Tahoe-TruckeeUnified.pdf",
    },
    {
        "district_name": "Wheatland",
        "pdf_path": "data/pdfs/Wheatland.pdf",
    },
]

OUTPUT_DIR = "data/output"
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "all_fmps_chunked_results.csv")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    results = []

    for fmp in TEST_FMPS:
        district = fmp["district_name"]
        pdf_path = fmp["pdf_path"]

        print(f"\nScoring {district}...")
        print(f"PDF path: {pdf_path}")

        try:
            scored = score_fmp_pdf(pdf_path)

            pred_outdoor = int(scored["outdoor"]["score"])
            pred_climate = int(scored["climate"]["score"])
            pred_energy = int(scored["energy"]["score"])
            pred_total = pred_outdoor + pred_climate + pred_energy

            results.append({
                "District Name": district,
                "PDF Path": pdf_path,

                "Pred Outdoor Score": pred_outdoor,
                "Pred Climate Score": pred_climate,
                "Pred Energy Score": pred_energy,
                "Pred Total Score": pred_total,

                "Outdoor Confidence": scored["outdoor"]["confidence"],
                "Climate Confidence": scored["climate"]["confidence"],
                "Energy Confidence": scored["energy"]["confidence"],

                "Outdoor Reasoning": scored["outdoor"]["reasoning"],
                "Climate Reasoning": scored["climate"]["reasoning"],
                "Energy Reasoning": scored["energy"]["reasoning"],

                "Num Pages": scored["num_pages"],
                "Num Chunks": scored["num_chunks"],
            })

            district_slug = (
                district.lower()
                .replace(" ", "_")
                .replace("-", "_")
            )

            with open(os.path.join(OUTPUT_DIR, f"{district_slug}_chunked_full_output.json"), "w") as f:
                json.dump(scored, f, indent=2)

        except Exception as e:
            print(f"Failed on {district}: {e}")
            results.append({
                "District Name": district,
                "PDF Path": pdf_path,
                "error": str(e)
            })

    out_df = pd.DataFrame(results)
    out_df.to_csv(OUTPUT_CSV, index=False)

    print("\nDone.")
    print(out_df)
    print(f"\nSaved CSV results to: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()