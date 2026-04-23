# Reddit Morning Digest

A personal digest pipeline that fetches top Reddit posts, summarizes them with Claude on AWS Bedrock, emails the digest via AWS SES, and displays it in a React UI.

## How it works

```
Python pipeline → digest.json → Node/Express API → React UI
                       ↓
                  AWS SES email
```

1. **Fetch** — pulls top posts from configured subreddits via the Reddit JSON API
2. **Summarize** — sends posts to Claude (Haiku 4.5 via AWS Bedrock) for a structured JSON summary with key insights
3. **Write** — saves the digest to `pipeline/output/digest.json`
4. **Email** — sends an HTML digest email via AWS SES
5. **View** — Node server exposes the digest; React app renders it

## Project structure

```
├── pipeline/
│   ├── main.py          # Entry point — orchestrates fetch → summarize → write → email
│   ├── fetcher.py       # Reddit JSON API client
│   ├── summarizer.py    # AWS Bedrock / Claude integration
│   ├── email_sender.py  # AWS SES HTML email sender
│   └── writer.py        # Writes digest.json
├── server/
│   └── index.js         # Express API serving digest.json on port 3001
├── client/
│   └── src/             # React/Vite frontend
└── config.yaml          # Subreddits, model, and email settings
```

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- AWS account with Bedrock and SES access

### 1. Clone and install

```bash
git clone https://github.com/shalinigarikapaty/garikapati-reddit-digest-agents.git
cd garikapati-reddit-digest-agents
```

```bash
# Python dependencies
cd pipeline && pip install -r requirements.txt

# Node dependencies
cd ../server && npm install
cd ../client && npm install
```

### 2. Configure credentials

Copy `.env.example` to `.env` in the `pipeline/` directory and fill in your AWS credentials:

```bash
cp .env.example pipeline/.env
```

```env
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_DEFAULT_REGION=us-east-1
```

Your IAM user needs:
- `AmazonBedrockFullAccess`
- `AmazonSESFullAccess`

### 3. Configure subreddits and email

Edit `config.yaml`:

```yaml
reddit:
  subreddits:
    - vibecoding
    - claudeai
    - productivity

email:
  enabled: true
  sender: your-verified-sender@example.com
  recipient: your-recipient@example.com
  aws_region: us-east-1
```

Both sender and recipient must be verified in the [AWS SES console](https://console.aws.amazon.com/ses) (required while in SES sandbox mode).

### 4. Run the pipeline

```bash
cd pipeline && python main.py
```

### 5. View the digest

```bash
# Terminal 1 — start the API server
cd server && node index.js

# Terminal 2 — start the React app
cd client && npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

## Automating with a cron job (macOS)

Create a Launch Agent plist at `~/Library/LaunchAgents/com.reddit-digest.plist` to run the pipeline on a schedule.

## Configuration reference

| Key | Description |
|---|---|
| `reddit.subreddits` | List of subreddits to fetch |
| `reddit.time_filter` | `hour`, `day`, `week`, `month`, `year` |
| `reddit.post_limit` | Max posts to fetch per subreddit |
| `reddit.score_threshold` | Minimum upvote score to include a post |
| `reddit.posts_per_summary` | Posts passed to Claude per subreddit |
| `claude.model` | Bedrock model ID (cross-region inference profile) |
| `claude.max_tokens` | Max tokens in Claude's response |
| `email.enabled` | Set to `false` to skip email |
