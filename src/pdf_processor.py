from pathlib import Path
import pymupdf4llm


def extract_pdf_to_markdown(pdf_path: str | Path) -> str:
    """
    Extract the contents of a PDF file and convert them to Markdown.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Extracted document contents as Markdown.
    """

    # Convert the supplied path into a Path object.
    pdf_path = Path(pdf_path).expanduser()

    # Check whether the PDF exists.
    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    # Extract PDF contents and convert them into Markdown.
    markdown_text = pymupdf4llm.to_markdown(str(pdf_path))

    # Make sure something was extracted.
    if not markdown_text.strip():
        raise ValueError(f"No text could be extracted from: {pdf_path}")

    return markdown_text


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python src/pdf_processor.py path/to/paper.pdf")
        sys.exit(1)

    pdf_file = sys.argv[1]

    try:
        extracted_text = extract_pdf_to_markdown(pdf_file)

        print("\nPDF extraction successful!")
        print(f"Extracted characters: {len(extracted_text)}")
        print("\n--- First 3,000 characters ---\n")
        print(extracted_text[:3000])

    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
        sys.exit(1)
