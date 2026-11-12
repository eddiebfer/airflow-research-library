
import json
import sqlite3
from pathlib import Path


# Store the database in the local project folder,
# NOT inside the Google Drive synchronized folder.
PROJECT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_DIR / "data" / "research_library.db"


def get_connection():
    """Create a connection to the SQLite database."""

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def init_db():
    """Create the papers table if it does not exist."""

    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                summary TEXT NOT NULL,
                keywords TEXT NOT NULL,
                category TEXT NOT NULL,
                processed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.commit()

    print(f"Database initialized: {DB_PATH}")


def save_paper(filename: str, metadata: dict) -> bool:
    """
    Save a research paper's metadata.

    Returns True if a new record was inserted.
    Returns False if the filename already exists.
    """

    init_db()

    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT OR IGNORE INTO papers
            (filename, title, summary, keywords, category)
            VALUES (?, ?, ?, ?, ?)
        """, (
            filename,
            metadata["title"],
            metadata["summary"],
            json.dumps(metadata["keywords"], ensure_ascii=False),
            metadata["category"]
        ))

        connection.commit()

        return cursor.rowcount == 1


def paper_exists(filename: str) -> bool:
    """Check whether a paper has already been processed."""

    init_db()

    with get_connection() as connection:
        result = connection.execute("""
            SELECT 1 FROM papers WHERE filename = ?
        """, (filename,)).fetchone()

        return result is not None


def get_all_papers() -> list:
    """Retrieve all papers from the database."""

    init_db()

    with get_connection() as connection:
        rows = connection.execute("""
            SELECT * FROM papers ORDER BY processed_at DESC
        """).fetchall()

        papers = []

        for row in rows:
            paper = dict(row)
            paper["keywords"] = json.loads(paper["keywords"])
            papers.append(paper)

        return papers


if __name__ == "__main__":
    init_db()

