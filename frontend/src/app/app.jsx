import { useCallback, useEffect, useRef, useState } from 'react'
import ThemeToggle from '../components/common/ThemeToggle.jsx'
import MaturityDateFilter from '../components/filters/MaturityDateFilter.jsx'
import OptionTypeToggle from '../components/filters/OptionTypeToggle.jsx'

const API = '/api'

  const TYPE_LABEL = { stock: 'Акция', bond: 'Облигация', futures: 'Фьючерс', option: 'Опцион' }
  const STRIPE_COLOR = { stock: '#3B82F6', bond: '#22C55E', futures: '#F97316', option: '#D946EF' }
  const BADGE_CLASS = { stock: 'b-stock', bond: 'b-bond', futures: 'b-futures', option: 'b-option' }
  const OPTION_TYPE_LABEL = { C: 'Call', P: 'Put' }
  const OPTION_TYPE_COLOR = { C: '#22C55E', P: '#E879F9' }

const TYPES = [
  { id: '', label: 'Все инструменты' },
  { id: 'stock', label: 'Акции' },
  { id: 'bond', label: 'Облигации' },
  { id: 'futures', label: 'Фьючерсы' },
  { id: 'option', label: 'Опционы' },
]

const ALL_SORTS = [
  { sort: 'ticker', order: 'asc', label: 'Тикер A→Z' },
  { sort: 'price', order: 'desc', label: 'Цена ↓' },
  { sort: 'price', order: 'asc', label: 'Цена ↑' },
  { sort: 'volume', order: 'desc', label: 'Объём ↓' },
  { sort: 'volume', order: 'asc', label: 'Объём ↑' },
  { sort: 'market_cap', order: 'desc', label: 'Капитализация ↓' },
  { sort: 'market_cap', order: 'asc', label: 'Капитализация ↑' },
  { sort: 'yield', order: 'desc', label: 'Доходность ↓' },
  { sort: 'yield', order: 'asc', label: 'Доходность ↑' },
  { sort: 'strike_price', order: 'desc', label: 'Страйк ↓' },
  { sort: 'strike_price', order: 'asc', label: 'Страйк ↑' },
]

function fmt(v, d = 2) {
  if (v == null) return '—'
  return Number(v).toLocaleString('ru', { minimumFractionDigits: d, maximumFractionDigits: d })
}

function fmtVol(v) {
  if (!v) return '—'
  if (v >= 1e9) return (v / 1e9).toFixed(1) + ' млрд'
  if (v >= 1e6) return (v / 1e6).toFixed(1) + ' млн'
  if (v >= 1e3) return (v / 1e3).toFixed(0) + ' тыс'
  return Number(v).toLocaleString('ru')
}

function getMarketStatus() {
  const now = new Date()
  const h = now.getHours(), m = now.getMinutes(), d = now.getDay()
  const isWeekday = d >= 1 && d <= 5
  const isOpen = isWeekday && (h > 10 || (h === 10 && m >= 0)) && h < 19
  const time = now.toLocaleTimeString('ru', { hour: '2-digit', minute: '2-digit' })
  return { isOpen, time }
}

export default function App() {
  const [curType, setCurType] = useState('')
  const [curPage, setCurPage] = useState(0)
  const [perPage, setPerPage] = useState(20)
  const [sortKey, setSortKey] = useState(0)
  const [search, setSearch] = useState('')
  const [instruments, setInstruments] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [counts, setCounts] = useState({ total: 0, stock: 0, bond: 0, futures: 0, option: 0 })
  const [tickerData, setTickerData] = useState([])
  const [marketStatus, setMarketStatus] = useState(getMarketStatus)
  const [modal, setModal] = useState(null)
  const [modalLoading, setModalLoading] = useState(false)
  const [toastMsg, setToastMsg] = useState('')
  const [showAdv, setShowAdv] = useState(false)
  const [fMinP, setFMinP] = useState('')
  const [fMaxP, setFMaxP] = useState('')
  const [fMinS, setFMinS] = useState('')
  const [fMaxS, setFMaxS] = useState('')
  const [fMinY, setFMinY] = useState('')
  const [fMaxY, setFMaxY] = useState('')
  const [fD1, setFD1] = useState('')
  const [fD2, setFD2] = useState('')
  const [fMinV, setFMinV] = useState('')
  const [fMaxV, setFMaxV] = useState('')
  const [fOpt, setFOpt] = useState('')
  const [showNullPrice, setShowNullPrice] = useState(true)
  const [showNullPriceFilter, setShowNullPriceFilter] = useState(true)
  const searchTimer = useRef(null)
  const toastTimer = useRef(null)
  const SORTS = curType === 'option'
    ? ALL_SORTS.filter(s => ['ticker', 'price', 'strike_price'].includes(s.sort))
    : curType === 'stock'
    ? ALL_SORTS.filter(s => ['ticker', 'price', 'volume', 'market_cap'].includes(s.sort))
    : curType === 'bond'
    ? ALL_SORTS.filter(s => ['ticker', 'price', 'volume', 'yield'].includes(s.sort))
    : curType === 'futures'
    ? ALL_SORTS.filter(s => ['ticker', 'price', 'volume'].includes(s.sort))
    : ALL_SORTS
  const curSort = SORTS[sortKey].sort
  const curOrder = SORTS[sortKey].order

  function toast(msg) {
    setToastMsg(msg)
    clearTimeout(toastTimer.current)
    toastTimer.current = setTimeout(() => setToastMsg(''), 3000)
  }

  const loadStats = useCallback(async () => {
    try {
      const [all, stock, bond, fut, opt] = await Promise.all([
        fetch(`${API}/instruments/count`).then(r => r.json()),
        fetch(`${API}/instruments/count?type=stock`).then(r => r.json()),
        fetch(`${API}/instruments/count?type=bond`).then(r => r.json()),
        fetch(`${API}/instruments/count?type=futures`).then(r => r.json()),
        fetch(`${API}/instruments/count?type=option`).then(r => r.json()),
      ])
      setCounts({ total: all.count, stock: stock.count, bond: bond.count, futures: fut.count, option: opt.count })
    } catch { /* optional */ }
  }, [])

  const loadTicker = useCallback(async () => {
    try {
      const r = await fetch(`${API}/instruments?type=stock&limit=14&sort_by=market_cap&order=desc`)
      const data = await r.json()
      setTickerData(data.filter(s => s.price))
    } catch { /* optional */ }
  }, [])

  const loadInstruments = useCallback(async () => {
    setLoading(true)
    try {
      let data, tot
      const q = search.trim()
      if (q) {
        const tp = curType ? `&type=${curType}` : ''
        const r = await fetch(`${API}/instruments/search?q=${encodeURIComponent(q)}${tp}&sort_by=${curSort}&order=${curOrder}`)
        const all = await r.json()
        tot = all.length
        data = all.slice(curPage * perPage, (curPage + 1) * perPage)
      } else {
        const p = new URLSearchParams()
        if (curType) p.set('type', curType)
        if (curType === 'option') {
        } else if (curType === 'futures') {
          if (fMinP) p.set('min_price', fMinP)
          if (fMaxP) p.set('max_price', fMaxP)
          if (fMinV) p.set('min_volume', fMinV)
          if (fMaxV) p.set('max_volume', fMaxV)
        } else {
          if (fMinP) p.set('min_price', fMinP)
          if (fMaxP) p.set('max_price', fMaxP)
        }
        if (curType !== 'option' && fMinY) p.set('min_yield', fMinY)
        if (curType !== 'option' && fMaxY) p.set('max_yield', fMaxY)
        if (fD1) p.set('maturity_from', fD1)
        if (fD2) p.set('maturity_to', fD2)
        if (curType !== 'option') p.set('show_null_price', showNullPriceFilter ? '1' : '0')
        if (curType === 'option' && fOpt) p.set('option_type', fOpt)
        if (curType === 'option' && fMinS) p.set('min_strike', fMinS)
        if (curType === 'option' && fMaxS) p.set('max_strike', fMaxS)
        if (curType === 'futures' && fMinV) p.set('min_volume', fMinV)
        if (curType === 'futures' && fMaxV) p.set('max_volume', fMaxV)
        p.set('sort_by', curSort)
        p.set('order', curOrder)
        p.set('limit', String(perPage))
        p.set('offset', String(curPage * perPage))
        const r = await fetch(`${API}/instruments?${p}`)
        data = await r.json()
        const countP = new URLSearchParams()
        if (curType) countP.set('type', curType)
        if (curType === 'option') {
          // strike filters applied unconditionally below
        } else if (curType === 'futures') {
          if (fMinP) countP.set('min_price', fMinP)
          if (fMaxP) countP.set('max_price', fMaxP)
          // volume filters applied unconditionally below
        } else {
          if (fMinP) countP.set('min_price', fMinP)
          if (fMaxP) countP.set('max_price', fMaxP)
        }
        if (curType !== 'option' && fMinY) countP.set('min_yield', fMinY)
        if (curType !== 'option' && fMaxY) countP.set('max_yield', fMaxY)
        if (fD1) countP.set('maturity_from', fD1)
        if (fD2) countP.set('maturity_to', fD2)
        if (curType !== 'option') countP.set('show_null_price', showNullPriceFilter ? '1' : '0')
        if (curType === 'option' && fOpt) countP.set('option_type', fOpt)
        if (curType === 'option' && fMinS) countP.set('min_strike', fMinS)
        if (curType === 'option' && fMaxS) countP.set('max_strike', fMaxS)
        if (curType === 'futures' && fMinV) countP.set('min_volume', fMinV)
        if (curType === 'futures' && fMaxV) countP.set('max_volume', fMaxV)
        const countR = await fetch(`${API}/instruments/count/full?${countP}`)
        const countData = await countR.json()
        tot = countData.total
      }
      setInstruments(data)
      setTotal(tot)
    } catch {
      setInstruments([])
      setTotal(0)
      toast('Ошибка подключения к API')
    } finally {
      setLoading(false)
    }
  }, [search, curType, curSort, curOrder, curPage, perPage, fMinS, fMaxS, fMinP, fMaxP, fMinV, fMaxV, fMinY, fMaxY, fD1, fD2, showNullPriceFilter, fOpt])

  useEffect(() => {
    loadStats()
    loadTicker()
    fetch(`${API}/health`).then(r => r.json()).then(d => { if (d.status === 'ok') toast('API подключён') }).catch(() => toast('API недоступен'))
    const iv = setInterval(() => setMarketStatus(getMarketStatus()), 60000)
    return () => clearInterval(iv)
  }, [loadStats, loadTicker])

  useEffect(() => { loadInstruments() }, [loadInstruments])

  useEffect(() => {
    const iv = setInterval(() => { loadStats(); loadTicker(); loadInstruments() }, 30 * 60 * 1000)
    return () => clearInterval(iv)
  }, [loadStats, loadTicker, loadInstruments])

  function onSearch(e) {
    const val = e.target.value
    setSearch(val)
    clearTimeout(searchTimer.current)
    searchTimer.current = setTimeout(() => setCurPage(0), 350)
  }

  function selectType(id) {
    setCurType(id); setCurPage(0)
    setFMinP(''); setFMaxP(''); setFMinS(''); setFMaxS(''); setFMinY(''); setFMaxY(''); setFMinV(''); setFMaxV('')
    setFD1(''); setFD2(''); setFOpt('')
    setShowAdv(false)
  }
  function selectSort(idx) { setSortKey(idx); setCurPage(0) }
  function applyFilters() { setCurPage(0) }
  function resetFilters() {
    setSearch(''); setFMinP(''); setFMaxP(''); setFMinS(''); setFMaxS(''); setFMinY(''); setFMaxY(''); setFMinV(''); setFMaxV('')
    setFD1(''); setFD2(''); setFOpt('')
    setShowNullPriceFilter(true)
    setCurType(''); setCurPage(0); setSortKey(0)
  }
  function goPage(p) { setCurPage(p); window.scrollTo({ top: 160, behavior: 'smooth' }) }

  async function openModal(ticker) {
    setModal({ ticker }); setModalLoading(true)
    try {
      const r = await fetch(`${API}/instruments/${ticker}`)
      setModal(await r.json())
    } catch { setModal({ ticker, error: true }) }
    finally { setModalLoading(false) }
  }
  function closeModal() { setModal(null) }

  useEffect(() => {
    const fn = e => { if (e.key === 'Escape') closeModal() }
    document.addEventListener('keydown', fn)
    return () => document.removeEventListener('keydown', fn)
  }, [])

  const pages = Math.ceil(total / perPage)
  const ps = Math.max(0, curPage - 2), pe = Math.min(pages, ps + 5)
  const tickerLoop = [...tickerData, ...tickerData]

  return (
    <>
      <div className="ticker-wrap">
        <div className="ticker-inner">
          {tickerLoop.map((s, i) => (
            <span className="t-item" key={`${s.ticker}-${i}`}>
              <span className="t-ticker">{s.ticker}</span>
              <span className="t-price">{s.price ? fmt(s.price) : '—'}</span>
            </span>
          ))}
        </div>
      </div>
      <header className="site-header">
        <div className="logo"><div className="logo-mark" />MOEX</div>
        <nav className="header-nav">
          <span className="nav-item">Главная</span>
          <span className="nav-item active">Инструменты</span>
          <span className="nav-item">Индексы</span>
          <span className="nav-item">О бирже</span>
        </nav>
        <div className="header-right">
          <div className="market-status">
            <div className="status-dot" style={{ background: marketStatus.isOpen ? 'var(--green2)' : 'var(--text3)' }} />
            <span>{marketStatus.isOpen ? 'Биржа открыта' : 'Биржа закрыта'}</span>
          </div>
          <div className="update-time">Обновлено: {marketStatus.time}</div>
        </div>
      </header>
      <div className="hero">
        <div className="hero-top"><div>
          <div className="hero-title">Подбор <span>финансовых инструментов</span></div>
          <div className="hero-sub">Акции · Облигации · Фьючерсы · Опционы — данные Московской биржи</div>
        </div></div>
      </div>
      <div className="layout">
        <aside className="sidebar">
          <div className="s-section">
            <div className="s-label">Тип инструмента</div>
            <div className="type-list">
              {TYPES.map(t => (
                <div key={t.id || 'all'} className={`type-row${curType === t.id ? ' active' : ''}`} onClick={() => selectType(t.id)}>
                  <div className="type-indicator" />
                  <span className="type-name">{t.label}</span>
                  <span className="type-count">{t.id ? (counts[t.id] ? counts[t.id].toLocaleString('ru') : '—') : (counts.total ? counts.total.toLocaleString('ru') : '—')}</span>
                </div>
              ))}
            </div>
          </div>
          <hr className="s-divider" />
          <div className="s-section">
            <div className="s-label">Основные фильтры</div>
            {curType === 'option' ? (
              <div className="f-group"><div className="f-label">Страйк</div>
                <div className="f-row">
                  <input type="number" placeholder="от" min="0" value={fMinS} onChange={e => setFMinS(e.target.value)} />
                  <span className="f-sep">—</span>
                  <input type="number" placeholder="до" min="0" value={fMaxS} onChange={e => setFMaxS(e.target.value)} />
                </div>
              </div>
            ) : (
              <div className="f-group"><div className="f-label">Цена</div>
                <div className="f-row">
                  <input type="number" placeholder="от" min="0" value={fMinP} onChange={e => setFMinP(e.target.value)} />
                  <span className="f-sep">—</span>
                  <input type="number" placeholder="до" min="0" value={fMaxP} onChange={e => setFMaxP(e.target.value)} />
                </div>
              </div>
            )}
            <div className="f-group" style={{ marginTop: '8px' }}>
              {curType !== 'option' && <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '11px', color: 'var(--text2)' }}>
                <input
                  type="checkbox"
                  checked={showNullPriceFilter}
                  onChange={e => setShowNullPriceFilter(e.target.checked)}
                  style={{ width: 'auto', accentColor: 'var(--accent)' }}
                />
                Показывать инструменты без цены
              </label>}
            </div>
            {curType === 'bond' && <button type="button" className={`adv-toggle${showAdv ? ' open' : ''}`} onClick={() => setShowAdv(v => !v)}>
              <span className="adv-arrow">▾</span> Расширенные фильтры
            </button>}
            {curType === 'futures' && <button type="button" className={`adv-toggle${showAdv ? ' open' : ''}`} onClick={() => setShowAdv(v => !v)}>
              <span className="adv-arrow">▾</span> Расширенные фильтры
            </button>}
            {curType === 'option' && <button type="button" className={`adv-toggle${showAdv ? ' open' : ''}`} onClick={() => setShowAdv(v => !v)}>
              <span className="adv-arrow">▾</span> Расширенные фильтры
            </button>}
            {showAdv && <div className="adv-body">
              {curType === 'option' && <OptionTypeToggle value={fOpt} onChange={setFOpt} />}
              {curType === 'bond' && <MaturityDateFilter value={[fD1, fD2]} onChange={([from, to]) => { setFD1(from); setFD2(to) }} />}
              {curType === 'bond' && <div className="f-group"><div className="f-label">Доходность, % (доп.)</div>
                <div className="f-row">
                <input type="number" placeholder="от" step="0.1" min="0" value={fMinY} onChange={e => setFMinY(e.target.value)} />
                <span className="f-sep">—</span>
                <input type="number" placeholder="до" step="0.1" min="0" value={fMaxY} onChange={e => setFMaxY(e.target.value)} />
                </div>
              </div>}
              {curType === 'futures' && <div className="f-group"><div className="f-label">Объём</div>
                <div className="f-row">
                  <input type="number" placeholder="от" min="0" value={fMinV} onChange={e => setFMinV(e.target.value)} />
                  <span className="f-sep">—</span>
                  <input type="number" placeholder="до" min="0" value={fMaxV} onChange={e => setFMaxV(e.target.value)} />
                </div>
              </div>}
            </div>}
          </div>
          <div style={{ marginTop: '8px' }}>
            <button className="btn-clear" onClick={resetFilters}>Сбросить фильтры</button>
          </div>
        </aside>
        <main className="content">
          <div className="search-wrap">
            <input className="search-input" type="text" placeholder="Поиск по тикеру или названию..." value={search} onChange={onSearch} />
            <span className="search-ico">⌕</span>
          </div>
          <div className="toolbar">
            <div className="sort-pills">
              <span className="sort-label">Сортировка:</span>
              {SORTS.map((s, i) => (
                <div key={i} className={`pill${sortKey === i ? ' active' : ''}`} onClick={() => selectSort(i)}>{s.label}</div>
              ))}
            </div>
            <div className="toolbar-right">
              <span className="found-count">Найдено: <b>{total.toLocaleString('ru')}</b></span>
              <select className="per-page-select" value={perPage} onChange={e => { setPerPage(+e.target.value); setCurPage(0) }}>
                <option value={20}>20</option><option value={50}>50</option><option value={100}>100</option>
              </select>
            </div>
          </div>
          <div className="table-scroll">
            <div className="table-header" style={{ gridTemplateColumns: curType === 'option' ? '200px 1fr 90px 90px' : curType === 'bond' ? '200px 1fr 90px 90px 100px' : curType === 'stock' ? '200px 1fr 90px 90px 100px' : curType === 'futures' ? '200px 1fr 90px 90px' : '200px 1fr 70px 80px 50px' }}>
              {curType === 'option' ? (
                <>
                  <div className="th">Инструмент</div>
                  <div className="th">Тип</div>
                  <div className="th">Страйк</div>
                  <div className="th">Цена</div>
                </>
              ) : curType === 'bond' ? (
                <>
                  <div className="th">Инструмент</div>
                  <div className="th">Название</div>
                  <div className="th right">Цена</div>
                  <div className="th right">Объём</div>
                  <div className="th right">Доходность</div>
                </>
              ) : curType === 'stock' ? (
                <>
                  <div className="th">Инструмент</div>
                  <div className="th">Название</div>
                  <div className="th right">Цена</div>
                  <div className="th right">Объём</div>
                  <div className="th right">Капитализация</div>
                </>
              ) : curType === 'futures' ? (
                <>
                  <div className="th">Инструмент</div>
                  <div className="th">Название</div>
                  <div className="th right">Цена</div>
                  <div className="th right">Объём</div>
                </>
              ) : (
                <>
                  <div className="th">Инструмент</div>
                  <div className="th">Название</div>
                  <div className="th right">Доп. инфо</div>
                </>
              )}
            </div>
          </div>
          <div className="cards">
            {loading && Array.from({ length: 6 }).map((_, i) => <div className="skel" key={i} />)}
            {!loading && instruments.length === 0 && <div className="empty-msg">
              {total === 0
                ? 'Инструменты не найдены.'
                : 'Ничего не найдено. Измените фильтры.'}
            </div>}
            {!loading && instruments.map(item => {
              const type = item.type || ''
              const hasPrice = item.price > 0
              const stripe = STRIPE_COLOR[type] || '#555'
              const meta = []
              if (item.issuer) meta.push(item.issuer)
              if (item.sector) meta.push(item.sector)
              const yieldColor = item.yield && item.yield > 0 ? 'var(--green2)' : (item.yield && item.yield < 0 ? '#EF4444' : 'var(--text2)')
              const yieldDisplay = item.yield != null ? `${item.yield}%` : '—'
              const marketCapDisplay = item.market_cap ? fmtVol(item.market_cap) : '—'
              const priceDisplay = hasPrice ? fmt(item.price) : 'нет данных'
              const volDisplay = hasPrice ? fmtVol(item.volume) : 'нет данных'
              const strikeDisplay = item.strike_price ? `${Number(item.strike_price).toLocaleString('ru')}` : '—'
              const optionLabel = OPTION_TYPE_LABEL[item.option_type] || item.option_type || '—'
              const optionColor = OPTION_TYPE_COLOR[item.option_type] || 'var(--text2)'
              
              if (curType === 'option') {
                const hasPrice = item.price !== null && item.price !== undefined && item.price !== '';
                return (
                  <div 
                    className={`card${!hasPrice ? ' no-price' : ''} card-option`} 
                    key={item.ticker} 
                    onClick={() => openModal(item.ticker)}
                  >
                    <div className="card-ticker-col">
                      <div className="card-stripe" style={{ background: stripe }} />
                      <div>
                        <span className="card-ticker">
                          {item.ticker}
                          {curType === '' && (
                            <span className={`card-badge ${BADGE_CLASS[type] || ''}`}>
                              {TYPE_LABEL[type] || type}
                            </span>
                          )}
                        </span>
                      </div>
                    </div>
                    <div className="card-name-col">
                      <div className="card-name" style={{ color: optionColor, fontWeight: 600 }}>
                        {optionLabel}
                      </div>
                    </div>
                    <div className="card-price-col" style={{ textAlign: 'right', paddingLeft: '4px' }}>
                      <div className="card-price">{strikeDisplay}</div>
                    </div>
                    <div className="card-extra-col" style={{ textAlign: 'right', paddingRight: '4px' }}>
                      <div className={`card-extra${!hasPrice ? ' empty' : ''}`}>
                        {item.price || 'нет данных'}
                      </div>
                    </div>
                  </div>
                )
              }
              
              if (curType === 'bond') {
                return (
                  <div className={`card${!hasPrice ? ' no-price' : ''} card-bond-only`} key={item.ticker} onClick={() => openModal(item.ticker)}>
                    <div className="card-ticker-col">
                      <div className="card-stripe" style={{ background: stripe }} />
                      <div><span className="card-ticker">{item.ticker}{curType === '' && <span className={`card-badge ${BADGE_CLASS[type] || ''}`}>{TYPE_LABEL[type] || type}</span>}</span></div>
                    </div>
                    <div className="card-name-col">
                      <div className="card-name">{item.name || '—'}</div>
                      {meta.length > 0 && <div className="card-meta">{meta.join(' · ')}</div>}
                    </div>
                    <div className="card-price-col">
                      <div className={`card-price${!hasPrice ? ' empty' : ''}`}>{priceDisplay}</div>
                      <div className="card-currency">{item.currency || ''}</div>
                    </div>
                    <div className="card-vol-col"><div className="card-vol">{volDisplay}</div></div>
                    <div className="card-extra-col"><div className="card-extra yield-val" style={{ color: yieldColor }}>{yieldDisplay}</div></div>
                  </div>
                )
              }
              
              if (curType === 'stock') {
                return (
                  <div className={`card${!hasPrice ? ' no-price' : ''} card-stock-only`} key={item.ticker} onClick={() => openModal(item.ticker)}>
                    <div className="card-ticker-col">
                      <div className="card-stripe" style={{ background: stripe }} />
                      <div><span className="card-ticker">{item.ticker}{curType === '' && <span className={`card-badge ${BADGE_CLASS[type] || ''}`}>{TYPE_LABEL[type] || type}</span>}</span></div>
                    </div>
                    <div className="card-name-col">
                      <div className="card-name">{item.name || '—'}</div>
                      {meta.length > 0 && <div className="card-meta">{meta.join(' · ')}</div>}
                    </div>
                    <div className="card-price-col">
                      <div className={`card-price${!hasPrice ? ' empty' : ''}`}>{priceDisplay}</div>
                      <div className="card-currency">{item.currency || ''}</div>
                    </div>
                    <div className="card-vol-col"><div className="card-vol">{volDisplay}</div></div>
                    <div className="card-extra-col"><div className="card-extra">{marketCapDisplay}</div></div>
                  </div>
                )
              }
              
              if (curType === 'futures') {
                return (
                  <div className={`card${!hasPrice ? ' no-price' : ''}`} key={item.ticker} onClick={() => openModal(item.ticker)}>
                    <div className="card-ticker-col">
                      <div className="card-stripe" style={{ background: stripe }} />
                      <div><span className="card-ticker">{item.ticker}{curType === '' && <span className={`card-badge ${BADGE_CLASS[type] || ''}`}>{TYPE_LABEL[type] || type}</span>}</span></div>
                    </div>
                    <div className="card-name-col">
                      <div className="card-name">{item.name || '—'}</div>
                      {meta.length > 0 && <div className="card-meta">{meta.join(' · ')}</div>}
                    </div>
                    <div className="card-price-col">
                      <div className={`card-price${!hasPrice ? ' empty' : ''}`}>{priceDisplay}</div>
                      <div className="card-currency">{item.currency || ''}</div>
                    </div>
                    <div className="card-vol-col"><div className="card-vol">{volDisplay}</div></div>
                  </div>
                )
              }
              
              if (curType === '') {
                if (type === 'bond') {
                  return (
                    <div className={`card card-all${!hasPrice ? ' no-price' : ''}`} key={item.ticker} onClick={() => openModal(item.ticker)}>
                      <div className="card-ticker-col">
                        <div className="card-stripe" style={{ background: stripe }} />
                      <div><span className="card-ticker">{item.ticker}{curType === '' && <span className={`card-badge ${BADGE_CLASS[type] || ''}`}>{TYPE_LABEL[type] || type}</span>}</span></div>
                    </div>
                    <div className="card-name-col">
                      <div className="card-name">{item.name || '—'}</div>
                      {meta.length > 0 && <div className="card-meta">{meta.join(' · ')}</div>}
                    </div>
                    <div className="card-extra-col"><div className="card-extra yield-val" style={{ color: yieldColor }}>{yieldDisplay}</div></div>
                    </div>
                  )
                }
                if (type === 'stock') {
                  return (
                    <div className={`card card-all${!hasPrice ? ' no-price' : ''}`} key={item.ticker} onClick={() => openModal(item.ticker)}>
                      <div className="card-ticker-col">
                        <div className="card-stripe" style={{ background: stripe }} />
                        <div><span className="card-ticker">{item.ticker}{curType === '' && <span className={`card-badge ${BADGE_CLASS[type] || ''}`}>{TYPE_LABEL[type] || type}</span>}</span></div>
                      </div>
                      <div className="card-name-col">
                        <div className="card-name">{item.name || '—'}</div>
                        {meta.length > 0 && <div className="card-meta">{meta.join(' · ')}</div>}
                      </div>
                      <div className="card-extra-col"><div className="card-extra">{marketCapDisplay}</div></div>
                    </div>
                  )
                }
                if (type === 'option') {
                  return (
                    <div className="card card-all" key={item.ticker} onClick={() => openModal(item.ticker)}>
                      <div className="card-ticker-col">
                        <div className="card-stripe" style={{ background: stripe }} />
                      <div><span className="card-ticker">{item.ticker}{curType === '' && <span className={`card-badge ${BADGE_CLASS[type] || ''}`}>{TYPE_LABEL[type] || type}</span>}</span></div>
                    </div>
                    <div className="card-name-col">
                      <div className="card-name">{item.name || '—'}</div>
                    </div>
                    <div className="card-extra-col" style={{ textAlign: 'right' }}>
                      <div className="card-extra">{strikeDisplay}</div>
                      </div>
                    </div>
                  )
                }
                if (type === 'futures') {
                  return (
                    <div className={`card card-all${!hasPrice ? ' no-price' : ''}`} key={item.ticker} onClick={() => openModal(item.ticker)}>
                      <div className="card-ticker-col">
                        <div className="card-stripe" style={{ background: stripe }} />
                      <div><span className="card-ticker">{item.ticker}{curType === '' && <span className={`card-badge ${BADGE_CLASS[type] || ''}`}>{TYPE_LABEL[type] || type}</span>}</span></div>
                    </div>
                    <div className="card-name-col">
                      <div className="card-name">{item.name || '—'}</div>
                      {meta.length > 0 && <div className="card-meta">{meta.join(' · ')}</div>}
                    </div>
                    <div className="card-extra-col" style={{ textAlign: 'right' }}>
                      <div className="card-extra">{priceDisplay}</div>
                      </div>
                    </div>
                  )
                }
              }
              
              return (
                <div className={`card card-all${!hasPrice ? ' no-price' : ''}`} key={item.ticker} onClick={() => openModal(item.ticker)}>
                  <div className="card-ticker-col">
                    <div className="card-stripe" style={{ background: stripe }} />
                    <div><span className="card-ticker">{item.ticker}{curType === '' && <span className={`card-badge ${BADGE_CLASS[type] || ''}`}>{TYPE_LABEL[type] || type}</span>}</span></div>
                  </div>
                  <div className="card-name-col">
                    <div className="card-name">{item.name || '—'}</div>
                    {meta.length > 0 && <div className="card-meta">{meta.join(' · ')}</div>}
                  </div>
                  <div className="card-price-col">
                    <div className={`card-price${!hasPrice ? ' empty' : ''}`}>{priceDisplay}</div>
                    <div className="card-currency">{item.currency || ''}</div>
                  </div>
                  <div className="card-vol-col"><div className="card-vol">{volDisplay}</div></div>
                </div>
              )
            })}
          </div>
          {pages > 1 && <div className="pagination">
            <div className={`pg${curPage === 0 ? ' disabled' : ''}`} onClick={() => curPage > 0 && goPage(0)}>«</div>
            <div className={`pg${curPage === 0 ? ' disabled' : ''}`} onClick={() => curPage > 0 && goPage(curPage - 1)} title="Предыдущая">‹</div>
            {ps > 0 && <><div className="pg">1</div><div className="pg dots">…</div></>}
            {Array.from({ length: pe - ps }, (_, i) => {
              const p = ps + i
              return <div key={p} className={`pg${p === curPage ? ' active' : ''}`} onClick={() => goPage(p)}>{p + 1}</div>
            })}
            {pe < pages && <><div className="pg dots">…</div><div className="pg">{pages}</div></>}
            <div className={`pg${curPage >= pages - 1 ? ' disabled' : ''}`} onClick={() => curPage < pages - 1 && goPage(curPage + 1)} title="Следующая">›</div>
            <div className={`pg${curPage >= pages - 1 ? ' disabled' : ''}`} onClick={() => curPage < pages - 1 && goPage(pages - 1)} title="Последняя">»</div>
          </div>}
        </main>
      </div>
      {modal && <div className="modal-overlay" onClick={e => { if (e.target === e.currentTarget) closeModal() }}>
        <div className="modal">
          <button className="modal-close" onClick={closeModal}>×</button>
          {modalLoading ? <div className="loading"><div className="spinner" /> Загрузка...</div>
            : modal.error ? <div className="modal-eyebrow">Ошибка загрузки</div>
              : <>
                <div className="modal-eyebrow">{TYPE_LABEL[modal.type] || modal.type}</div>
                <div className="modal-title">{modal.ticker}</div>
                <div className="modal-subtitle">{modal.name || ''}</div>
                <div className="modal-grid">
                  <div className="modal-cell"><div className="modal-cell-label">Цена</div><div className="modal-cell-val">{modal.price ? fmt(modal.price) + '' : '—'}</div></div>
                  <div className="modal-cell"><div className="modal-cell-label">Объём</div><div className="modal-cell-val">{fmtVol(modal.volume)}</div></div>
                  <div className="modal-cell"><div className="modal-cell-label">Валюта</div><div className="modal-cell-val">{modal.currency || '—'}</div></div>
                </div>
                <div className="modal-details">
                  {modal.issuer && <div className="modal-detail-item"><div className="modal-detail-label">Эмитент</div><div className="modal-detail-val">{modal.issuer}</div></div>}
                  {modal.sector && <div className="modal-detail-item"><div className="modal-detail-label">Сектор</div><div className="modal-detail-val">{modal.sector}</div></div>}
                  {modal.yield && <div className="modal-detail-item"><div className="modal-detail-label">Доходность</div><div className="modal-detail-val">{modal.yield}%</div></div>}
                  {modal.maturity_date && <div className="modal-detail-item"><div className="modal-detail-label">Погашение</div><div className="modal-detail-val">{modal.maturity_date}</div></div>}
                  {modal.market_cap && <div className="modal-detail-item"><div className="modal-detail-label">Капитализация</div><div className="modal-detail-val">{fmtVol(modal.market_cap)}</div></div>}
                  {modal.strike_price && <div className="modal-detail-item"><div className="modal-detail-label">Страйк</div><div className="modal-detail-val">{Number(modal.strike_price).toLocaleString('ru')}</div></div>}
                  {modal.option_type && <div className="modal-detail-item"><div className="modal-detail-label">Тип опциона</div><div className="modal-detail-val" style={{ color: modal.option_type === 'C' ? 'var(--green2)' : '#E879F9', fontWeight: 600 }}>{OPTION_TYPE_LABEL[modal.option_type] || modal.option_type}</div></div>}
                  {modal.volatility && <div className="modal-detail-item"><div className="modal-detail-label">Волатильность</div><div className="modal-detail-val">{modal.volatility}</div></div>}
                </div>
                {modal.updated_at && <div className="modal-updated">Последнее обновление: {new Date(modal.updated_at).toLocaleString('ru')}</div>}
              </>}
        </div>
      </div>}
      <div className={`toast${toastMsg ? ' show' : ''}`}>{toastMsg}</div>
      <ThemeToggle />
    </>
  )
}