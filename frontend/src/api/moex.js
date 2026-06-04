const API_BASE = import.meta.env.VITE_API_URL ?? ''

function buildQuery(params) {
  const search = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      search.set(key, String(value))
    }
  })
  const query = search.toString()
  return query ? `?${query}` : ''
}

async function request(path) {
  const response = await fetch(`${API_BASE}${path}`)
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    const detail = body.detail
    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg ?? JSON.stringify(item)).join('; ')
      : detail ?? response.statusText
    throw new Error(message || `HTTP ${response.status}`)
  }
  return response.json()
}

export function fetchInstruments(filters) {
  return request(`/api/instruments${buildQuery(filters)}`)
}

export function searchInstruments({ q, type, sort_by, order }) {
  return request(`/api/instruments/search${buildQuery({ q, type, sort_by, order })}`)
}

export function fetchInstrument(ticker) {
  return request(`/api/instruments/${encodeURIComponent(ticker)}`)
}

export function fetchTypes() {
  return request('/api/instruments/types')
}

export function fetchCount(type) {
  return request(`/api/instruments/count${buildQuery({ type })}`)
}

export function fetchHealth() {
  return request('/api/health')
}
