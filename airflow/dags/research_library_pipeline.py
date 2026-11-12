
import os
import sys
from pathlib import Path

import pendulum
from airflow.sdk import dag, task


# Locate the project root so Airflow can import modules from src/
PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))


@dag(
    dag_id="research_library_pipeline",
    description="Automatically process research papers using a local LLM",
    start_date=pendulum.datetime(
        2026, 11, 10, tz="Europe/Brussels"
    ),
    schedule="0 * * * *",
    catchup=False,
    tags=["assignment3", "research", "AI"],
)
def research_library_pipeline():

    # TASK 1: Find new PDF files in Google Drive
    @task
    def discover_new_papers():

        from src.database import init_db, paper_exists

        papers_dir = os.environ.get("PAPERS_DIR")

        if not papers_dir:
            raise ValueError("PAPERS_DIR environment variable is missing")

        papers_path = Path(papers_dir).expanduser()

        if not papers_path.is_dir():
            raise FileNotFoundError(
                f"Research papers folder not found: {papers_path}"
            )

        init_db()

        new_papers = []

        for pdf_file in sorted(papers_path.glob("*.pdf")):
            if not paper_exists(pdf_file.name):
                new_papers.append(str(pdf_file))

        print(f"New papers found: {len(new_papers)}")

        for filename in new_papers:
            print(f" - {Path(filename).name}")

        return new_papers

    # TASK 2: Extract PDF and generate metadata using Qwen
    @task
    def process_new_papers(pdf_files):

        from src.pdf_processor import extract_pdf_to_markdown
        from src.llm_processor import generate_metadata
        from src.database import save_paper

        newly_processed = []

        for pdf_path in pdf_files:

            pdf_path = Path(pdf_path)

            print(f"\nProcessing: {pdf_path.name}")

            # Extract PDF content
            markdown_text = extract_pdf_to_markdown(pdf_path)

            print(
                f"Extracted characters: {len(markdown_text)}"
            )

            # Generate metadata using local Qwen model
            metadata = generate_metadata(
                markdown_text,
                filename=pdf_path.name
            )

            print("Metadata generated successfully.")

            # Save metadata in SQLite
            inserted = save_paper(
                pdf_path.name,
                metadata
            )

            if inserted:
                print(f"Saved to database: {pdf_path.name}")

                newly_processed.append({
                    "filename": pdf_path.name,
                    "metadata": metadata
                })
            else:
                print(f"Already in database: {pdf_path.name}")

        return newly_processed

    # TASK 3: Send a Discord notification for each new paper
    @task
    def send_notifications(papers):

        from src.discord_notifier import send_discord_notification

        for paper in papers:

            send_discord_notification(
                paper["metadata"],
                paper["filename"]
            )

        print(f"Notifications sent: {len(papers)}")

    # TASK 4: Regenerate the searchable HTML library
    @task
    def generate_research_library():

        from src.html_generator import generate_html

        output_file = generate_html()

        print(f"Research library updated: {output_file}")

    # Define the task dependencies
    new_papers = discover_new_papers()

    processed_papers = process_new_papers(new_papers)

    notifications = send_notifications(processed_papers)

    html_library = generate_research_library()

    notifications >> html_library


research_library_pipeline()
