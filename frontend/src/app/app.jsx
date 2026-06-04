import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  fetchCount,
  fetchHealth,
  fetchInstruments,
  searchInstruments,
} from '../api/moex.js'

const INSTRUMENT_TYPES = [
  { id: '', label: 'Все' },
  { id: 'stock', label: 'Акции' },
  { id: 'bond', label: 'Облигации' },
  { id: 'futures', label: 'Фьючерсы' },
  { id: 'option', label: 'Опционы' },
]

const SORT_OPTIONS = [
  { id: 'ticker', label: 'Тикер' },
  { id: 'name', label: 'Название' },
  { id: 'price', label: 'Цена' },
  { id: 'volume', label: 'Объём' },
  { id: 'market_cap', label: 'Капитализация' },
]

const TYPE_LABELS = {
  stock: 'Акция',
  bond: 'Облигация',
  futures: 'Фьючерс',
  option: 'Опцион',
}

const PAGE_SIZE = 50

function formatNumber(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '—'
  return new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 2 }).format(Number(value))
}

function formatPercent(value) {
  if (value === null || value === undefined) return '—'
  return `${Number(value).toFixed(2).replace('.', ',')}%`
}

function formatDate(value) {
  if (!value) return '—'
  return new Intl.DateTimeFormat('ru-RU').format(new Date(value))
}

function FilterChip({ active, children, onClick }) {
  return (
    <button
      type="button"
      className={`filter-chip ${active ? 'filter-chip--active' : ''}`}
      onClick={onClick}
    >
      {children}
    </button>
  )
}

const emptyFilters = {
  type: '',
  sector: '',
  min_price: '',
  max_price: '',
  min_yield: '',
  max_yield: '',
  maturity_from: '',
  maturity_to: '',
  sort_by: 'ticker',
  order: 'asc',
}

export default function App() {
  const [filters, setFilters] = useState(emptyFilters)
  const [search, setSearch] = useState('')
  const [offset, setOffset] = useState(0)
  const [instruments, setInstruments] = useState([])
  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [health, setHealth] = useState(null)
  const [counts, setCounts] = useState({ total: 0, stock: 0, bond: 0, futures: 0, option: 0 })
  const [listTotal, setListTotal] = useState(0)

  const loadCounts = useCallback(async () => {
    try {
      const [total, stock, bond, futures, option] = await Promise.all([
        fetchCount(),
        fetchCount('stock'),
        fetchCount('bond'),
        fetchCount('futures'),
        fetchCount('option'),
      ])
      setCounts({
        total: total.count,
        stock: stock.count,
        bond: bond.count,
        futures: futures.count,
        option: option.count,
      })
    } catch {
      /* stats are optional */
    }
  }, [])

  const buildApiFilters = useCallback(() => {
    const payload = {
      sort_by: filters.sort_by,
      order: filters.order,
      limit: PAGE_SIZE,
      offset,
    }
    if (filters.type) payload.type = filters.type
    if (filters.sector.trim()) payload.sector = filters.sector.trim()
    if (filters.min_price !== '') payload.min_price = Number(filters.min_price)
    if (filters.max_price !== '') payload.max_price = Number(filters.max_price)
    if (filters.min_yield !== '') payload.min_yield = Number(filters.min_yield)
    if (filters.max_yield !== '') payload.max_yield = Number(filters.max_yield)
    if (filters.maturity_from) payload.maturity_from = filters.maturity_from
    if (filters.maturity_to) payload.maturity_to = filters.maturity_to
    return payload
  }, [filters, offset])

  const loadInstruments = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const query = search.trim()
      let rows
      if (query.length > 0) {
        rows = await searchInstruments({
          q: query,
          type: filters.type || undefined,
          sort_by: filters.sort_by,
          order: filters.order,
        })
        setListTotal(rows.length)
      } else {
        rows = await fetchInstruments(buildApiFilters())
        const countRes = await fetchCount(filters.type || undefined)
        setListTotal(countRes.count)
      }
      setInstruments(rows)
      if (rows.length === 0) {
        setSelected(null)
      } else {
        setSelected((prev) => {
          if (prev && rows.some((row) => row.ticker === prev.ticker)) return prev
          return rows[0]
        })
      }
    } catch (err) {
      setError(err.message ?? 'Не удалось загрузить данные')
      setInstruments([])
      setSelected(null)
    } finally {
      setLoading(false)
    }
  }, [search, filters, offset, buildApiFilters])

  useEffect(() => {
    fetchHealth().then(setHealth).catch(() => setHealth({ status: 'error' }))
    loadCounts()
  }, [loadCounts])

  useEffect(() => {
    const timer = setTimeout(() => {
      loadInstruments()
    }, 300)
    return () => clearTimeout(timer)
  }, [loadInstruments])

  const summary = useMemo(
    () => [
      { label: 'Всего', value: counts.total },
      { label: 'Акции', value: counts.stock },
      { label: 'Облигации', value: counts.bond },
      { label: 'Фьючерсы', value: counts.futures },
      { label: 'Опционы', value: counts.option },
    ],
    [counts],
  )

  const page = Math.floor(offset / PAGE_SIZE) + 1
  const totalPages = Math.max(1, Math.ceil(listTotal / PAGE_SIZE))
  const searchMode = search.trim().length > 0

  function updateFilter(key, value) {
    setOffset(0)
    setFilters((prev) => ({ ...prev, [key]: value }))
  }

  function resetFilters() {
    setOffset(0)
    setFilters(emptyFilters)
    setSearch('')
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand__dot" />
          MOEX
        </div>
        <nav className="topbar__nav">
          <button type="button" className="is-active">
            Инструменты
          </button>
        </nav>
        <div className="topbar__status">
          API:{' '}
          {health === null
            ? '…'
            : health.status === 'ok'
              ? 'подключён'
              : 'ошибка'}
          {health?.cache ? ` · кэш ${health.cache}` : ''}
        </div>
      </header>

      <section className="headline">
        <h1>
          Поиск и фильтрация <span>инструментов</span>
        </h1>
        <p>Данные Московской биржи через REST API · обновление коллектором каждые 30 мин</p>
      </section>

      <section className="summary-row">
        {summary.map((item) => (
          <article key={item.label} className="summary-cell">
            <div className="summary-cell__value">{formatNumber(item.value)}</div>
            <div className="summary-cell__label">{item.label}</div>
          </article>
        ))}
      </section>

      <div className="workspace">
        <aside className="filters-panel">
          <div className="filters-section">
            <div className="filters-title">Тип инструмента</div>
            <div className="chip-grid">
              {INSTRUMENT_TYPES.map((item) => (
                <FilterChip
                  key={item.id || 'all'}
                  active={filters.type === item.id}
                  onClick={() => updateFilter('type', item.id)}
                >
                  {item.label}
                </FilterChip>
              ))}
            </div>
          </div>

          <div className="filters-section">
            <div className="filters-title">Цена</div>
            <div className="range-row">
              <label className="field">
                <span>От</span>
                <input
                  type="number"
                  min="0"
                  placeholder="0"
                  value={filters.min_price}
                  onChange={(e) => updateFilter('min_price', e.target.value)}
                />
              </label>
              <label className="field">
                <span>До</span>
                <input
                  type="number"
                  min="0"
                  placeholder="∞"
                  value={filters.max_price}
                  onChange={(e) => updateFilter('max_price', e.target.value)}
                />
              </label>
            </div>
          </div>

          <div className="filters-section">
            <div className="filters-title">Доходность</div>
            <div className="range-row">
              <label className="field">
                <span>От, %</span>
                <input
                  type="number"
                  min="0"
                  step="0.1"
                  value={filters.min_yield}
                  onChange={(e) => updateFilter('min_yield', e.target.value)}
                />
              </label>
              <label className="field">
                <span>До, %</span>
                <input
                  type="number"
                  min="0"
                  step="0.1"
                  value={filters.max_yield}
                  onChange={(e) => updateFilter('max_yield', e.target.value)}
                />
              </label>
            </div>
          </div>

          <div className="filters-section">
            <div className="filters-title">Погашение</div>
            <label className="field">
              <span>С</span>
              <input
                type="date"
                value={filters.maturity_from}
                onChange={(e) => updateFilter('maturity_from', e.target.value)}
              />
            </label>
            <label className="field">
              <span>По</span>
              <input
                type="date"
                value={filters.maturity_to}
                onChange={(e) => updateFilter('maturity_to', e.target.value)}
              />
            </label>
          </div>

          <div className="filters-section">
            <div className="filters-title">Сектор</div>
            <label className="field">
              <span>Точное совпадение</span>
              <input
                type="text"
                placeholder="например, IT"
                value={filters.sector}
                onChange={(e) => updateFilter('sector', e.target.value)}
              />
            </label>
          </div>

          <div className="filters-section">
            <div className="filters-title">Сортировка</div>
            <label className="field">
              <span>Поле</span>
              <select
                value={filters.sort_by}
                onChange={(e) => updateFilter('sort_by', e.target.value)}
              >
                {SORT_OPTIONS.map((opt) => (
                  <option key={opt.id} value={opt.id}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </label>
            <div className="chip-grid">
              <FilterChip
                active={filters.order === 'asc'}
                onClick={() => updateFilter('order', 'asc')}
              >
                ↑ По возрастанию
              </FilterChip>
              <FilterChip
                active={filters.order === 'desc'}
                onClick={() => updateFilter('order', 'desc')}
              >
                ↓ По убыванию
              </FilterChip>
            </div>
          </div>

          <button type="button" className="apply-button" onClick={resetFilters}>
            Сбросить фильтры
          </button>
        </aside>

        <main className="results-panel">
          <div className="results-search">
            <input
              type="search"
              placeholder="Поиск по тикеру или названию…"
              value={search}
              onChange={(e) => {
                setOffset(0)
                setSearch(e.target.value)
              }}
            />
          </div>

          <div className="results-toolbar">
            <div className="results-meta">
              {loading ? 'Загрузка…' : `Показано ${instruments.length} из ${formatNumber(listTotal)}`}
              {searchMode ? ' · режим поиска' : ''}
            </div>
            {!searchMode && (
              <div className="results-meta">
                <button
                  type="button"
                  className="filter-chip"
                  disabled={offset === 0 || loading}
                  onClick={() => setOffset((v) => Math.max(0, v - PAGE_SIZE))}
                >
                  ← Назад
                </button>
                <span>
                  {page} / {totalPages}
                </span>
                <button
                  type="button"
                  className="filter-chip"
                  disabled={offset + PAGE_SIZE >= listTotal || loading}
                  onClick={() => setOffset((v) => v + PAGE_SIZE)}
                >
                  Вперёд →
                </button>
              </div>
            )}
          </div>

          {error && <p className="api-error">{error}</p>}

          <div className="table-wrap">
            <table className="bonds-table">
              <thead>
                <tr>
                  <th>Инструмент</th>
                  <th>Тип</th>
                  <th>Эмитент / сектор</th>
                  <th>Цена</th>
                  <th>Доходность</th>
                  <th>Объём</th>
                  <th>Погашение</th>
                </tr>
              </thead>
              <tbody>
                {!loading && instruments.length === 0 && (
                  <tr>
                    <td colSpan={7}>Ничего не найдено. Измените фильтры или запустите коллектор.</td>
                  </tr>
                )}
                {instruments.map((row) => (
                  <tr
                    key={row.ticker}
                    className={selected?.ticker === row.ticker ? 'is-selected' : ''}
                    onClick={() => setSelected(row)}
                  >
                    <td>
                      <div className="instrument-cell">
                        <div className="instrument-line" />
                        <div>
                          <div className="instrument-ticker">{row.ticker}</div>
                          <div className="issuer-sub">{row.name}</div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className="instrument-badge">
                        {TYPE_LABELS[row.type] ?? row.type}
                      </span>
                    </td>
                    <td>
                      <div className="issuer-name">{row.issuer ?? '—'}</div>
                      <div className="issuer-sub">{row.sector ?? '—'}</div>
                    </td>
                    <td className="numeric-cell">
                      {formatNumber(row.price)} {row.currency ?? ''}
                    </td>
                    <td className="numeric-cell">{formatPercent(row.yield)}</td>
                    <td className="numeric-cell">{formatNumber(row.volume)}</td>
                    <td className="numeric-cell">{formatDate(row.maturity_date)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {selected && (
            <section className="details-inline">
              <div>
                <span>Выбранный инструмент</span>
                <strong>
                  {selected.ticker} — {selected.name}
                </strong>
              </div>
              <div>
                <span>Капитализация</span>
                <strong>{formatNumber(selected.market_cap)}</strong>
              </div>
              <div>
                <span>Страйк / тип опциона</span>
                <strong>
                  {formatNumber(selected.strike_price)} / {selected.option_type ?? '—'}
                </strong>
              </div>
              <div>
                <span>Волатильность</span>
                <strong>{formatPercent(selected.volatility)}</strong>
              </div>
              <div>
                <span>Обновлено</span>
                <strong>{formatDate(selected.updated_at)}</strong>
              </div>
            </section>
          )}
        </main>
      </div>
    </div>
  )
}
