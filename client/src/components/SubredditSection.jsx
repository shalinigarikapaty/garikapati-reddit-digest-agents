import { useState } from 'react'
import PostCard from './PostCard'

export default function SubredditSection({ subreddit }) {
  const [open, setOpen] = useState(false)

  return (
    <section className="subreddit-section">
      <h2 className="subreddit-toggle" onClick={() => setOpen(o => !o)}>
        <span className="toggle-icon">{open ? '▼' : '►'}</span>
        <span className="subreddit-prefix">r/</span>{subreddit.name}
        <span className="post-count">{subreddit.posts.length} posts</span>
      </h2>
      <div className={`posts-grid${open ? ' posts-grid--open' : ''}`}>
        <div className="posts-grid-inner">
          {subreddit.posts.map((post, i) => (
            <PostCard key={post.url || i} post={post} />
          ))}
        </div>
      </div>
    </section>
  )
}
