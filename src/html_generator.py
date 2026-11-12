
import os
import html
import sys
from pathlib import Path

# Add the project root to Python's import path.
PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from src.database import get_all_papers


PROJECT_DIR = Path(__file__).resolve().parents[1]


def get_output_directory() -> Path:
    """
    Prefer the output folder next to the Google Drive papers folder.
    Otherwise, use the local project output folder.
    """

    papers_dir = os.environ.get("PAPERS_DIR")

    if papers_dir:
        return Path(papers_dir).expanduser().parent / "output"

    return PROJECT_DIR / "output"


def generate_html():
    """Generate the searchable HTML research library."""

    papers = get_all_papers()
    output_dir = get_output_directory()

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "index.html"

    # Get all unique research categories.
    categories = sorted({
        paper["category"] for paper in papers
    })

    # Generate category dropdown options.
    category_options = "\n".join(
        f'<option value="{html.escape(category, quote=True)}">'
        f'{html.escape(category)}</option>'
        for category in categories
    )

    # Generate one HTML card for each paper.
    paper_cards = []

    for paper in papers:
        title = html.escape(paper["title"])
        summary = html.escape(paper["summary"])
        filename = html.escape(paper["filename"])
        category = html.escape(paper["category"])
        keywords = ", ".join(paper["keywords"])
        keywords = html.escape(keywords)

        card = f"""
        <article class="paper-card"
                 data-category="{category}">
            <h2>{title}</h2>

            <p class="category">{category}</p>

            <p>{summary}</p>

            <p class="keywords">
                <strong>Keywords:</strong> {keywords}
            </p>

            <p class="filename">
                <strong>PDF:</strong> {filename}
            </p>
        </article>
        """

        paper_cards.append(card)

    cards_html = "\n".join(paper_cards)

    if not papers:
        cards_html = "<p>No research papers have been processed yet.</p>"

    # Complete HTML page.
    template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Research Library</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1000px;
            margin: 40px auto;
            padding: 0 20px;
            background: #f5f7fa;
            color: #263238;
        }

        h1 {
            color: #183153;
        }

        .controls {
            display: flex;
            gap: 12px;
            margin: 25px 0;
            flex-wrap: wrap;
        }

        input, select {
            padding: 12px;
            font-size: 15px;
            border: 1px solid #ccc;
            border-radius: 6px;
        }

        input {
            flex: 1;
            min-width: 220px;
        }

        .paper-card {
            background: white;
            padding: 22px;
            margin-bottom: 18px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.08);
        }

        .paper-card h2 {
            color: #183153;
            margin-top: 0;
        }

        .category {
            color: #087f8c;
            font-weight: bold;
        }

        .keywords, .filename {
            font-size: 14px;
            color: #555;
        }

        #paper-count {
            color: #555;
            margin-bottom: 20px;
        }

        .no-results {
            display: none;
            padding: 20px;
            background: white;
            border-radius: 8px;
        }
    </style>
</head>

<body>

    <h1>Research Library</h1>

    <p>Browse and search your processed research papers.</p>

    <div class="controls">
        <input
            type="text"
            id="search"
            placeholder="Search title, summary or keywords..."
        >

        <select id="category">
            <option value="">All categories</option>
            CATEGORY_OPTIONS
        </select>
    </div>

    <p id="paper-count"></p>

    <main id="paper-list">
        PAPER_CARDS
    </main>

    <p class="no-results" id="no-results">
        No matching research papers found.
    </p>

    <script>
        const searchInput = document.getElementById("search");
        const categorySelect = document.getElementById("category");
        const cards = document.querySelectorAll(".paper-card");
        const countDisplay = document.getElementById("paper-count");
        const noResults = document.getElementById("no-results");

        function filterPapers() {
            const searchText = searchInput.value.toLowerCase();
            const selectedCategory = categorySelect.value;

            let visibleCount = 0;

            cards.forEach(card => {
                const text = card.textContent.toLowerCase();
                const category = card.dataset.category;

                const matchesSearch = text.includes(searchText);
                const matchesCategory =
                    !selectedCategory || category === selectedCategory;

                const visible = matchesSearch && matchesCategory;

                card.style.display = visible ? "block" : "none";

                if (visible) {
                    visibleCount++;
                }
            });

            countDisplay.textContent =
                visibleCount + " of " + cards.length + " papers displayed";

            noResults.style.display =
                visibleCount === 0 ? "block" : "none";
        }

        searchInput.addEventListener("input", filterPapers);
        categorySelect.addEventListener("change", filterPapers);

        filterPapers();
    </script>

</body>
</html>
"""

    page = (
        template
        .replace("CATEGORY_OPTIONS", category_options)
        .replace("PAPER_CARDS", cards_html)
    )

    output_file.write_text(page, encoding="utf-8")

    print(f"\nHTML research library generated successfully!")
    print(f"Total papers: {len(papers)}")
    print(f"Output file: {output_file}")

    return output_file


if __name__ == "__main__":
    generate_html()

