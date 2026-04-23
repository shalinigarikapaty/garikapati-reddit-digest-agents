import logging
import requests

logger = logging.getLogger(__name__)

USER_AGENT = "reddit-digest-agent/1.0"


def fetch_subreddit_posts(subreddit: str, time_filter: str, limit: int, score_threshold: int) -> list[dict]:
    url = f"https://www.reddit.com/r/{subreddit}/top.json"
    params = {"t": time_filter, "limit": limit}
    headers = {"User-Agent": USER_AGENT}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger.warning(f"Failed to fetch r/{subreddit}: {e}")
        return []
    except ValueError as e:
        logger.warning(f"Failed to parse response from r/{subreddit}: {e}")
        return []

    posts = []
    for child in data.get("data", {}).get("children", []):
        post = child.get("data", {})

        if post.get("stickied") or post.get("distinguished") == "moderator":
            continue

        score = post.get("score", 0)
        if score < score_threshold:
            continue

        selftext = post.get("selftext", "") or ""
        if selftext in ("[removed]", "[deleted]"):
            selftext = ""
        selftext = selftext[:500]

        posts.append({
            "title": post.get("title", ""),
            "score": score,
            "url": post.get("url", ""),
            "selftext": selftext,
            "num_comments": post.get("num_comments", 0),
            "author": post.get("author", "[deleted]"),
        })

    return posts
