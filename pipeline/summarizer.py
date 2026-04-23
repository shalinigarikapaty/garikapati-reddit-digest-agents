import json
import logging
import boto3

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are a Reddit digest assistant. When given Reddit posts, return a JSON array "
    "where each element has exactly these fields:\n"
    '- "title": the original post title (string)\n'
    '- "url": the original post URL (string)\n'
    '- "summary": a 1-2 sentence summary of what the post is about (string)\n'
    '- "key_insight": the single most interesting or actionable takeaway (string)\n\n'
    "CRITICAL: Return ONLY the JSON array. No markdown code fences, no backticks, "
    "no explanation before or after. Start with [ and end with ]. "
    "Escape all quotes inside strings properly using backslashes."
)


def summarize_posts(posts: list[dict], subreddit: str, model: str, max_tokens: int) -> list[dict]:
    if not posts:
        return []

    bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

    posts_text = ""
    for i, post in enumerate(posts, 1):
        posts_text += f"\n--- Post {i} ---\n"
        posts_text += f"Title: {post['title']}\n"
        posts_text += f"Score: {post['score']} | Comments: {post['num_comments']}\n"
        posts_text += f"URL: {post['url']}\n"
        if post["selftext"]:
            posts_text += f"Text: {post['selftext']}\n"

    user_message = f"Summarize the top posts from r/{subreddit}:\n{posts_text}"

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "system": _SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_message}],
    })

    try:
        response = bedrock.invoke_model(modelId=model, body=body)
    except Exception as e:
        logger.warning(f"Bedrock API error for r/{subreddit}: {e}")
        return []

    result = json.loads(response["body"].read())
    raw = result["content"][0]["text"].strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        lines = raw.splitlines()
        raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        summaries = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse Claude JSON for r/{subreddit}: {e}\nRaw: {raw[:200]}")
        return []

    if not isinstance(summaries, list):
        logger.warning(f"Unexpected Claude response shape for r/{subreddit}")
        return []

    # Validate, attach original score/num_comments by URL match
    url_map = {p["url"]: p for p in posts}
    validated = []
    for item in summaries:
        if not isinstance(item, dict):
            continue
        original = url_map.get(str(item.get("url", "")), {})
        validated.append({
            "title": str(item.get("title", "")),
            "url": str(item.get("url", "")),
            "summary": str(item.get("summary", "")),
            "key_insight": str(item.get("key_insight", "")),
            "score": original.get("score", 0),
            "num_comments": original.get("num_comments", 0),
        })

    return validated
