export default function Header({ generatedAt }) {
  const formatted = generatedAt
    ? new Date(generatedAt).toLocaleString(undefined, {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    : null

  return (
    <header className="site-header">
      <h1>
        <span>r/</span>Morning Digest
      </h1>
      {formatted && <span className="timestamp">Generated {formatted}</span>}
    </header>
  )
}
