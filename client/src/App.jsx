import { useState, useEffect } from 'react'
import Header from './components/Header'
import SubredditSection from './components/SubredditSection'
import './App.css'

export default function App() {
  const [digest, setDigest] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch('http://localhost:3001/api/digest')
      .then(res => {
        if (!res.ok) {
          return res.json().then(body => {
            throw new Error(body.error || `HTTP ${res.status}`)
          })
        }
        return res.json()
      })
      .then(data => {
        setDigest(data)
        setLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="app">
        <div className="status-screen">
          <div className="spinner" />
          <p>Loading your digest...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="app">
        <div className="status-screen error">
          <h2>Could not load digest</h2>
          <p className="error-message">{error}</p>
          <div className="error-instructions">
            <p>To generate the digest, run:</p>
            <pre>cd pipeline && python main.py</pre>
            <p>Then refresh this page.</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <Header generatedAt={digest.generated_at} />
      <main className="main-content">
        {digest.subreddits.map(subreddit => (
          <SubredditSection key={subreddit.name} subreddit={subreddit} />
        ))}
      </main>
    </div>
  )
}
