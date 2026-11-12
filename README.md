# Research Library Automation with Apache Airflow

**Automated Research Paper Processing and Indexing**  
**Author:** Eddie Fernandez  
**Course:** Université libre de Bruxelles (ULB) — INFO-H420, Assignment 3: Workflows with Airflow  
**GitHub repository:** https://github.com/eddiebfer/airflow-research-library

## 1. Project overview

This project automates the processing and indexing of academic research papers stored as PDF files in a Google Drive-synchronized folder.

Apache Airflow orchestrates the workflow. When a new PDF is detected, the system extracts its text, uses a locally hosted large language model (LLM) to generate structured metadata, saves the metadata in SQLite, sends a Discord notification, and regenerates a searchable HTML research library.

The final end-to-end test processed a newly added paper in **1 minute and 17 seconds**. The library increased from seven to **eight indexed papers**.

## 2. Features

- Detects new PDF files in the configured research-paper folder.
- Extracts PDF content and converts it to Markdown using **PyMuPDF4LLM**.
- Uses **Ollama** with the **Qwen 2.5 7B** model to generate metadata locally.
- Produces structured metadata:
  - `title`
  - `summary`
  - `keywords` (a list)
  - `category`
- Parses and validates the LLM response as JSON, with one correction attempt if validation fails.
- Stores paper metadata in a local **SQLite** database.
- Avoids duplicate processing using a unique filename constraint.
- Sends a **Discord** notification after a new paper is successfully processed.
- Generates an HTML research library with search and category filtering.

## 3. Workflow

The Airflow DAG is named `research_library_pipeline` and is configured to run hourly (`0 * * * *`) with catchup disabled.

The DAG contains four tasks:

1. **`discover_new_papers`** — scans the configured papers folder and identifies PDF files that are not yet recorded in SQLite.
2. **`process_new_papers`** — extracts each new PDF, requests metadata from the local Qwen model, validates the response, and stores the result in SQLite.
3. **`send_notifications`** — sends a Discord notification for each newly processed paper.
4. **`generate_research_library`** — regenerates the HTML research library from the SQLite records.

The processing, notification, and HTML-generation steps run in sequence after discovery.

## 4. Technology stack

| Component | Technology | Purpose |
|---|---|---|
| Workflow orchestration | Apache Airflow 3.4.0 | Schedules and coordinates tasks |
| PDF extraction | PyMuPDF4LLM | Converts PDF content to Markdown |
| Local LLM runtime | Ollama | Hosts the language model locally |
| LLM | Qwen 2.5 7B | Generates paper metadata |
| LLM API client | OpenAI Python client | Communicates with Ollama's OpenAI-compatible endpoint |
| Database | SQLite | Stores metadata and prevents duplicate records |
| Notifications | Discord webhook | Reports successful processing |
| Output | HTML, CSS and JavaScript | Provides the searchable research library |
| Input/output storage | Google Drive for Desktop | Synchronizes source PDFs and generated HTML |

## 5. Project structure

The main project components are organized as follows:

```text
airflow_research_project/
├── airflow/
│   └── dags/
│       └── research_library_pipeline.py
├── data/
│   └── research_library.db          # Generated locally; do not commit
├── dags/                            # Additional DAG-related project folder, if used
├── output/                          # Local project output, if used
├── scripts/
│   └── test_pipeline.py
├── src/
│   ├── pdf_processor.py
│   ├── llm_processor.py
│   ├── database.py
│   ├── html_generator.py
│   └── discord_notifier.py
├── tests/
├── .gitignore
└── README.md
```

The SQLite database is stored locally under `data/`, outside the Google Drive-synchronized research library. The generated `index.html` is saved to the configured Google Drive output folder.

## 6. Prerequisites

The project was developed and tested on a MacBook Air with Apple Silicon.

Install or configure the following:

- Python (the development environment used Python 3.14.10).
- Apache Airflow 3.4.0.
- Ollama.
- The Qwen 2.5 7B model in Ollama.
- Google Drive for Desktop, with a synchronized `ResearchLibrary` folder.
- A Discord webhook for notifications.

The Python environment also needs the project dependencies used by the source modules, including PyMuPDF4LLM, the OpenAI Python client, and the HTTP requests library. If the repository contains a `requirements.txt`, install from that file using the installation instructions appropriate for the Airflow version.

> **Note:** Airflow can be sensitive to Python-version and dependency compatibility. Use a Python version supported by the installed Airflow release if recreating the environment on another computer.

## 7. Configuration

### 7.1 Google Drive folders

Create the following folder structure in your Google Drive:

```text
ResearchLibrary/
├── papers/
└── output/
```

Place the research PDF files in `papers/`. The generated `index.html` will be written to `output/`.

### 7.2 Environment variables

Set the following environment variables in the same Terminal session used to start Airflow. Update the Google Drive path to match the location on your computer.

```bash
export AIRFLOW_HOME="$HOME/airflow_research_project/airflow"

export PAPERS_DIR="$HOME/Library/CloudStorage/GoogleDrive-YOUR-ACCOUNT/My Drive/ResearchLibrary/papers"

export DISCORD_WEBHOOK_URL="YOUR_DISCORD_WEBHOOK_URL"
```

Replace `YOUR-ACCOUNT` with the Google Drive account folder name on your Mac, and replace the webhook placeholder with your own Discord webhook URL.

**Security:** Never commit a real Discord webhook URL, `.env` file, credentials, or other secrets to GitHub. Keep secrets in environment variables or another secure local configuration method.

### 7.3 Ollama model

Make sure Ollama is running and the model is available:

```bash
ollama pull qwen2.5:7b
ollama run qwen2.5:7b
```

The application communicates with Ollama through its OpenAI-compatible local endpoint:

```text
http://localhost:11434/v1
```

The configured model is `qwen2.5:7b`.

## 8. Running the project

Open a Terminal, activate the project's virtual environment, and configure the environment variables:

```bash
cd ~/airflow_research_project
source .venv/bin/activate

export AIRFLOW_HOME="$HOME/airflow_research_project/airflow"
export PAPERS_DIR="$HOME/Library/CloudStorage/GoogleDrive-YOUR-ACCOUNT/My Drive/ResearchLibrary/papers"
export DISCORD_WEBHOOK_URL="YOUR_DISCORD_WEBHOOK_URL"
```

Ensure Ollama is running in the background and that `qwen2.5:7b` is available.

Start Airflow:

```bash
airflow standalone
```

Airflow standalone starts the local Airflow services. Open the Airflow UI:

```text
http://localhost:8080
```

Find the DAG named `research_library_pipeline`. Enable it if necessary, then use **Trigger DAG** to run it manually. Otherwise, the DAG runs according to its hourly schedule.

Keep the Terminal session running while Airflow is operating. The environment variables must be present in the environment in which Airflow is started.

## 9. Outputs

The workflow produces the following outputs:

| Output | Location | Description |
|---|---|---|
| SQLite database | `data/research_library.db` | Stores paper metadata and processing timestamps |
| HTML research library | `ResearchLibrary/output/index.html` in Google Drive | Searchable page with category filtering, summaries, and keywords |
| Discord message | Configured Discord channel | Notification for each successfully processed new paper |

The original PDFs remain in the Google Drive `ResearchLibrary/papers/` folder.

## 10. Testing and verification

The project was tested through manual and scheduled Airflow executions.

| Test | Result |
|---|---|
| Manual DAG run with no new papers | Successful — approximately 11 seconds |
| Scheduled DAG run with no new papers | Successful — approximately 12 seconds |
| New PDF detection | One new paper detected |
| End-to-end processing of the new PDF | Successful — 1 minute 17 seconds |
| SQLite database | Eight papers saved |
| Discord notification | Successfully delivered |
| HTML research library | Successfully regenerated with eight papers |

The end-to-end test consisted of adding a new integral-imaging research paper to the Google Drive `papers` folder and triggering the DAG. Airflow detected the new file, extracted its content, generated and validated metadata using Qwen 2.5 7B, inserted the record into SQLite, sent the Discord notification, and regenerated the HTML page.

## 11. Known limitations and possible improvements

- Duplicate detection currently relies on the PDF filename. A modified PDF with the same filename will not automatically be reprocessed. A content hash or file-modification check could improve this.
- LLM-generated summaries and keywords may contain omissions or inaccuracies and should be reviewed.
- Long research papers can increase local inference time. The current implementation limits the amount of extracted text sent to the model.
- Future improvements could include stronger retry and backoff handling, more detailed task-level error reporting, additional search/filter options, and a configurable LLM model.

## 12. Individual authorship

**Author:** Eddie Fernandez

This project was completed individually. The author designed, implemented, integrated, tested, and documented the complete research-paper automation workflow.

---

**Course submission:** ULB — INFO-H420, Assignment 3: Workflows with Airflow  
**Repository:** https://github.com/eddiebfer/airflow-research-library
