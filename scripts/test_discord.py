
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from src.discord_notifier import send_discord_notification


sample_metadata = {
    "title": "Integral Imaging: A 3D Imaging Technique",
    "summary": (
        "This paper explains integral imaging as a technique "
        "for capturing and reconstructing three-dimensional scenes. "
        "It uses microlens arrays to record elemental images "
        "from different viewing angles."
    ),
    "keywords": [
        "Integral Imaging",
        "3D Imaging",
        "Elemental Images",
        "Microlens Array"
    ],
    "category": "3D Imaging"
}

send_discord_notification(
    sample_metadata,
    "integral_imaging_test.pdf"
)
