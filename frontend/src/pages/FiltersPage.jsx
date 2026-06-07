import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './FiltersPage.css';

const API_BASE_URL = 'http://localhost:8000';

function tileTone(change) {
  if (change === undefined || change === null) return 'good-soft';
  if (change < -3) return 'bad-strong';
  if (change < 0) return 'bad';
  if (change > 3) return 'good';
  return 'good-soft';
}

export default function FiltersPage() {
  const [instruments, setInstruments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeInstrument, setActiveInstrument] = useState(null);

  // Параметры фильтрации под эндпоинты Swagger
  const [assetType, setAssetType] = useState('stock');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSector, setSelectedSector] = useState('');
  const [minPrice, setMinPrice] = useState(0);
  const [maxPrice, setMaxPrice] = useState(50000);

  // Облигационные поля
  const [minYield, setMinYield] = useState(0);
  const [maxYield, setMaxYield] = useState(30);
  const [maturityFrom, setMaturityFrom] = useState('');
  const [maturityTo, setMaturityTo] = useState('');

  // Сортировка и пагинация
  const [sortBy, setSortBy] = useState('ticker');
  const [sortOrder, setSortOrder] = useState('asc');
  const [page, setPage] = useState(1);
  const limit = 12;

  const fetchFilteredInstruments = async () => {
    setLoading(true);
    setError(null);
    try {
      let url = '';
      const params = new URLSearchParams();

      if (searchQuery.trim() !== '') {
        url = `${API_BASE_URL}/api/instruments/search`;
        params.append('q', searchQuery.trim());
        if (assetType) params.append('type', assetType);
        params.append('sort_by', sortBy);
        params.append('order', sortOrder);
      } else {
        url = `${API_BASE_URL}/api/instruments`;
        if (assetType) params.append('type', assetType);
        if (selectedSector) params.append('sector', selectedSector);

        params.append('min_price', String(minPrice));
        params.append('max_price', String(maxPrice));

        if (assetType === 'bond') {
          params.append('min_yield', String(minYield));
          params.append('max_yield', String(maxYield));
          if (maturityFrom) params.append('maturity_from', maturityFrom);
          if (maturityTo) params.append('maturity_to', maturityTo);
        }

        params.append('sort_by', sortBy);
        params.append('order', sortOrder);
        params.append('limit', String(limit));
        params.append('offset', String((page - 1) * limit));
      }

      const response = await fetch(`${url}?${params.toString()}`);
      if (!response.ok) {
        throw new Error('Ошибка при загрузке данных с бэкенда');
      }
      const data = await response.json();
      setInstruments(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      fetchFilteredInstruments();
    }, 250);
    return () => clearTimeout(delayDebounceFn);
  }, [assetType, searchQuery, selectedSector, sortBy, sortOrder, page, minPrice, maxPrice, minYield, maxYield, maturityFrom, maturityTo]);

  useEffect(() => {
    setPage(1);
    setSelectedSector('');
    setMinYield(0);
    setMaxYield(30);
    setMaturityFrom('');
    setMaturityTo('');
  }, [assetType]);

  const hasNextPage = instruments.length === limit;

  return (
    // Оберточный контейнер на весь экран с красивым фоном
    <div className="filters-page-wrapper">
      <div className="filters-page-container">
        {/* Шапка страницы */}
        <header className="filters-header">
          <h1>Интеллектуальный подбор MOEX</h1>
          <Link to="/" className="back-link">← На главную</Link>
        </header>

        {/* Переключатель вкладок классов активов */}
        <div className="asset-tabs">
          <button className={`asset-tab-btn ${assetType === 'stock' ? 'is-active' : ''}`} onClick={() => setAssetType('stock')}>Акции</button>
          <button className={`asset-tab-btn ${assetType === 'bond' ? 'is-active' : ''}`} onClick={() => setAssetType('bond')}>Облигации</button>
          <button className={`asset-tab-btn ${assetType === 'futures' ? 'is-active' : ''}`} onClick={() => setAssetType('futures')}>Фьючерсы</button>
          <button className={`asset-tab-btn ${assetType === 'option' ? 'is-active' : ''}`} onClick={() => setAssetType('option')}>Опционы</button>
        </div>

        <div className="filters-layout">
          {/* ПАНЕЛЬ СИДБАРА (ФИЛЬТРЫ) */}
          <aside className="filter-sidebar">
            <h3>Параметры</h3>

            {/* Поиск */}
            <div className="filter-group">
              <label>Поиск по тикеру/имени (q)</label>
              <input
                type="text"
                className="filter-input"
                placeholder="Например, SBER..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            {/* Сектор */}
            {assetType === 'stock' && (
              <div className="filter-group">
                <label>Сектор рынка</label>
                <select className="filter-select" value={selectedSector} onChange={(e) => setSelectedSector(e.target.value)}>
                  <option value="">Все секторы</option>
                  <option value="Финансы">Финансы</option>
                  <option value="Энергетика">Энергетика</option>
                  <option value="IT">IT</option>
                  <option value="Металлы">Металлы</option>
                  <option value="Потребсектор">Потребсектор</option>
                  <option value="Транспорт">Транспорт</option>
                  <option value="Недвижимость">Недвижимость</option>
                </select>
              </div>
            )}

            {/* Макс. Цена */}
            <div className="filter-group">
              <label>Макс. цена (max_price)</label>
              <input
                type="range"
                className="filter-range"
                min="0"
                max="100000"
                step="50"
                value={maxPrice}
                onChange={(e) => setMaxPrice(Number(e.target.value))}
              />
              <div className="range-values">
                <span>{minPrice} ₽</span>
                <span>{maxPrice.toLocaleString('ru-RU')} ₽</span>
              </div>
            </div>

            {/* Облигационные фильтры */}
            {assetType === 'bond' && (
              <>
                <div className="filter-group">
                  <label>Макс. доходность (max_yield)</label>
                  <input
                    type="range"
                    className="filter-range"
                    min="0"
                    max="40"
                    value={maxYield}
                    onChange={(e) => setMaxYield(Number(e.target.value))}
                  />
                  <div className="range-values">
                    <span>{minYield}%</span>
                    <span>{maxYield}%</span>
                  </div>
                </div>

                <div className="filter-group">
                  <label>Погашение от</label>
                  <input type="date" className="filter-input" value={maturityFrom} onChange={(e) => setMaturityFrom(e.target.value)} />
                </div>

                <div className="filter-group">
                  <label>Погашение до</label>
                  <input type="date" className="filter-input" value={maturityTo} onChange={(e) => setMaturityTo(e.target.value)} />
                </div>
              </>
            )}

            {/* Сортировка */}
            <div className="filter-group">
              <label>Сортировка (sort_by)</label>
              <select className="filter-select" value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                <option value="ticker">Тикеру (ticker)</option>
                <option value="name">Названию (name)</option>
                <option value="price">Цене (price)</option>
                <option value="volume">Объему (volume)</option>
                {assetType === 'bond' && <option value="yield">Доходности (yield)</option>}
                {assetType === 'stock' && <option value="market_cap">Капитализации (market_cap)</option>}
              </select>
              <select className="filter-select" style={{ marginTop: '8px' }} value={sortOrder} onChange={(e) => setSortOrder(e.target.value)}>
                <option value="asc">По возрастанию (asc)</option>
                <option value="desc">По убыванию (desc)</option>
              </select>
            </div>
          </aside>

          {/* СЕТКА С КАРТОЧКАМИ */}
          <div className="results-container">
            {error && <div style={{ color: 'red', textAlign: 'center', padding: '20px' }}>Ошибка: {error}</div>}

            {!loading && !error && instruments.length === 0 && (
              <div style={{ textAlign: 'center', padding: '40px', color: '#475569' }}>Инструменты не найдены.</div>
            )}

            {instruments.length > 0 && (
              <>
                {/* Теперь сетка просто плавно затухает на opacity: 0.6 во время loading без прыгающих надписей */}
                <div className={`results-grid ${loading ? 'loading-blur' : ''}`}>
                  {instruments.map((item, idx) => (
                    <button key={idx} className={`instrument-tile ${tileTone(item.change)}`} onClick={() => setActiveInstrument(item)}>
                      <b>{item.ticker}</b>
                      <span>{item.price ? `${item.price} ${item.currency || '₽'}` : '0 ₽'}</span>
                      {item.change !== undefined && item.change !== null && (
                        <small>{item.change > 0 ? '+' : ''}{item.change.toFixed(2)}%</small>
                      )}
                    </button>
                  ))}
                </div>

                {/* Пагинация */}
                <div className="pagination">
                  <button className="page-btn" disabled={page === 1} onClick={() => setPage(prev => Math.max(prev - 1, 1))}>‹</button>
                  <span>Страница {page}</span>
                  <button className="page-btn" disabled={!hasNextPage} onClick={() => setPage(prev => prev + 1)}>›</button>
                </div>
              </>
            )}
          </div>
        </div>

        {/* ОВЕРЛЕЙ МОДАЛКИ */}
        <div className={`modal-overlay ${activeInstrument ? 'is-open' : ''}`} onClick={(e) => e.target.id === 'modal-bg' && setActiveInstrument(null)} id="modal-bg">
          <div className="modal-content">
            <button className="modal-close-btn" onClick={() => setActiveInstrument(null)}>×</button>
            <p style={{ color: '#2563eb', fontSize: '12px', fontWeight: 'bold', margin: '0 0 8px 0', textTransform: 'uppercase' }}>
              {activeInstrument && (activeInstrument.change >= 0 ? 'Рост за сессию' : 'Падение за сессию')}
            </p>
            <h2 style={{ margin: '0 0 4px 0', fontSize: '28px' }}>{activeInstrument?.ticker}</h2>
            <p style={{ margin: '0 0 20px 0', color: '#475569' }}>{activeInstrument?.name}</p>

            <div className="modal-stats-grid">
              <div className="stat-item"><small>Текущая цена</small><b>{activeInstrument?.price} {activeInstrument?.currency || '₽'}</b></div>
              <div className="stat-item">
                <small>Изменение</small>
                <b style={{ color: activeInstrument?.change >= 0 ? '#166534' : '#991b1b' }}>
                  {activeInstrument && (activeInstrument.change > 0 ? '+' : '')}{activeInstrument?.change?.toFixed(2)}%
                </b>
              </div>
              <div className="stat-item"><small>Тип инструмента</small><b>{activeInstrument?.type}</b></div>
              <div className="stat-item"><small>Сектор рынка</small><b>{activeInstrument?.sector || '—'}</b></div>

              {activeInstrument?.type === 'bond' && (
                <>
                  <div className="stat-item"><small>Доходность (yield)</small><b>{activeInstrument?.yield}%</b></div>
                  <div className="stat-item"><small>Дата погашения</small><b>{activeInstrument?.maturity_date || '—'}</b></div>
                  <div className="stat-item"><small>Эмитент</small><b>{activeInstrument?.issuer || '—'}</b></div>
                </>
              )}

              {activeInstrument?.type === 'stock' && (
                <div className="stat-item"><small>Капитализация</small><b>{activeInstrument?.market_cap ? `${activeInstrument.market_cap.toLocaleString('ru-RU')} ₽` : '—'}</b></div>
              )}

              {activeInstrument?.type === 'option' && (
                <>
                  <div className="stat-item"><small>Тип опциона</small><b>{activeInstrument?.option_type}</b></div>
                  <div className="stat-item"><small>Страйк</small><b>{activeInstrument?.strike_price} ₽</b></div>
                  <div className="stat-item"><small>Волатильность</small><b>{activeInstrument?.volatility}%</b></div>
                </>
              )}
              <div className="stat-item"><small>Объем торгов</small><b>{activeInstrument?.volume ? `${activeInstrument.volume.toLocaleString('ru-RU')} ₽` : '—'}</b></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}