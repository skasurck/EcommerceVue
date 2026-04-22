import api from '@/axios'

const VISITOR_KEY = 'mk_vid'
const CONSENT_KEY = 'mk_consent'
const BATCH_SIZE = 10
const FLUSH_MS = 8000
const DEDUPE_WINDOW_MS = 2000

function uuid() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID()
  }
  // Fallback razonable
  return 'mk-' + Math.random().toString(36).slice(2) + Date.now().toString(36)
}

export function getVisitorId() {
  try {
    let v = localStorage.getItem(VISITOR_KEY)
    if (!v) {
      v = uuid()
      localStorage.setItem(VISITOR_KEY, v)
    }
    return v
  } catch {
    return ''
  }
}

export function getConsent() {
  try {
    return JSON.parse(localStorage.getItem(CONSENT_KEY) || 'null')
  } catch {
    return null
  }
}

export function hasAnalyticsConsent() {
  return getConsent()?.analytics === true
}

export function setConsent(consent) {
  const payload = {
    analytics: !!consent?.analytics,
    personalizacion: !!consent?.personalizacion,
    v: consent?.v || 'v1',
    ts: Date.now(),
  }
  try {
    localStorage.setItem(CONSENT_KEY, JSON.stringify(payload))
  } catch { /* ignore */ }

  api.post('/tracking/consentimiento/', payload, {
    headers: { 'X-Visitor-Id': getVisitorId() },
  }).catch(() => { /* nunca bloquear UX */ })

  return payload
}

const queue = []
let timer = null

function flush(useBeacon = false) {
  if (!queue.length) return
  const batch = queue.splice(0, 50)
  const body = { eventos: batch }

  if (useBeacon && typeof navigator !== 'undefined' && navigator.sendBeacon) {
    try {
      const url = `${api.defaults.baseURL}tracking/eventos/`.replace(/\/+/g, '/')
        .replace(':/', '://')
      const blob = new Blob([JSON.stringify(body)], { type: 'application/json' })
      navigator.sendBeacon(url, blob)
      return
    } catch { /* fall through to axios */ }
  }

  api.post('/tracking/eventos/', body, {
    headers: { 'X-Visitor-Id': getVisitorId() },
  }).catch(() => { /* fire-and-forget */ })
}

function schedule() {
  if (queue.length >= BATCH_SIZE) {
    flush()
    return
  }
  if (timer) return
  timer = setTimeout(() => { timer = null; flush() }, FLUSH_MS)
}

const recent = new Map()
function isDuplicate(tipo, productoId) {
  if (!productoId) return false
  const key = `${tipo}:${productoId}`
  const now = Date.now()
  const prev = recent.get(key)
  if (prev && now - prev < DEDUPE_WINDOW_MS) return true
  recent.set(key, now)
  if (recent.size > 200) {
    const cutoff = now - DEDUPE_WINDOW_MS * 5
    for (const [k, t] of recent) if (t < cutoff) recent.delete(k)
  }
  return false
}

export function trackEvento(tipo, payload = {}) {
  if (!tipo) return
  if (!hasAnalyticsConsent()) return
  if (isDuplicate(tipo, payload.producto_id)) return

  queue.push({
    tipo,
    producto_id: payload.producto_id ?? null,
    categoria_id: payload.categoria_id ?? null,
    metadata: payload.metadata ?? {},
    ts: Date.now(),
  })
  schedule()
}

let _bound = false
export function initTracking() {
  if (_bound || typeof window === 'undefined') return
  _bound = true
  // Asegura visitor id desde el primer render
  getVisitorId()
  window.addEventListener('pagehide', () => flush(true))
  window.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') flush(true)
  })
}

export const _internal = { flush, queue }
