const express = require('express')
const cors = require('cors')
const fs = require('fs')
const path = require('path')

const app = express()
const PORT = 3001
const DIGEST_PATH = path.join(__dirname, '..', 'pipeline', 'output', 'digest.json')

app.use(cors({ origin: 'http://localhost:5173' }))

// Request logger
app.use((req, res, next) => {
  const start = Date.now()
  res.on('finish', () => {
    const ms = Date.now() - start
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.path} → ${res.statusCode} (${ms}ms)`)
  })
  next()
})

app.get('/api/digest', (_req, res) => {
  if (!fs.existsSync(DIGEST_PATH)) {
    return res.status(404).json({
      error: 'Digest not found. Run the Python pipeline first.',
    })
  }

  try {
    const raw = fs.readFileSync(DIGEST_PATH, 'utf-8')
    const data = JSON.parse(raw)
    res.json(data)
  } catch (err) {
    console.error('Failed to read/parse digest:', err.message)
    res.status(500).json({ error: 'Failed to read digest file.' })
  }
})

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`)
  console.log(`Serving digest from: ${DIGEST_PATH}`)
})
