import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def write_digest(digest: dict[str, list[dict]], output_path: str) -> None:
    subreddits = [
        {
            "name": name,
            "posts": [
                {
                    "title": post["title"],
                    "url": post["url"],
                    "score": post.get("score", 0),
                    "num_comments": post.get("num_comments", 0),
                    "summary": post["summary"],
                    "key_insight": post["key_insight"],
                }
                for post in posts
            ],
        }
        for name, posts in digest.items()
    ]

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "subreddits": subreddits,
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"  Digest written → {output_path}")
    logger.info(f"Digest written to {output_path}")
    return payload
