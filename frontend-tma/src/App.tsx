import { useEffect, useState } from 'react'
import './App.css'

interface Location {
  id: number
  name: string
  address: string
  latitude: number
  longitude: number
  is_active: boolean
}

function App() {
  const [locations, setLocations] = useState<Location[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/locations')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch')
        return res.json()
      })
      .then(data => {
        setLocations(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Error:', err)
        setError('Не вдалося завантажити локації')
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Завантаження...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="error-container">
        <p>❌ {error}</p>
        <button onClick={() => window.location.reload()}>
          Спробувати знову
        </button>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="header">
        <div className="logo">🤖☕</div>
        <h1>PerkUP</h1>
        <p className="subtitle">Система лояльності для кав'ярень</p>
        <div className="stats">
          <div className="stat">
            <span className="stat-value">0</span>
            <span className="stat-label">Балів</span>
          </div>
          <div className="stat">
            <span className="stat-value">1</span>
            <span className="stat-label">Рівень</span>
          </div>
        </div>
      </header>

      <main className="main">
        <h2>📍 Наші Локації</h2>
        <div className="locations">
          {locations.map(loc => (
            <div key={loc.id} className="location-card">
              <div className="location-header">
                <h3>{loc.name}</h3>
                <span className="location-badge">
                  {loc.is_active ? '🟢 Відкрито' : '🔴 Закрито'}
                </span>
              </div>
              <p className="location-address">{loc.address}</p>
              <div className="location-info">
                <span>📏 До {loc.radius_meters}м для check-in</span>
              </div>
              <button className="checkin-btn">
                ✓ Check-in
              </button>
            </div>
          ))}
        </div>
      </main>

      <footer className="footer">
        <p>© 2025 PerkUP. Зроблено з ❤️ та ☕</p>
      </footer>
    </div>
  )
}

export default App
