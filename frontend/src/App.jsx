import { useState, useEffect, useRef } from 'react';
import './style.css';

const tickerData = [
  ['¥', '10,435', 'down'],
  ['₺', '1,56', 'down'],
  ['T', '15,65', 'up'],
  ['Br', '25,805', 'down'],
  ['SARE', '0,751', 'down'],
  ['ZVEZ', '6,12', 'down'],
  ['LVHK', '23,20', 'down'],
  ['SOFL', '61,60', 'down'],
  ['RU000A106N57', '1025,00', 'down']
];

const shares = [
  { ticker: 'GAZP', name: 'Газпром', price: '119.33', change: 0.27, sector: 'Энергетика', volume: '8,8 млрд ₽', size: 'size-lg' },
  { ticker: 'SBER', name: 'Сбербанк', price: '323.77', change: 0.16, sector: 'Финансы', volume: '14,5 млрд ₽', size: 'size-lg' },
  { ticker: 'VTBR', name: 'ВТБ', price: '89.98', change: 0.25, sector: 'Финансы', volume: '4,2 млрд ₽', size: 'size-lg' },
  { ticker: 'LKOH', name: 'Лукойл', price: '5 236.00', change: 2.29, sector: 'Энергетика', volume: '7,2 млрд ₽', size: 'size-md' },
  { ticker: 'T', name: 'Т-Технологии', price: '312.84', change: 0.12, sector: 'IT', volume: '3,1 млрд ₽', size: 'size-md' },
  { ticker: 'ROSN', name: 'Роснефть', price: '404.55', change: 0.17, sector: 'Энергетика', volume: '2,6 млрд ₽', size: 'size-md' },
  { ticker: 'X5', name: 'X5 Group', price: '2 493.50', change: 1.73, sector: 'Потребсектор', volume: '940 млн ₽', size: 'size-md' },
  { ticker: 'NVTK', name: 'Новатэк', price: '1126.60', change: 0.41, sector: 'Энергетика', volume: '1,8 млрд ₽', size: '' },
  { ticker: 'TATN', name: 'Татнефть', price: '636.70', change: 3.33, sector: 'Энергетика', volume: '1,4 млрд ₽', size: '' },
  { ticker: 'RUAL', name: 'Русал', price: '35.51', change: -0.74, sector: 'Металлы', volume: '760 млн ₽', size: '' },
  { ticker: 'GMKN', name: 'Норникель', price: '129.46', change: 1.89, sector: 'Металлы', volume: '1,1 млрд ₽', size: '' },
  { ticker: 'VKCO', name: 'VK', price: '246.10', change: 4.13, sector: 'IT', volume: '890 млн ₽', size: '' },
  { ticker: 'PLZL', name: 'Полюс', price: '2 100.00', change: 1.40, sector: 'Металлы', volume: '1,6 млрд ₽', size: '' },
  { ticker: 'AFLT', name: 'Аэрофлот', price: '47.99', change: 2.70, sector: 'Транспорт', volume: '670 млн ₽', size: '' },
  { ticker: 'OZON', name: 'Ozon', price: '4 205.50', change: 1.74, sector: 'IT', volume: '2,2 млрд ₽', size: '' },
  { ticker: 'YDEX', name: 'Яндекс', price: '4 080.00', change: 1.12, sector: 'IT', volume: '5,9 млрд ₽', size: '' },
  { ticker: 'MOEX', name: 'Московская Биржа', price: '175.66', change: 1.43, sector: 'Финансы', volume: '820 млн ₽', size: '' },
  { ticker: 'SMLT', name: 'Самолет', price: '504.20', change: 2.31, sector: 'Недвижимость', volume: '430 млн ₽', size: '' }
];

const futures = [
  { ticker: 'CRM6', name: 'CNY/RUB', price: '10.53', change: -0.37, sector: 'Валютный рынок', volume: '1,9 млрд ₽', size: 'size-lg' },
  { ticker: 'BRM6', name: 'Brent', price: '107.09', change: 1.33, sector: 'Товарный рынок', volume: '9,6 млрд ₽', size: 'size-lg' },
  { ticker: 'SiM6', name: 'USD/RUB', price: '71 677.00', change: -0.28, sector: 'Валютный рынок', volume: '18,8 млрд ₽', size: 'size-lg' },
  { ticker: 'CNYRUBF', name: 'CNY/RUB Futures', price: '10.43', change: -0.32, sector: 'Валютный рынок', volume: '820 млн ₽', size: 'size-md' },
  { ticker: 'MXM6', name: 'Индекс МосБиржи', price: '268 800.00', change: 1.20, sector: 'Индексы', volume: '5,4 млрд ₽', size: 'size-md' },
  { ticker: 'GDM6', name: 'Золото', price: '4 512.40', change: -0.68, sector: 'Металлы', volume: '2,1 млрд ₽', size: 'size-md' },
  { ticker: 'SVM6', name: 'Серебро', price: '76.88', change: -0.21, sector: 'Металлы', volume: '740 млн ₽', size: 'size-md' },
  { ticker: 'USDRUBF', name: 'USD/RUB Futures', price: '71.19', change: -0.24, sector: 'Валютный рынок', volume: '4,3 млрд ₽', size: '' },
  { ticker: 'IMOEXF', name: 'Индексный фьючерс', price: '2 660.50', change: 1.08, sector: 'Индексы', volume: '3,7 млрд ₽', size: '' },
  { ticker: 'NGK6', name: 'Газ', price: '3.04', change: 0.03, sector: 'Товарный рынок', volume: '590 млн ₽', size: '' },
  { ticker: 'SiU6', name: 'USD/RUB', price: '72 716.00', change: -0.37, sector: 'Валютный рынок', volume: '1,2 млрд ₽', size: '' },
  { ticker: 'RIM6', name: 'RTS Index', price: '118 190.00', change: 1.49, sector: 'Индексы', volume: '2,9 млрд ₽', size: '' },
  { ticker: 'EuM6', name: 'EUR/RUB', price: '82 985.00', change: -0.54, sector: 'Валютный рынок', volume: '620 млн ₽', size: '' },
  { ticker: 'CCM6', name: 'Какао', price: '274.60', change: -3.62, sector: 'Товарный рынок', volume: '180 млн ₽', size: '' },
  { ticker: 'BRN6', name: 'Brent', price: '103.38', change: 1.57, sector: 'Товарный рынок', volume: '8,7 млрд ₽', size: '' },
  { ticker: 'BMM6', name: 'Металлы', price: '107.06', change: 1.33, sector: 'Металлы', volume: '530 млн ₽', size: '' },
  { ticker: 'MMM6', name: 'Индекс', price: '2 688.40', change: 1.24, sector: 'Индексы', volume: '950 млн ₽', size: '' },
  { ticker: 'NAM6', name: 'NASDAQ', price: '28 963.00', change: -0.31, sector: 'Индексы', volume: '410 млн ₽', size: '' }
];

const productGroups = {
  popular: [
    ['Акции', 'Ценные бумаги, удостоверяющие право на долю собственности в компании и получение дивидендов', '▥'],
    ['Облигации', 'Долговые ценные бумаги с регулярными выплатами дохода и известным сроком погашения', '%'],
    ['Фьючерсы на цифровые активы', 'Контракты на инструменты, цена которых связана с цифровыми активами', '₿'],
    ['Фьючерсы на драгметаллы', 'Контракты на золото и другие драгоценные металлы с расчетами по биржевой цене', '✦'],
    ['Фонды денежного рынка', 'Инструменты для размещения средств на любой срок с низкой волатильностью', '₽'],
    ['Золото', 'Инвестируйте в свой золотой резерв на Московской бирже', '▰'],
    ['Репо для бизнеса', 'Размещайте и привлекайте средства под обеспечение ценными бумагами', '↔'],
    ['IPO на MOEX', 'Привлечение капитала для вашего бизнеса за счет продажи акций инвесторам', '▤']
  ],
  investors: [
    ['Индексы', 'Следите за динамикой рынков и используйте индексы как ориентир', '⌁'],
    ['Валютный рынок', 'Инструменты для операций с рублем и иностранными валютами', '¥'],
    ['Драгоценные металлы', 'Золото и серебро в биржевом формате', 'Au'],
    ['Фонды', 'Готовые портфели ценных бумаг с простой покупкой через брокера', '▦']
  ],
  issuers: [
    ['Листинг ценных бумаг', 'Выводите акции и облигации на организованный рынок', '✓'],
    ['IR-сервисы', 'Коммуникации с инвесторами и раскрытие информации', 'i'],
    ['Размещение облигаций', 'Привлекайте долговое финансирование через инфраструктуру MOEX', '%'],
    ['IPO', 'Публичное размещение акций на Московской бирже', '↗']
  ],
  pros: [
    ['Подключение к торгам', 'Сервисы и технологический доступ для участников рынка', '⌘'],
    ['Маркет-дата', 'Потоки данных, индикаторы и исторические значения', '∿'],
    ['Клиринг', 'Расчеты, обеспечение и контроль рисков', '□'],
    ['API', 'Интеграции для торговых календарей и рыночной информации', '{}']
  ]
};

const trends = {
  shares: [
    ['IMOEX', '2 664,29', '+0,91%', '19:00'],
    ['IMOEX2', '2 659,69', '+0,73%', '20:05'],
    ['RTSI', '1 185,63', '+1,14%', '19:00'],
    ['MOEXBMI', '1 907,04', '+0,88%', '19:00']
  ],
  bonds: [
    ['RGBI', '105,37', '+0,22%', '19:00'],
    ['RUCBITR', '782,18', '+0,17%', '18:45'],
    ['MOEXOG', '246,70', '+0,09%', '19:00'],
    ['RUGBITR', '636,12', '+0,14%', '19:00']
  ],
  pension: [
    ['RUPAI', '1 420,30', '+0,41%', '19:00'],
    ['RUPCI', '983,11', '+0,18%', '19:00'],
    ['RUPMI', '734,40', '+0,26%', '18:50'],
    ['RUPFI', '611,65', '+0,20%', '19:00']
  ]
};

const monthNames = [
  'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
  'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
];
const weekdayNames = ['вс', 'пн', 'вт', 'ср', 'чт', 'пт', 'сб'];

const calendarEvents = [
  ['Фондовый рынок', ['Погашаются облигации', 'ВТБС1-589', 'ВТБС1-590', 'СЕЛЛСерв02', 'СберСИБ835']],
  ['Валютный рынок', ['Дата исполнения по', 'USDRUB_SPT 26.05.2026', 'USDRUB_STS 26.05.2026']],
  ['Срочный рынок', ['В этот день экспирируются', 'Индексы RVI', 'Товары GOLD, SILV', 'Валюта CNY, Si']]
];

const news = [
  ['21 мая 2026', 'Первые внебиржевые сделки с золотом заключены на рынке драгметаллов Московской биржи'],
  ['21 мая 2026', 'Московская биржа объявляет финансовые результаты за первый квартал 2026 года'],
  ['19 мая 2026', 'Московская биржа проводит хакатон по созданию ИИ-агента'],
  ['18 мая 2026', 'Московская биржа допустит акции "B2B РТС" к торгам утром, вечером и в выходные'],
  ['18 мая 2026', 'Расписание торгов на Московской бирже в июне 2026 года'],
  ['18 мая 2026', 'Московская биржа получила специальный приз премии Data Award 2026'],
  ['15 мая 2026', 'Московская биржа проведет годовое собрание акционеров 22 июня'],
  ['15 мая 2026', 'Московская биржа увеличивает число ПИФ на дополнительных сессиях']
];

const ipoItems = [
  ['ПАО "B2B-РТС"', 'Технологии и телеком', '17.04.2026', '118', 'B2B'],
  ['ПАО «ГК «БАЗИС»', 'Технологии и телеком', '10.12.2025', '109', 'BASIS'],
  ['ПАО «ДОМ.РФ»', 'Финансовые услуги', '20.11.2025', '1750', 'ДОМ']
];
// === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ РИСОВАНИЯ ===
function tileTone(change) {
  if (change < -3) return 'bad strong';
  if (change < 0) return 'bad';
  if (change > 3) return 'good';
  return 'good soft';
}

function makeChartValues(kind, activeIndex) {
  return Array.from({ length: 54 }, (_, i) => {
    const start = kind === 'bonds' ? 2630 : kind === 'pension' ? 2622 : 2635;
    const wave = Math.sin(i / 4 + activeIndex) * 9;
    const softWave = Math.cos(i / 7) * 4;
    const slope = i * (kind === 'shares' ? 0.7 : 0.45);
    const dip = i > 12 && i < 18 ? 20 : 0;
    return start + wave + softWave + slope - dip;
  });
}

function drawRoundRect(ctx, x, y, width, height, radius) {
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.lineTo(x + width - radius, y);
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
  ctx.lineTo(x + width, y + height - radius);
  ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
  ctx.lineTo(x + radius, y + height);
  ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
  ctx.lineTo(x, y + radius);
  ctx.quadraticCurveTo(x, y, x + radius, y);
  ctx.closePath();
}

export default function App() {
  const [cookieAccepted, setCookieAccepted] = useState(false);
  const [productTab, setProductTab] = useState('popular');
  const [trendKind, setTrendKind] = useState('shares');
  const [trendActiveIndex, setTrendActiveIndex] = useState(0);
  const [trendHoverIndex, setTrendHoverIndex] = useState(null);

  const [calendarState, setCalendarState] = useState({
    month: 4, // Май
    year: 2026,
    selectedDay: 21
  });

  const [activeInstrument, setActiveInstrument] = useState(null);

  const canvasRef = useRef(null);
  const [chartPoints, setChartPoints] = useState([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    const values = makeChartValues(trendKind, trendActiveIndex);

    const minValue = 2610;
    const maxValue = 2674;
    const leftPad = 12;
    const rightPad = 78;
    const topPad = 28;
    const bottomPad = 42;
    const chartWidth = width - leftPad - rightPad;
    const chartHeight = height - topPad - bottomPad;

    const calculatedPoints = values.map((value, index) => {
      const x = leftPad + (index / (values.length - 1)) * chartWidth;
      const y = topPad + (1 - (value - minValue) / (maxValue - minValue)) * chartHeight;
      return { x, y, value };
    });

    setChartPoints(calculatedPoints);

    ctx.clearRect(0, 0, width, height);
    ctx.strokeStyle = '#d8dde4';
    ctx.lineWidth = 1;

    const labels = [2670, 2655, 2640, 2625, 2610];
    labels.forEach(label => {
      const y = topPad + (1 - (label - minValue) / (maxValue - minValue)) * chartHeight;
      ctx.beginPath();
      ctx.moveTo(leftPad, y);
      ctx.lineTo(width - rightPad, y);
      ctx.stroke();
    });

    ctx.strokeStyle = '#4168ff';
    ctx.lineWidth = 3;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    ctx.beginPath();
    calculatedPoints.forEach((point, index) => {
      index === 0 ? ctx.moveTo(point.x, point.y) : ctx.lineTo(point.x, point.y);
    });
    ctx.stroke();

    ctx.fillStyle = '#26313d';
    ctx.font = '18px Arial';
    labels.forEach(label => {
      const y = topPad + (1 - (label - minValue) / (maxValue - minValue)) * chartHeight;
      ctx.fillText(new Intl.NumberFormat('ru-RU').format(label), width - 58, y + 6);
    });

    ctx.font = '15px Arial';
    for (let i = 0; i < 8; i += 1) {
      ctx.fillText(i === 0 ? '20 мая' : '21 мая', leftPad + i * 76, height - 6);
    }

    if (trendHoverIndex !== null && calculatedPoints[trendHoverIndex]) {
      const point = calculatedPoints[trendHoverIndex];
      const activeTicker = trends[trendKind][trendActiveIndex][0];
      const date = new Date(2026, 4, 21, 18, Math.min(59, 6 + trendHoverIndex), 59);
      const valueStr = point.value.toLocaleString('ru-RU', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
      const tooltipWidth = 245;
      const tooltipHeight = 76;
      const tooltipX = Math.min(Math.max(point.x - tooltipWidth / 2, 12), width - tooltipWidth - 12);
      const tooltipY = point.y > 130 ? point.y - 96 : point.y + 22;

      ctx.save();
      ctx.strokeStyle = '#c8cdd4';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(point.x, 28);
      ctx.lineTo(point.x, height - 42);
      ctx.stroke();

      ctx.fillStyle = '#4168ff';
      ctx.beginPath();
      ctx.arc(point.x, point.y, 5, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#fff';
      ctx.beginPath();
      ctx.arc(point.x, point.y, 2, 0, Math.PI * 2);
      ctx.fill();

      ctx.shadowColor = 'rgba(20, 30, 44, 0.16)';
      ctx.shadowBlur = 18;
      ctx.shadowOffsetY = 8;
      ctx.fillStyle = '#fff';
      drawRoundRect(ctx, tooltipX, tooltipY, tooltipWidth, tooltipHeight, 10);
      ctx.fill();
      ctx.shadowColor = 'transparent';
      ctx.strokeStyle = '#c8cdd4';
      ctx.stroke();

      ctx.fillStyle = '#4d5766';
      ctx.font = '16px Arial';
      ctx.fillText(activeTicker, tooltipX + 16, tooltipY + 28);
      ctx.fillText('Дата', tooltipX + 16, tooltipY + 56);

      ctx.fillStyle = '#000';
      ctx.textAlign = 'right';
      ctx.fillText(valueStr, tooltipX + tooltipWidth - 16, tooltipY + 28);
      ctx.fillText(date.toLocaleString('ru-RU'), tooltipX + tooltipWidth - 16, tooltipY + 56);
      ctx.restore();
    }
  }, [trendKind, trendActiveIndex, trendHoverIndex]);

  const getDaysInMonth = (year, month) => {
    return new Date(year, month + 1, 0).getDate();
  };

  const daysCount = getDaysInMonth(calendarState.year, calendarState.month);

  const handleMonthChange = (e) => {
    setCalendarState(prev => ({ ...prev, month: Number(e.target.value) }));
  };

  const handleYearChange = (e) => {
    setCalendarState(prev => ({ ...prev, year: Number(e.target.value) }));
  };

  const stepMonth = (direction) => {
    setCalendarState(prev => {
      let nextMonth = prev.month + direction;
      let nextYear = prev.year;
      if (nextMonth < 0) {
        nextMonth = 11;
        nextYear -= 1;
      } else if (nextMonth > 11) {
        nextMonth = 0;
        nextYear += 1;
      }
      return { ...prev, month: nextMonth, year: nextYear };
    });
  };

  const handleMouseMove = (e) => {
    const canvas = canvasRef.current;
    if (!canvas || chartPoints.length === 0) return;
    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left) * (canvas.width / rect.width);

    const nearest = chartPoints.reduce((best, point, index) => {
      const distance = Math.abs(point.x - x);
      return distance < best.distance ? { index, distance } : best;
    }, { index: 0, distance: Infinity });

    setTrendHoverIndex(nearest.index);
  };

  return (
    <div className="moex-app">
      {/* Бегущая строка котировок */}
      <div className="ticker-strip">
        <div className="page ticker-line" id="tickerLine">
          {tickerData.map(([name, value, direction], idx) => (
            <span key={idx} className="ticker-item">
              <b>{name}</b>
              <span>{value}</span>
              <span className={direction}>{direction === 'up' ? '↑' : '↓'}</span>
              {/* eslint-disable-next-line react-hooks/purity */}
              <small className="badge-change">-2,{Math.floor(Math.random() * 9)}%</small>
            </span>
          ))}
        </div>
      </div>

      {/* Хедер */}
      <header className="site-header">
        <div className="page">
          <div className="main-nav">
            <a className="logo" href="#" aria-label="MOEX">
              <span>MOEX</span>
              <small>Московская<br />Биржа</small>
            </a>
            <nav className="nav-links" aria-label="Главное меню">
              <a href="#ipo">IPO</a>
              <a className="is-current" href="#investors">Инвесторам</a>
              <a href="#products">Эмитентам</a>
              <a href="#market">Рыночная информация</a>
              <a href="#group">О бирже</a>
            </nav>
            <div className="header-actions">
              <button className="icon-button" aria-label="Поиск">⌕</button>
              <button className="icon-button" aria-label="Корзина">⌑</button>
              <div className="time-box">
                <span>Четверг</span>
                <b>21 мая 20:04</b>
              </div>
              <button className="red-button">Войти</button>
            </div>
          </div>
          <nav className="market-nav" aria-label="Разделы рынка">
            <a href="#market">Индексы</a>
            <a href="#market">Фондовый рынок</a>
            <a href="#market">Срочный рынок</a>
            <a href="#products">Рынок СПФИ</a>
            <a href="#calendar">Денежный рынок</a>
            <a href="#products">Рынок драгоценных металлов</a>
            <a href="#market">Валютный рынок</a>
            <a href="#news">Еще</a>
          </nav>
        </div>
      </header>

      {/* Основной контент */}
      <main>
        {/* Промо баннеры */}
        <section className="page promo-grid" id="investors">
          <article className="promo-card promo-main">
            <div>
              <h1>Участвуйте в движении процентных ставок</h1>
              <p>Новые фьючерсы на индекс RUONIA уже в торгах</p>
              <button className="red-button">Торговать</button>
            </div>
            <div className="rate-visual" aria-hidden="true">
              <span></span><span></span><span></span>
              <strong>%</strong>
            </div>
          </article>
          <article className="promo-card">
            <div className="small-visual blue"></div>
            <h2>Лучший частный инвестор 2026</h2>
            <p>Призовой фонд 100 млн рублей</p>
          </article>
          <article className="promo-card">
            <div className="small-visual red"></div>
            <h2>Крипто без криптобиржи</h2>
            <p>Новые фьючерсы на криптоиндексы уже в торгах</p>
          </article>
          <article className="promo-card wide">
            <div>
              <h2>Время покупать драгметаллы</h2>
              <p>на Московской бирже</p>
            </div>
            <div className="gold-bars" aria-hidden="true"><i></i><i></i><i></i></div>
          </article>
        </section>

        {/* Карта рынка */}
        <section className="page section" id="market">
          <h2 className="section-title">Карта рынка</h2>
          <div className="heatmap-layout">
            <div>
              <h3 className="map-title">Акции</h3>
              <div className="heatmap" id="sharesMap">
                {shares.map((item, idx) => (
                  <button
                    key={idx}
                    className={`tile ${tileTone(item.change)} ${item.size || ''}`}
                    onClick={() => setActiveInstrument(item)}
                  >
                    <b>{item.ticker}</b>
                    <span>{item.price}</span>
                    <small>{item.change > 0 ? '+' : ''}{item.change.toFixed(2)}%</small>
                  </button>
                ))}
              </div>
            </div>
            <div>
              <h3 className="map-title">Фьючерсы</h3>
              <div className="heatmap" id="futuresMap">
                {futures.map((item, idx) => (
                  <button
                    key={idx}
                    className={`tile ${tileTone(item.change)} ${item.size || ''}`}
                    onClick={() => setActiveInstrument(item)}
                  >
                    <b>{item.ticker}</b>
                    <span>{item.price}</span>
                    <small>{item.change > 0 ? '+' : ''}{item.change.toFixed(2)}%</small>
                  </button>
                ))}
              </div>
            </div>
          </div>
          <div className="market-note">
            <p>Получите доступ к углубленной аналитике MOEX: рыночные дисбалансы, индексы концентрации, открытый интерес и еще более 50 индикаторов</p>
            <button className="light-button">Поделиться картой</button>
            <button className="red-button">Попробовать</button>
          </div>
          <p className="caption">Данные отображаются с задержкой в 15 минут.</p>
        </section>

        {/* Табы Продуктов */}
        <section className="page section" id="products">
          <div className="section-row">
            <h2 className="section-title">Продукты</h2>
            <div className="segmented" id="productTabs">
              {['popular', 'investors', 'issuers', 'pros'].map((group) => (
                <button
                  key={group}
                  className={productTab === group ? 'is-active' : ''}
                  onClick={() => setProductTab(group)}
                >
                  {group === 'popular' && 'Популярное'}
                  {group === 'investors' && 'Инвесторам'}
                  {group === 'issuers' && 'Эмитентам'}
                  {group === 'pros' && 'Профучастникам'}
                </button>
              ))}
            </div>
          </div>
          <div className="product-grid" id="productGrid">
            {productGroups[productTab].map(([title, text, icon], idx) => (
              <article key={idx} className="product-card">
                <h3>{title}</h3>
                <p>{text}</p>
                <span className="product-icon">{icon}</span>
              </article>
            ))}
          </div>
        </section>

        {/* Интерактивный график Тенденции */}
        <section className="page section trends-section">
          <div className="section-row left">
            <h2 className="section-title">Тенденции</h2>
            <select
              id="trendSelect"
              className="select"
              value={trendKind}
              onChange={(e) => {
                setTrendKind(e.target.value);
                setTrendActiveIndex(0);
              }}
            >
              <option value="shares">Индексы / Акции</option>
              <option value="bonds">Облигации</option>
            </select>
          </div>
          <div className="trend-tabs" id="trendTabs">
            {['shares', 'bonds', 'pension'].map((kind) => (
              <button
                key={kind}
                className={trendKind === kind ? 'is-active' : ''}
                onClick={() => {
                  setTrendKind(kind);
                  setTrendActiveIndex(0);
                  setTrendHoverIndex(null);
                }}
              >
                {kind === 'shares' && 'Акции'}
                {kind === 'bonds' && 'Облигации'}
                {kind === 'pension' && 'Пенсионные'}
              </button>
            ))}
          </div>
          <div className="trends-grid">
            <div className="trend-list" id="trendList">
              {trends[trendKind].map((item, idx) => (
                <button
                  key={idx}
                  className={`trend-row ${idx === trendActiveIndex ? 'is-active' : ''}`}
                  onClick={() => {
                    setTrendActiveIndex(idx);
                    setTrendHoverIndex(null);
                  }}
                >
                  <b>{item[0]}</b>
                  <span>
                    <b>{item[1]} <em className="positive">{item[2]}</em></b>
                    <small>Время расчета {item[3]}</small>
                  </span>
                </button>
              ))}
            </div>
            <div className="chart-panel">
              <canvas
                ref={canvasRef}
                id="trendChart"
                width="640"
                height="330"
                onMouseMove={handleMouseMove}
                onMouseLeave={() => setTrendHoverIndex(null)}
              ></canvas>
            </div>
          </div>
        </section>

        {/* Календарь */}
        <section className="calendar-section" id="calendar">
          <div className="page">
            <div className="section-row">
              <div className="section-row left">
                <h2 className="section-title">Календарь</h2>
                <div className="segmented dark">
                  <button className="is-active">Торговый</button>
                  <button>Мероприятий</button>
                </div>
              </div>
              <button className="light-button">Все события</button>
            </div>
            <div className="api-banner">
              <b>Календарь торговых дней также доступен по API</b>
              <button className="red-button">Оформить подписку</button>
            </div>
            <div className="calendar-card">
              <div className="calendar-head">
                <h3 id="calendarTitle">{monthNames[calendarState.month]} {calendarState.year}</h3>
                <div className="calendar-controls">
                  <select
                    id="monthSelect"
                    className="select small-select"
                    aria-label="Месяц"
                    value={calendarState.month}
                    onChange={handleMonthChange}
                  >
                    {monthNames.map((month, idx) => (
                      <option key={idx} value={idx}>{month}</option>
                    ))}
                  </select>
                  <select
                    id="yearSelect"
                    className="select small-select"
                    aria-label="Год"
                    value={calendarState.year}
                    onChange={handleYearChange}
                  >
                    {Array.from({ length: 10 }, (_, i) => 2026 + i).map(y => (
                      <option key={y} value={y}>{y}</option>
                    ))}
                  </select>
                  <button className="square-button" onClick={() => stepMonth(-1)} aria-label="Предыдущий месяц">‹</button>
                  <button className="square-button" onClick={() => stepMonth(1)} aria-label="Следующий месяц">›</button>
                </div>
              </div>
              <div className="days-row" id="daysRow">
                {Array.from({ length: daysCount }, (_, idx) => {
                  const day = idx + 1;
                  const date = new Date(calendarState.year, calendarState.month, day);
                  const active = day === calendarState.selectedDay;
                  return (
                    <button
                      key={day}
                      className={`day-button ${active ? 'is-active' : ''}`}
                      onClick={() => setCalendarState(prev => ({ ...prev, selectedDay: day }))}
                    >
                      <span>{weekdayNames[date.getDay()]}</span>
                      <b>{String(day).padStart(2, '0')}</b>
                      <span className="dots">
                        <i style={{ background: '#f00' }}></i>
                        <i style={{ background: '#219400' }}></i>
                        <i style={{ background: '#4168ff' }}></i>
                      </span>
                    </button>
                  );
                })}
              </div>
              <div className="events-grid" id="eventsGrid">
                {calendarEvents.map(([title, rows], idx) => (
                  <div key={idx} className="event-column">
                    <h4>{title}</h4>
                    {rows.map((row, rIdx) => rIdx === 0 ? (
                      <b key={rIdx}>{row}</b>
                    ) : (
                      <p key={rIdx}>
                        {row.includes(' ') ? row.split(' ').slice(0, -1).join(' ') : row}
                        <span>{row.split(' ').at(-1)}</span>
                      </p>
                    ))}
                    <small>Выбранный день: {calendarState.selectedDay} {monthNames[calendarState.month].toLowerCase()} {calendarState.year}</small>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Новости */}
        <section className="page section" id="news">
          <div className="section-row">
            <h2 className="section-title">Новости</h2>
            <button className="light-button">Все новости</button>
          </div>
          <div className="news-grid" id="newsGrid">
            {news.map(([date, title], idx) => (
              <article key={idx} className="news-card">
                <time>{date}</time><small>Главные</small>
                <h3>{title}</h3>
              </article>
            ))}
          </div>
        </section>

        {/* IPO */}
        <section className="page section" id="ipo">
          <div className="section-row">
            <h2 className="section-title">IPO на MOEX</h2>
            <button className="red-button">Все IPO</button>
          </div>
          <div className="ipo-grid" id="ipoGrid">
            {ipoItems.map(([name, area, date, price, logo], idx) => (
              <article key={idx} className="ipo-card">
                <div className="ipo-top">
                  <span className="round-logo">{logo}</span>
                  <div>
                    <h3>{name}</h3>
                    <p>{area}</p>
                  </div>
                </div>
                <div className="ipo-info">
                  <span><small>Дата размещения</small><b>{date}</b></span>
                  <span><small>Цена размещения акции</small><b>{price}</b></span>
                </div>
              </article>
            ))}
          </div>
        </section>

        {/* Метрики успеха */}
        <section className="page section" id="metrics">
          <h2 className="section-title">Метрики успеха</h2>
          <div className="metrics-grid">
            <article className="metric-card">
              <span>01</span>
              <h3>Скорость подбора</h3>
              <p>Пользователь быстро переходит от типа инструмента к ключевым карточкам и деталям.</p>
            </article>
            <article className="metric-card">
              <span>02</span>
              <h3>Понятность данных</h3>
              <p>Цена, изменение, сектор, объем и календарные события читаются без лишней нагрузки.</p>
            </article>
            <article className="metric-card">
              <span>03</span>
              <h3>Интерактивность</h3>
              <p>Карточки, график, календарь и вкладки дают быстрый отклик без обращения к серверу.</p>
            </article>
            <article className="metric-card">
              <span>04</span>
              <h3>Мобильный доступ</h3>
              <p>Основные сценарии доступны на телефоне: просмотр рынка, продуктов, новостей и деталей.</p>
            </article>
          </div>
        </section>

        {/* О группе */}
        <section className="page section" id="group">
          <h2 className="section-title">MOEX Group</h2>
          <div className="group-grid">
            <article className="group-card large">
              <button className="corner-button">↗</button>
              <h3>Национальный клиринговый центр</h3>
              <p>Услуги центрального контрагента и клиринговой организации</p>
            </article>
            <article className="group-card large">
              <button className="corner-button">↗</button>
              <h3>Национальный расчетный депозитарий</h3>
              <p>Услуги центрального депозитария, расчетного банка и торгового репозитария</p>
            </article>
            <article className="group-card">
              <button className="corner-button">↗</button>
              <h3>Школа Московской Биржи</h3>
              <p>Инвестируем грамотно. Руководство для начинающих и опытных инвесторов.</p>
            </article>
            <article className="group-card">
              <button className="corner-button">↗</button>
              <h3>Финуслуги</h3>
              <p>Маркетплейс финансовых услуг от Мосбиржи.</p>
            </article>
            <article className="group-card">
              <button className="corner-button">↗</button>
              <h3>Венчурный фонд МБ Инновации</h3>
              <p>Поддержка инновационных технологий финансового рынка России.</p>
            </article>
          </div>
        </section>
      </main>

      {/* Футер */}
      <footer className="site-footer">
        <div className="page footer-grid">
          <div>
            <a className="logo footer-logo" href="#"><span>MOEX</span><small>Московская<br />Биржа</small></a>
            <p>Интернет-приемная</p>
            <p>Обратный звонок</p>
            <b>+7 495 363-32-32</b>
            <b>+7 495 232-33-63</b>
          </div>
          <div>
            <h3>Инвесторам</h3>
            <a href="#market">Фондовый рынок</a>
            <a href="#market">Срочный рынок</a>
            <a href="#calendar">Денежный рынок</a>
            <a href="#market">Валютный рынок</a>
          </div>
          <div>
            <h3>Эмитентам</h3>
            <a href="#products">Эмитенту облигаций</a>
            <a href="#products">Эмитенту акций</a>
            <a href="#ipo">IPO на MOEX</a>
          </div>
          <div>
            <h3>Рыночная информация</h3>
            <a href="#products">Продукты и сервисы</a>
            <a href="#calendar">Ход торгов</a>
            <a href="#market">Индексы</a>
          </div>
          <div>
            <h3>О бирже</h3>
            <a href="#news">Пресс-центр</a>
            <a href="#group">MOEX Group</a>
            <a href="#group">Контакты</a>
          </div>
        </div>
      </footer>

      {/* Баннер куки */}
      {!cookieAccepted && (
        <div className="cookie" id="cookiePanel">
          <div className="page cookie-inner">
            <p>На сайте осуществляется обработка пользовательских данных с использованием Cookie. Оставаясь на сайте, вы соглашаетесь с условиями правил.</p>
            <button className="link-button">Настроить</button>
            <button className="light-button" id="acceptCookie" onClick={() => setCookieAccepted(true)}>Согласен</button>
          </div>
        </div>
      )}

      {/* Модалка с деталями */}
      <div className={`modal ${activeInstrument ? 'is-open' : ''}`} id="instrumentModal" aria-hidden={!activeInstrument}>
        <div className="modal-window" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
          <button className="modal-close" id="closeModal" onClick={() => setActiveInstrument(null)} aria-label="Закрыть">×</button>
          <p className="eyebrow" id="modalKind">
            {activeInstrument && (activeInstrument.change >= 0 ? 'Растущий инструмент' : 'Снижение за день')}
          </p>
          <h2 id="modalTitle">{activeInstrument?.ticker}</h2>
          <p id="modalName">{activeInstrument?.name}</p>
          <div className="modal-stats">
            <span><small>Цена</small><b id="modalPrice">{activeInstrument?.price} ₽</b></span>
            <span>
              <small>Изменение</small>
              <b id="modalChange" style={{ color: activeInstrument?.change >= 0 ? '#178b31' : '#ee3124' }}>
                {activeInstrument && (activeInstrument.change > 0 ? '+' : '')}{activeInstrument?.change.toFixed(2)}%
              </b>
            </span>
            <span><small>Сектор</small><b id="modalSector">{activeInstrument?.sector}</b></span>
            <span><small>Объем</small><b id="modalVolume">{activeInstrument?.volume}</b></span>
          </div>
          <div className="mini-chart" id="modalChart">
            {activeInstrument && Array.from({ length: 16 }, (_, i) => {
              const height = Math.max(22, Math.min(100, 42 + Math.sin(i + activeInstrument.change) * 22 + i * (activeInstrument.change > 0 ? 3 : -1)));
              return <i key={i} style={{ height: `${height}%` }}></i>;
            })}
          </div>
        </div>
      </div>
    </div>
  );
}