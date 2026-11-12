
import json
from openai import OpenAI


client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    timeout=180.0,
    max_retries=0
)

MODEL = "qwen2.5:7b"

# Limit the input size for this initial test.
# We can adjust this after confirming the model's context capacity.
MAX_INPUT_CHARACTERS = 8000


def validate_metadata(data: dict) -> dict:
    """Validate the metadata returned by the LLM."""

    required_fields = ["title", "summary", "keywords", "category"]

    if not isinstance(data, dict):
        raise ValueError("The AI response must be a JSON object")

    for field in required_fields:
        if field not in data:
            raise ValueError(
                f"Missing required field: {field}. "
                f"Fields received: {list(data.keys())}"
            )

    if not isinstance(data["title"], str) or not data["title"].strip():
        raise ValueError("Title must be a non-empty string")

    if not isinstance(data["summary"], str) or not data["summary"].strip():
        raise ValueError("Summary must be a non-empty string")

    if not isinstance(data["keywords"], list):
        raise ValueError("Keywords must be a list")

    if not all(isinstance(k, str) for k in data["keywords"]):
        raise ValueError("Every keyword must be a string")

    if not isinstance(data["category"], str) or not data["category"].strip():
        raise ValueError("Category must be a non-empty string")

    return {
        "title": data["title"].strip(),
        "summary": data["summary"].strip(),
        "keywords": data["keywords"],
        "category": data["category"].strip()
    }


def generate_metadata(markdown_text: str, filename: str = "") -> dict:
    """Generate and validate paper metadata, retrying once if necessary."""

    if not markdown_text or not markdown_text.strip():
        raise ValueError("The Markdown text is empty")

    # Keep the beginning of the paper, where title and abstract
    # are normally located, while limiting the prompt size.
    paper_text = markdown_text[:MAX_INPUT_CHARACTERS]

    system_prompt = """
You are an academic research paper analysis assistant.

Return exactly ONE valid JSON object.
Do not use Markdown code fences or add explanations.

The JSON object MUST contain exactly these four keys:

{
  "title": "string",
  "summary": "string",
  "keywords": ["string", "string", "string"],
  "category": "string"
}

Requirements:
- title: the actual title of the research paper.
- summary: approximately 3 to 5 sentences.
- keywords: an array containing 3 to 8 strings.
- category: a short research subject area.
- Base your answer on the supplied paper.
- Do not use alternative key names such as paper_title or abstract.
- Do not omit any of the four required keys.
"""

    user_prompt = f"""
Filename: {filename}

Research paper content:

{paper_text}
"""

    previous_error = None
    previous_response = None

    for attempt in range(2):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # On the second attempt, explicitly explain the previous failure.
        if attempt == 1:
            messages.append({
                "role": "assistant",
                "content": previous_response or "{}"
            })
            messages.append({
                "role": "user",
                "content": (
                    f"Your previous response failed validation: {previous_error}. "
                    "Please correct it. Return a JSON object containing all "
                    "four exact keys: title, summary, keywords, category. "
                    "Do not omit title."
                )
            })

        try:
            print(f"Sending request to Qwen (attempt {attempt + 1})...")

            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1
            )

            response_text = response.choices[0].message.content

            if not response_text:
                raise ValueError("The AI returned an empty response")

            metadata = json.loads(response_text)

            return validate_metadata(metadata)

        except (json.JSONDecodeError, ValueError) as error:
            previous_error = str(error)
            previous_response = response_text if "response_text" in locals() else None

            print(f"Attempt {attempt + 1} failed: {previous_error}")

            if attempt == 1:
                print("\nRaw AI response for troubleshooting:")
                print(previous_response)

                raise ValueError(
                    "The AI failed to return valid metadata after 2 attempts"
                ) from error

    raise RuntimeError("Unexpected error while generating metadata")


if __name__ == "__main__":
    sample_text = """
    Integral imaging is a 3D imaging technique.
    It uses an array of microlenses to capture elemental images
    from different viewing angles. These images can be used
    to reconstruct a three-dimensional scene.
    """

    result = generate_metadata(
        sample_text,
        filename="integral_imaging_test.pdf"
    )

    print("\nMetadata generated successfully:")
    print(json.dumps(result, indent=4, ensure_ascii=False))
