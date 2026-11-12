
import os
import sys
import json
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from src.pdf_processor import extract_pdf_to_markdown
from src.llm_processor import generate_metadata
from src.database import init_db, save_paper, get_all_papers


def main():

    # Initialize the SQLite database.
    init_db()

    papers_dir = Path(os.environ["PAPERS_DIR"]).expanduser()

    if not papers_dir.is_dir():
        raise FileNotFoundError(
            f"Papers folder not found: {papers_dir}"
        )

    pdf_files = sorted(papers_dir.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            "No PDF files found in the papers folder"
        )

    # Test using the first PDF.
    pdf_path = pdf_files[0]

    print(f"\nSelected paper: {pdf_path.name}")

    print("\nStep 1: Checking database...")

    existing_papers = get_all_papers()

    if any(p["filename"] == pdf_path.name for p in existing_papers):
        print("Paper already exists in the database.")
        print("Skipping AI processing.")

    else:
        print("\nStep 2: Extracting PDF content...")

        markdown_text = extract_pdf_to_markdown(pdf_path)

        print("PDF extraction successful!")
        print(f"Extracted characters: {len(markdown_text)}")

        print("\nStep 3: Generating metadata using Qwen...")

        metadata = generate_metadata(
            markdown_text,
            filename=pdf_path.name
        )

        print("\nStep 4: Saving metadata to SQLite...")

        inserted = save_paper(pdf_path.name, metadata)

        if inserted:
            print("Paper successfully saved!")
        else:
            print("Paper already exists. No duplicate inserted.")

        print("\nGenerated metadata:")
        print(json.dumps(metadata, indent=4, ensure_ascii=False))

    # Display the database records.
    print("\nStep 5: Current database contents:")

    for paper in get_all_papers():
        print(f"\nFilename: {paper['filename']}")
        print(f"Title: {paper['title']}")
        print(f"Category: {paper['category']}")
        print(f"Keywords: {', '.join(paper['keywords'])}")


if __name__ == "__main__":
    main()
