export default function PostCard({ post }) {
  return (
    <article className="post-card">
      <div className="post-title">
        <a href={post.url} target="_blank" rel="noopener noreferrer">
          {post.title}
        </a>
      </div>

      {post.summary && (
        <p className="post-summary">{post.summary}</p>
      )}

      {post.key_insight && (
        <div className="key-insight">{post.key_insight}</div>
      )}

      <div className="post-meta">
        <span>▲ {post.score?.toLocaleString()} upvotes</span>
        <span>💬 {post.num_comments?.toLocaleString()} comments</span>
      </div>
    </article>
  )
}
