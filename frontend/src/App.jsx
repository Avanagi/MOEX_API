import { useState, useEffect, useRef } from 'react';

// URL вашего FastAPI бэкенда (если фронтенд запущен на другом порту, настройте CORS)
const API_BASE_URL = 'http://localhost:8000';

export default function App() {
  // --- Системные состояния ---
  const [cookieAccepted, setCookieAccepted] = useState(false);
  const [activeInstrument, setActiveInstrument] = useState(null);

  // --- Состояния API данных ---
  const [instruments, setInstruments] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // --- Состояния фильтрации (пользовательский ввод) ---
  const [assetType, setAssetType] = useState('shares'); // 'shares' | 'bonds' | 'futures' | 'options'
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSector, setSelectedSector] = useState('');
  const [sortBy, setSortBy] = useState('volume'); // Сортировка по умолчанию
  const [sortOrder, setSortOrder] = useState('desc'); // Направление сортировки
  const [page, setPage] = useState(1);
  const limit = 9; // Сколько карточек выводить на страницу

  // Диапазонные фильтры (слайдеры)
  const [minPrice, setMinPrice] = useState(0);
  const [maxPrice, setMaxPrice] = useState(10000);
  const [minYield, setMinYield] = useState(0); // только для облигаций (YTM)
  const [maxYield, setMaxYield] = useState(25);

  // --- Функция запроса к API фильтрации ---
  const fetchFilteredInstruments = async () => {
    setLoading(true);
    setError(null);
    try {
      // Строим базовый URL
      // Если введен поисковый запрос, используем эндпоинт поиска, иначе — общий список
      const endpoint = searchQuery
        ? `${API_BASE_URL}/api/instruments/search`
        : `${API_BASE_URL}/api/instruments`;

      const params = new URLSearchParams({
        type: assetType,
        page: String(page),
        limit: String(limit),
        sort_by: sortBy,
        order: sortOrder,
        min_price: String(minPrice),
        max_price: String(maxPrice),
      });

      // Добавляем текстовый поиск, если он есть
      if (searchQuery) {
        params.append('q', searchQuery);
      }

      // Добавляем специфичные фильтры для акций
      if (assetType === 'shares' && selectedSector) {
        params.append('sector', selectedSector);
      }

      // Добавляем специфичные фильтры для облигаций
      if (assetType === 'bonds') {
        params.append('min_yield', String(minYield));
        params.append('max_yield', String(maxYield));
      }

      const response = await fetch(`${endpoint}?${params.toString()}`);
      if (!response.ok) {
        throw new Error('Ошибка при загрузке данных с сервера');
      }

      const result = await response.json();

      // Предполагается, что бэкенд возвращает объект { data: [...], total: 120 }
      // Если бэкенд возвращает просто массив, адаптируйте под вашу структуру
      if (Array.isArray(result)) {
        setInstruments(result);
        setTotalCount(result.length);
      } else {
        setInstruments(result.data || []);
        setTotalCount(result.total || 0);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // --- Запрос данных при любом изменении фильтров (Debounce для ввода и слайдеров) ---
  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      fetchFilteredInstruments();
    }, 300); // 300 мс задержки для предотвращения спама запросами при вводе

    return () => clearTimeout(delayDebounceFn);
  }, [assetType, searchQuery, selectedSector, sortBy, sortOrder, page, minPrice, maxPrice, minYield, maxYield]);

  // Сброс страницы при смене типа актива
  useEffect(() => {
    setPage(1);
    setSelectedSector('');
  }, [assetType]);

  // --- Вспомогательные данные для рендеринга ---
  const totalPages = Math.ceil(totalCount / limit);

  return (
    <div className="moex-app">
      {/* Шапка и верхний тикер (можно оставить статичными или подключить к API) */}
      <header className="site-header">
        <div className="page">
          <div className="main-nav">
            <a className="logo" href="#">
              <span>MOEX</span>
              <small>Московская<br />Биржа</small>
            </a>
            <nav className="nav-links">
              <a href="#ipo">IPO</a>
              <a className="is-current" href="#market-filter">Подбор инструментов</a>
              <a href="#news">Новости</a>
            </nav>
          </div>
        </div>
      </header>

      <main>
        {/* ================= СЕКЦИЯ УМНОГО ПОДБОРА (ФИЛЬТРЫ) ================= */}
        <section className="page section" id="market-filter" style={{ marginTop: '40px' }}>
          <h2 className="section-title">Интеллектуальный подбор инструментов</h2>

          {/* 1. Верхний переключатель классов активов */}
          <div className="trend-tabs" style={{ marginBottom: '25px' }}>
            <button className={assetType === 'shares' ? 'is-active' : ''} onClick={() => setAssetType('shares')}>Акции</button>
            <button className={assetType === 'bonds' ? 'is-active' : ''} onClick={() => setAssetType('bonds')}>Облигации</button>
            <button className={assetType === 'futures' ? 'is-active' : ''} onClick={() => setAssetType('futures')}>Фьючерсы</button>
            <button className={assetType === 'options' ? 'is-active' : ''} onClick={() => setAssetType('options')}>Опционы</button>
          </div>

          <div className="trends-grid" style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '30px' }}>

            {/* ЛЕВАЯ ПАНЕЛЬ: ФИЛЬТРЫ (Слайдеры, Дропдауны, Поиск) */}
            <aside className="filter-panel" style={{ background: '#f5f7fa', padding: '20px', borderRadius: '12px' }}>
              <h3 style={{ marginBottom: '20px', fontSize: '18px' }}>Фильтрация</h3>

              {/* Поиск по тексту */}
              <div className="filter-group" style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>Поиск</label>
                <input
                  type="text"
                  className="select"
                  style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
                  placeholder="Тикер или название..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>

              {/* Сортировка */}
              <div className="filter-group" style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>Сортировать по</label>
                <select className="select" style={{ width: '100%' }} value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                  <option value="volume">Объему торгов</option>
                  <option value="price">Цене</option>
                  <option value="change">Изменению (%)</option>
                  {assetType === 'bonds' && <option value="yield">Доходности</option>}
                </select>
                <select className="select" style={{ width: '100%', marginTop: '8px' }} value={sortOrder} onChange={(e) => setSortOrder(e.target.value)}>
                  <option value="desc">По убыванию</option>
                  <option value="asc">По возрастанию</option>
                </select>
              </div>

              {/* Слайдер цены (для всех типов активов) */}
              <div className="filter-group" style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>Цена (до, ₽)</label>
                <input
                  type="range"
                  min="0"
                  max="10000"
                  step="10"
                  style={{ width: '100%' }}
                  value={maxPrice}
                  onChange={(e) => setMaxPrice(Number(e.target.value))}
                />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginTop: '4px' }}>
                  <span>0 ₽</span>
                  <span>{maxPrice.toLocaleString('ru-RU')} ₽</span>
                </div>
              </div>

              {/* Фильтр по сектору (только для Акций) */}
              {assetType === 'shares' && (
                <div className="filter-group" style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>Сектор</label>
                  <select className="select" style={{ width: '100%' }} value={selectedSector} onChange={(e) => setSelectedSector(e.target.value)}>
                    <option value="">Все секторы</option>
                    <option value="Финансы">Финансы</option>
                    <option value="Энергетика">Энергетика</option>
                    <option value="IT">IT / Технологии</option>
                    <option value="Металлы">Металлургия</option>
                    <option value="Потребсектор">Потребительский сектор</option>
                  </select>
                </div>
              )}

              {/* Слайдер доходности (только для Облигаций) */}
              {assetType === 'bonds' && (
                <div className="filter-group" style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>Доходность YTM (%): {maxYield}%</label>
                  <input
                    type="range"
                    min="0"
                    max="30"
                    style={{ width: '100%' }}
                    value={maxYield}
                    onChange={(e) => setMaxYield(Number(e.target.value))}
                  />
                </div>
              )}
            </aside>

            {/* ПРАВАЯ ЧАСТЬ: СЕТКА РЕЗУЛЬТАТОВ (Живые карточки из API) */}
            <div className="results-panel">
              {loading && <div style={{ textAlign: 'center', padding: '40px' }}>Загрузка инструментов...</div>}
              {error && <div style={{ color: 'red', padding: '20px' }}>Ошибка: {error}</div>}

              {!loading && !error && instruments.length === 0 && (
                <div style={{ textAlign: 'center', padding: '40px', color: '#667085' }}>
                  Инструменты с выбранными параметрами не найдены.
                </div>
              )}

              {!loading && !error && instruments.length > 0 && (
                <>
                  <div className="heatmap" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '15px' }}>
                    {instruments.map((item, idx) => (
                      <button
                        key={idx}
                        className={`tile ${tileTone(item.change)}`}
                        onClick={() => setActiveInstrument(item)}
                        style={{ width: '100%', minHeight: '100px', cursor: 'pointer' }}
                      >
                        <b>{item.ticker}</b>
                        <span>{item.price} ₽</span>
                        <small>{item.change > 0 ? '+' : ''}{item.change.toFixed(2)}%</small>
                      </button>
                    ))}
                  </div>

                  {/* Пагинация */}
                  {totalPages > 1 && (
                    <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', marginTop: '30px' }}>
                      <button
                        className="square-button"
                        disabled={page === 1}
                        onClick={() => setPage(prev => Math.max(prev - 1, 1))}
                      >
                        ‹
                      </button>
                      <span style={{ alignSelf: 'center', fontSize: '14px' }}>
                        Страница {page} из {totalPages}
                      </span>
                      <button
                        className="square-button"
                        disabled={page === totalPages}
                        onClick={() => setPage(prev => Math.min(prev + 1, totalPages))}
                      >
                        ›
                      </button>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </section>

        {/* Секции новостей, IPO и метрик можно оставить без изменений */}
      </main>

      {/* Окно детальной информации по клику (Модалка) */}
      <div className={`modal ${activeInstrument ? 'is-open' : ''}`} id="instrumentModal" aria-hidden={!activeInstrument}>
        <div className="modal-window" role="dialog" aria-modal="true">
          <button className="modal-close" onClick={() => setActiveInstrument(null)}>×</button>
          <p className="eyebrow">{activeInstrument && (activeInstrument.change >= 0 ? 'Растущий инструмент' : 'Снижение за день')}</p>
          <h2>{activeInstrument?.ticker}</h2>
          <p>{activeInstrument?.name}</p>
          <div className="modal-stats">
            <span><small>Цена</small><b>{activeInstrument?.price} ₽</b></span>
            <span>
              <small>Изменение</small>
              <b style={{ color: activeInstrument?.change >= 0 ? '#178b31' : '#ee3124' }}>
                {activeInstrument && (activeInstrument.change > 0 ? '+' : '')}{activeInstrument?.change.toFixed(2)}%
              </b>
            </span>
            <span><small>Сектор</small><b>{activeInstrument?.sector || 'Не указан'}</b></span>
            <span><small>Объем торгов</small><b>{activeInstrument?.volume || 'Н/Д'}</b></span>
          </div>
        </div>
      </div>
    </div>
  );
}