import { useEffect, useRef, useState } from 'react'
import './App.css'

const API_URL = 'http://localhost:8000'

let nextId = 0
function makeId() {
  nextId += 1
  return nextId
}

function App() {
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [users, setUsers] = useState([])
  const [userId, setUserId] = useState('')
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages, loading])

  useEffect(() => {
    fetch(`${API_URL}/users`)
      .then((response) => response.json())
      .then((data) => {
        setUsers(data)
        setUserId((current) => current || data[0]?.id || '')
      })
      .catch(() => setUsers([]))
  }, [])

  async function handleSubmit(event) {
    event.preventDefault()
    const trimmed = question.trim()
    if (!trimmed || loading) return

    if (trimmed === '/clear') {
      setMessages([])
      setQuestion('')
      return
    }

    setMessages((prev) => [...prev, { id: makeId(), role: 'user', content: trimmed }])
    setQuestion('')
    setLoading(true)

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: trimmed, user_id: userId }),
      })

      if (!response.ok) {
        const detail = await response.json().catch(() => null)
        throw new Error(detail?.detail?.[0]?.msg || `Request failed (${response.status})`)
      }

      const data = await response.json()
      setMessages((prev) => [
        ...prev,
        { id: makeId(), role: 'assistant', content: data.answer, sources: data.sources },
      ])
    } catch (err) {
      setMessages((prev) => [...prev, { id: makeId(), role: 'error', content: err.message }])
    } finally {
      setLoading(false)
    }
  }

  const isEmpty = messages.length === 0

  const currentUser = users.find((user) => user.id === userId)

  return (
    <div className="chat">
      <div className="session">
        <label htmlFor="user-select">Asking as</label>
        <select
          id="user-select"
          value={userId}
          onChange={(event) => setUserId(event.target.value)}
          disabled={loading || users.length === 0}
        >
          {users.map((user) => (
            <option key={user.id} value={user.id}>
              {user.name} - {user.title}
            </option>
          ))}
        </select>
        {currentUser && <span className="session-role">{currentUser.role}</span>}
      </div>

      <div className={`history ${isEmpty ? 'history--empty' : ''}`}>
        {isEmpty ? (
          <div className="prompt">
            <h1>Pinnacle Solutions HR Assistant</h1>
            <p className="prompt-sub">Ask about leave, pay, conduct, or any other HR policy.</p>
          </div>
        ) : (
          <ol className="messages">
            {messages.map((message) => (
              <li key={message.id} className={`message message--${message.role}`}>
                <div className="bubble">{message.content}</div>
                {message.role === 'assistant' && message.sources?.length > 0 && (
                  <p className="sources">Sources: {message.sources.join(', ')}</p>
                )}
              </li>
            ))}
            {loading && (
              <li className="message message--assistant">
                <div className="bubble bubble--loading" aria-live="polite" aria-label="Thinking">
                  <span className="dot" />
                  <span className="dot" />
                  <span className="dot" />
                </div>
              </li>
            )}
          </ol>
        )}
        <div ref={bottomRef} />
      </div>

      <form className="composer" onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask a question about HR policy..."
          autoComplete="off"
          disabled={loading}
          required
        />
        <button type="submit" disabled={loading || !question.trim()}>
          Ask
        </button>
      </form>
    </div>
  )
}

export default App
