import logging
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / '.env')

import yaml

from email_sender import send_digest
from fetcher import fetch_subreddit_posts
from summarizer import summarize_posts
from writer import write_digest
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent


def load_config() -> dict:
    config_path = PROJECT_ROOT / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def main() -> None:
    config = load_config()

    reddit_cfg = config["reddit"]
    claude_cfg = config["claude"]
    output_cfg = config["output"]
    email_cfg = config.get("email", {})

    subreddits = reddit_cfg["subreddits"]
    time_filter = reddit_cfg["time_filter"]
    post_limit = reddit_cfg["post_limit"]
    score_threshold = reddit_cfg["score_threshold"]
    posts_per_summary = reddit_cfg["posts_per_summary"]

    model = claude_cfg["model"]
    max_tokens = claude_cfg["max_tokens"]

    output_path = str(PROJECT_ROOT / output_cfg["json_file"])

    print(f"\nReddit Morning Digest Pipeline")
    print(f"{'─' * 40}")
    print(f"Subreddits : {', '.join(subreddits)}")
    print(f"Time filter: {time_filter}  |  Score threshold: {score_threshold}")
    print(f"Model      : {model}")
    print(f"Output     : {output_path}")
    print()

    digest: dict[str, list[dict]] = {}

    for subreddit in subreddits:
        # ── Fetch ──────────────────────────────────────────────────────────────
        print(f"[fetch]    r/{subreddit} …", end=" ", flush=True)
        posts = fetch_subreddit_posts(subreddit, time_filter, post_limit, score_threshold)

        if not posts:
            print("⚠  no qualifying posts — skipping")
            logger.warning(f"r/{subreddit} returned no posts above threshold — skipping")
            continue

        posts = posts[:posts_per_summary]
        print(f"✓  {len(posts)} posts")

        # ── Summarise ──────────────────────────────────────────────────────────
        print(f"[claude]   r/{subreddit} …", end=" ", flush=True)
        summaries = summarize_posts(posts, subreddit, model, max_tokens)

        if not summaries:
            print("⚠  summarisation failed — skipping")
            logger.warning(f"r/{subreddit} summarisation returned nothing — skipping")
            continue

        digest[subreddit] = summaries
        print(f"✓  {len(summaries)} summaries")

    if not digest:
        print("\nNothing to write. Check your ANTHROPIC_API_KEY and logs above.")
        sys.exit(1)

    # ── Write ──────────────────────────────────────────────────────────────────
    print(f"\n[write]    Saving digest …", end=" ", flush=True)
    digest_data = write_digest(digest, output_path)
    print("✓")

    # ── Email ──────────────────────────────────────────────────────────────────
    if email_cfg.get("enabled"):
        print("[email]    Sending digest …", end=" ", flush=True)
        send_digest(digest_data, email_cfg)

    print(f"\nDone! Start the Node server and open the React app to view your digest.")


if __name__ == "__main__":
    main()
