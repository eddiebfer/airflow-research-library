
import json
import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def send_discord_notification(metadata: dict, filename: str):
    """
    Send a research paper notification to a Discord channel.
    """

    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")

    if not webhook_url:
        raise ValueError("DISCORD_WEBHOOK_URL environment variable is missing")

    message = {
        "content": (
            "📚 **New Research Paper Processed!**\n\n"
            f"**Title:** {metadata['title']}\n"
            f"**Category:** {metadata['category']}\n"
            f"**Summary:** {metadata['summary']}\n"
            f"**Keywords:** {', '.join(metadata['keywords'])}\n"
            f"**Filename:** {filename}"
        )
    }

    payload = json.dumps(message).encode("utf-8")

    request = Request(
        webhook_url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "ResearchLibraryAirflow/1.0"
    },
        method="POST"
    )

    try:
        with urlopen(request, timeout=15) as response:
            if response.status not in (200, 204):
                raise RuntimeError(
                    f"Discord returned unexpected status: {response.status}"
                )

        print("Discord notification sent successfully!")

    except HTTPError as error:
        response_body = error.read().decode("utf-8", errors="replace")

        print(f"Discord HTTP error: {error.code}")
        print(f"Response body: {response_body[:1000]}")

        raise RuntimeError(
                f"Discord HTTP error: {error.code} - {error.reason}"
        ) from error

    except URLError as error:
        raise RuntimeError(
            f"Could not connect to Discord: {error.reason}"
        ) from error
