import { useState, useMemo, useRef, useEffect } from 'react'
import './MaturityDateFilter.css'

const MONTHS_SHORT = ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']

function formatDateShort(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr + 'T00:00:00')
  const day = d.getDate()
  const month = MONTHS_SHORT[d.getMonth()]
  return `${day} ${month}`
}

function getPresets() {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())

  const startOfWeek = new Date(today)
  startOfWeek.setDate(today.getDate() - today.getDay() + (today.getDay() === 0 ? -6 : 1))

  const endOfWeek = new Date(startOfWeek)
  endOfWeek.setDate(startOfWeek.getDate() + 6)

  const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)
  const endOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0)

  const next7 = new Date(today)
  next7.setDate(today.getDate() + 7)

  return [
    {
      label: 'Сегодня',
      from: formatDate(today),
      to: formatDate(today),
    },
    {
      label: 'Завтра',
      from: formatDate(new Date(today.getTime() + 86400000)),
      to: formatDate(new Date(today.getTime() + 86400000)),
    },
    {
      label: 'Эта неделя',
      from: formatDate(startOfWeek),
      to: formatDate(endOfWeek),
    },
    {
      label: 'Этот месяц',
      from: formatDate(startOfMonth),
      to: formatDate(endOfMonth),
    },
    {
      label: 'Просроченные',
      from: '2000-01-01',
      to: formatDate(today),
    },
    {
      label: 'Следующие 7 дней',
      from: formatDate(today),
      to: formatDate(next7),
    },
  ]
}

function formatDate(d) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

export default function MaturityDateFilter({ value = ['', ''], onChange, label = 'Срок погашения' }) {
  const [from, to] = value
  const [activePreset, setActivePreset] = useState(null)
  const [localFrom, setLocalFrom] = useState(from)
  const [localTo, setLocalTo] = useState(to)
  const [focusedField, setFocusedField] = useState(null)
  const presets = useMemo(() => getPresets(), [])
  const inputRef = useRef(null)

  // Sync local state when external value changes
  useEffect(() => {
    setLocalFrom(from)
    setLocalTo(to)
    if (!from && !to) setActivePreset(null)
  }, [from, to])

  function applyPreset(preset, idx) {
    setLocalFrom(preset.from)
    setLocalTo(preset.to)
    setActivePreset(idx)
    onChange([preset.from, preset.to])
  }

  function handleLocalChange(kind, val) {
    if (kind === 'from') {
      setLocalFrom(val)
      setActivePreset(null)
      onChange([val, to])
    } else {
      setLocalTo(val)
      setActivePreset(null)
      onChange([from, val])
    }
  }

  function displayText() {
    if (activePreset !== null) return presets[activePreset].label
    if (from && to) return `${formatDateShort(from)} — ${formatDateShort(to)}`
    if (from) return formatDateShort(from)
    if (to) return `— ${formatDateShort(to)}`
    return 'Любой диапазон'
  }

  const hasValue = !!(from || to)

  return (
    <div className="maturity-date-filter" data-maturity-filter>
      <div className="maturity-date-filter-label">
        <svg
          className="maturity-date-filter-icon"
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
          <line x1="16" y1="2" x2="16" y2="6" />
          <line x1="8" y1="2" x2="8" y2="6" />
          <line x1="3" y1="10" x2="21" y2="10" />
          <rect x="7" y="14" width="3" height="3" rx="0.5" fill="currentColor" opacity="0.3" />
        </svg>
        {label}
      </div>

      <div
        className={`maturity-date-filter-display${hasValue ? '' : ' empty'}`}
        title={displayText()}
        onClick={() => inputRef.current?.showPicker?.()}
      >
        <svg
          className="maturity-date-filter-display-icon"
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
          <line x1="16" y1="2" x2="16" y2="6" />
          <line x1="8" y1="2" x2="8" y2="6" />
          <line x1="3" y1="10" x2="21" y2="10" />
        </svg>
        {displayText()}
      </div>

      <div className="maturity-date-filter-presets">
        {presets.map((preset, idx) => (
          <button
            key={idx}
            className={`maturity-preset-btn${activePreset === idx ? ' active' : ''}`}
            onClick={() => applyPreset(preset, idx)}
            type="button"
          >
            {preset.label}
          </button>
        ))}
      </div>

      <div className="maturity-date-filter-custom">
        <div className={`maturity-date-field${focusedField === 'from' ? ' focused' : ''}`}>
          <input
            ref={inputRef}
            type="date"
            className="maturity-date-input"
            value={localFrom}
            onChange={(e) => handleLocalChange('from', e.target.value)}
            onFocus={() => setFocusedField('from')}
            onBlur={() => setFocusedField(null)}
            placeholder="От"
          />
        </div>
        <span className="maturity-date-sep" aria-hidden="true">—</span>
        <div className={`maturity-date-field${focusedField === 'to' ? ' focused' : ''}`}>
          <input
            type="date"
            className="maturity-date-input"
            value={localTo}
            onChange={(e) => handleLocalChange('to', e.target.value)}
            onFocus={() => setFocusedField('to')}
            onBlur={() => setFocusedField(null)}
            placeholder="До"
          />
        </div>
      </div>
    </div>
  )
}
