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
    { ticker: 'NVTK', name: 'Новатэк', price: '1126.60', change: 0.41, sector: 'Энергетика', volume: '1,8 млрд ₽' },
    { ticker: 'TATN', name: 'Татнефть', price: '636.70', change: 3.33, sector: 'Энергетика', volume: '1,4 млрд ₽' },
    { ticker: 'RUAL', name: 'Русал', price: '35.51', change: -0.74, sector: 'Металлы', volume: '760 млн ₽' },
    { ticker: 'GMKN', name: 'Норникель', price: '129.46', change: 1.89, sector: 'Металлы', volume: '1,1 млрд ₽' },
    { ticker: 'VKCO', name: 'VK', price: '246.10', change: 4.13, sector: 'IT', volume: '890 млн ₽' },
    { ticker: 'PLZL', name: 'Полюс', price: '2 100.00', change: 1.40, sector: 'Металлы', volume: '1,6 млрд ₽' },
    { ticker: 'AFLT', name: 'Аэрофлот', price: '47.99', change: 2.70, sector: 'Транспорт', volume: '670 млн ₽' },
    { ticker: 'OZON', name: 'Ozon', price: '4 205.50', change: 1.74, sector: 'IT', volume: '2,2 млрд ₽' },
    { ticker: 'YDEX', name: 'Яндекс', price: '4 080.00', change: 1.12, sector: 'IT', volume: '5,9 млрд ₽' },
    { ticker: 'MOEX', name: 'Московская Биржа', price: '175.66', change: 1.43, sector: 'Финансы', volume: '820 млн ₽' },
    { ticker: 'SMLT', name: 'Самолет', price: '504.20', change: 2.31, sector: 'Недвижимость', volume: '430 млн ₽' }
];

const futures = [
    { ticker: 'CRM6', name: 'CNY/RUB', price: '10.53', change: -0.37, sector: 'Валютный рынок', volume: '1,9 млрд ₽', size: 'size-lg' },
    { ticker: 'BRM6', name: 'Brent', price: '107.09', change: 1.33, sector: 'Товарный рынок', volume: '9,6 млрд ₽', size: 'size-lg' },
    { ticker: 'SiM6', name: 'USD/RUB', price: '71 677.00', change: -0.28, sector: 'Валютный рынок', volume: '18,8 млрд ₽', size: 'size-lg' },
    { ticker: 'CNYRUBF', name: 'CNY/RUB Futures', price: '10.43', change: -0.32, sector: 'Валютный рынок', volume: '820 млн ₽', size: 'size-md' },
    { ticker: 'MXM6', name: 'Индекс МосБиржи', price: '268 800.00', change: 1.20, sector: 'Индексы', volume: '5,4 млрд ₽', size: 'size-md' },
    { ticker: 'GDM6', name: 'Золото', price: '4 512.40', change: -0.68, sector: 'Металлы', volume: '2,1 млрд ₽', size: 'size-md' },
    { ticker: 'SVM6', name: 'Серебро', price: '76.88', change: -0.21, sector: 'Металлы', volume: '740 млн ₽', size: 'size-md' },
    { ticker: 'USDRUBF', name: 'USD/RUB Futures', price: '71.19', change: -0.24, sector: 'Валютный рынок', volume: '4,3 млрд ₽' },
    { ticker: 'IMOEXF', name: 'Индексный фьючерс', price: '2 660.50', change: 1.08, sector: 'Индексы', volume: '3,7 млрд ₽' },
    { ticker: 'NGK6', name: 'Газ', price: '3.04', change: 0.03, sector: 'Товарный рынок', volume: '590 млн ₽' },
    { ticker: 'SiU6', name: 'USD/RUB', price: '72 716.00', change: -0.37, sector: 'Валютный рынок', volume: '1,2 млрд ₽' },
    { ticker: 'RIM6', name: 'RTS Index', price: '118 190.00', change: 1.49, sector: 'Индексы', volume: '2,9 млрд ₽' },
    { ticker: 'EuM6', name: 'EUR/RUB', price: '82 985.00', change: -0.54, sector: 'Валютный рынок', volume: '620 млн ₽' },
    { ticker: 'CCM6', name: 'Какао', price: '274.60', change: -3.62, sector: 'Товарный рынок', volume: '180 млн ₽' },
    { ticker: 'BRN6', name: 'Brent', price: '103.38', change: 1.57, sector: 'Товарный рынок', volume: '8,7 млрд ₽' },
    { ticker: 'BMM6', name: 'Металлы', price: '107.06', change: 1.33, sector: 'Металлы', volume: '530 млн ₽' },
    { ticker: 'MMM6', name: 'Индекс', price: '2 688.40', change: 1.24, sector: 'Индексы', volume: '950 млн ₽' },
    { ticker: 'NAM6', name: 'NASDAQ', price: '28 963.00', change: -0.31, sector: 'Индексы', volume: '410 млн ₽' }
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

const calendarState = {
    month: 4,
    year: 2026,
    selectedDay: 21
};

const chartState = {
    kind: 'shares',
    activeIndex: 0,
    hoverIndex: null,
    points: []
};

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

const allInstruments = [...shares, ...futures];

function qs(selector) {
    return document.querySelector(selector);
}

function qsa(selector) {
    return Array.from(document.querySelectorAll(selector));
}

function renderTicker() {
    qs('#tickerLine').innerHTML = tickerData.map(([name, value, direction]) => `
    <span class="ticker-item">
      <b>${name}</b>
      <span>${value}</span>
      <span class="${direction}">${direction === 'up' ? '↑' : '↓'}</span>
      <small class="badge-change">-2,${Math.floor(Math.random() * 9)}%</small>
    </span>
  `).join('');
}

function tileTone(change) {
    if (change < -3) return 'bad strong';
    if (change < 0) return 'bad';
    if (change > 3) return 'good';
    return 'good soft';
}

function renderHeatmap(id, items) {
    qs(id).innerHTML = items.map(item => `
    <button class="tile ${tileTone(item.change)} ${item.size || ''}" data-ticker="${item.ticker}">
      <b>${item.ticker}</b>
      <span>${item.price}</span>
      <small>${item.change > 0 ? '+' : ''}${item.change.toFixed(2)}%</small>
    </button>
  `).join('');
}

function renderProducts(group = 'popular') {
    qs('#productGrid').innerHTML = productGroups[group].map(([title, text, icon]) => `
    <article class="product-card">
      <h3>${title}</h3>
      <p>${text}</p>
      <span class="product-icon">${icon}</span>
    </article>
  `).join('');
}

function renderTrends(kind = 'shares') {
    qs('#trendList').innerHTML = trends[kind].map((item, index) => `
    <button class="trend-row ${index === 0 ? 'is-active' : ''}" data-index="${index}">
      <b>${item[0]}</b>
      <span>
        <b>${item[1]} <em class="positive">${item[2]}</em></b>
        <small>Время расчета ${item[3]}</small>
      </span>
    </button>
  `).join('');
    chartState.kind = kind;
    chartState.activeIndex = 0;
    chartState.hoverIndex = null;
    drawTrendChart(kind, 0);
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

function drawTrendChart(kind = chartState.kind, activeIndex = chartState.activeIndex, hoverIndex = chartState.hoverIndex) {
    const canvas = qs('#trendChart');
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    const values = makeChartValues(kind, activeIndex);
    const minValue = 2610;
    const maxValue = 2674;
    const leftPad = 12;
    const rightPad = 78;
    const topPad = 28;
    const bottomPad = 42;
    const chartWidth = width - leftPad - rightPad;
    const chartHeight = height - topPad - bottomPad;

    chartState.kind = kind;
    chartState.activeIndex = activeIndex;
    chartState.hoverIndex = hoverIndex;
    chartState.points = values.map((value, index) => {
        const x = leftPad + (index / (values.length - 1)) * chartWidth;
        const y = topPad + (1 - (value - minValue) / (maxValue - minValue)) * chartHeight;
        return { x, y, value };
    });

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
    chartState.points.forEach((point, index) => {
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

    if (hoverIndex !== null && chartState.points[hoverIndex]) {
        drawChartTooltip(ctx, canvas, chartState.points[hoverIndex], hoverIndex);
    }
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

function drawChartTooltip(ctx, canvas, point, hoverIndex) {
    const width = canvas.width;
    const height = canvas.height;
    const activeTicker = trends[chartState.kind][chartState.activeIndex][0];
    const date = new Date(2026, 4, 21, 18, Math.min(59, 6 + hoverIndex), 59);
    const value = point.value.toLocaleString('ru-RU', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
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
    ctx.fillText(value, tooltipX + tooltipWidth - 16, tooltipY + 28);
    ctx.fillText(date.toLocaleString('ru-RU'), tooltipX + tooltipWidth - 16, tooltipY + 56);
    ctx.textAlign = 'left';
    ctx.restore();
}

function fillCalendarSelects() {
    qs('#monthSelect').innerHTML = monthNames.map((month, index) => `
    <option value="${index}">${month}</option>
  `).join('');

    qs('#yearSelect').innerHTML = Array.from({ length: 25 }, (_, index) => 2026 + index).map(year => `
    <option value="${year}">${year}</option>
  `).join('');
}

function daysInMonth(year, month) {
    return new Date(year, month + 1, 0).getDate();
}

function syncCalendarHeader() {
    qs('#calendarTitle').textContent = `${monthNames[calendarState.month]} ${calendarState.year}`;
    qs('#monthSelect').value = String(calendarState.month);
    qs('#yearSelect').value = String(calendarState.year);
}

function renderCalendar() {
    const daysCount = daysInMonth(calendarState.year, calendarState.month);
    if (calendarState.selectedDay > daysCount) {
        calendarState.selectedDay = daysCount;
    }

    syncCalendarHeader();
    qs('#daysRow').innerHTML = Array.from({ length: daysCount }, (_, index) => {
        const day = index + 1;
        const date = new Date(calendarState.year, calendarState.month, day);
        const active = day === calendarState.selectedDay;
        return `
      <button class="day-button ${active ? 'is-active' : ''}" data-day="${day}">
        <span>${weekdayNames[date.getDay()]}</span>
        <b>${String(day).padStart(2, '0')}</b>
        <span class="dots"><i style="background:#f00"></i><i style="background:#219400"></i><i style="background:#4168ff"></i></span>
      </button>
    `;
    }).join('');
    renderEvents(calendarState.selectedDay);
}

function renderEvents(day) {
    const month = monthNames[calendarState.month].toLowerCase();
    qs('#eventsGrid').innerHTML = calendarEvents.map(([title, rows]) => `
    <div class="event-column">
      <h4>${title}</h4>
      ${rows.map((row, index) => index === 0 ? `<b>${row}</b>` : `<p>${row.includes(' ') ? row.split(' ').slice(0, -1).join(' ') : row}<span>${row.split(' ').at(-1)}</span></p>`).join('')}
      <small>Выбранный день: ${day} ${month} ${calendarState.year}</small>
    </div>
  `).join('');
}

function renderNews() {
    qs('#newsGrid').innerHTML = news.map(([date, title]) => `
    <article class="news-card">
      <time>${date}</time><small>Главные</small>
      <h3>${title}</h3>
    </article>
  `).join('');
}

function renderIpo() {
    qs('#ipoGrid').innerHTML = ipoItems.map(([name, area, date, price, logo]) => `
    <article class="ipo-card">
      <div class="ipo-top">
        <span class="round-logo">${logo}</span>
        <div>
          <h3>${name}</h3>
          <p>${area}</p>
        </div>
      </div>
      <div class="ipo-info">
        <span><small>Дата размещения</small><b>${date}</b></span>
        <span><small>Цена размещения акции</small><b>${price}</b></span>
      </div>
    </article>
  `).join('');
}

function openInstrument(ticker) {
    const item = allInstruments.find(entry => entry.ticker === ticker);
    if (!item) return;

    qs('#modalKind').textContent = item.change >= 0 ? 'Растущий инструмент' : 'Снижение за день';
    qs('#modalTitle').textContent = item.ticker;
    qs('#modalName').textContent = item.name;
    qs('#modalPrice').textContent = `${item.price} ₽`;
    qs('#modalChange').textContent = `${item.change > 0 ? '+' : ''}${item.change.toFixed(2)}%`;
    qs('#modalChange').style.color = item.change >= 0 ? '#178b31' : '#ee3124';
    qs('#modalSector').textContent = item.sector;
    qs('#modalVolume').textContent = item.volume;
    qs('#modalChart').innerHTML = Array.from({ length: 16 }, (_, i) => {
        const height = Math.max(22, Math.min(100, 42 + Math.sin(i + item.change) * 22 + i * (item.change > 0 ? 3 : -1)));
        return `<i style="height:${height}%"></i>`;
    }).join('');

    qs('#instrumentModal').classList.add('is-open');
    qs('#instrumentModal').setAttribute('aria-hidden', 'false');
}

function closeInstrument() {
    qs('#instrumentModal').classList.remove('is-open');
    qs('#instrumentModal').setAttribute('aria-hidden', 'true');
}

function bindEvents() {
    qs('#productTabs').addEventListener('click', event => {
        const button = event.target.closest('button[data-group]');
        if (!button) return;
        qsa('#productTabs button').forEach(item => item.classList.remove('is-active'));
        button.classList.add('is-active');
        renderProducts(button.dataset.group);
    });

    qs('#trendTabs').addEventListener('click', event => {
        const button = event.target.closest('button[data-kind]');
        if (!button) return;
        qsa('#trendTabs button').forEach(item => item.classList.remove('is-active'));
        button.classList.add('is-active');
        renderTrends(button.dataset.kind);
    });

    qs('#trendList').addEventListener('click', event => {
        const row = event.target.closest('.trend-row');
        if (!row) return;
        qsa('.trend-row').forEach(item => item.classList.remove('is-active'));
        row.classList.add('is-active');
        const activeKind = qs('#trendTabs .is-active').dataset.kind;
        chartState.hoverIndex = null;
        drawTrendChart(activeKind, Number(row.dataset.index), null);
    });

    qs('#trendChart').addEventListener('mousemove', event => {
        const canvas = event.currentTarget;
        const rect = canvas.getBoundingClientRect();
        const x = (event.clientX - rect.left) * (canvas.width / rect.width);
        const nearest = chartState.points.reduce((best, point, index) => {
            const distance = Math.abs(point.x - x);
            return distance < best.distance ? { index, distance } : best;
        }, { index: 0, distance: Infinity });
        drawTrendChart(chartState.kind, chartState.activeIndex, nearest.index);
    });

    qs('#trendChart').addEventListener('mouseleave', () => {
        drawTrendChart(chartState.kind, chartState.activeIndex, null);
    });

    qs('#trendSelect').addEventListener('change', event => {
        const next = event.target.value === 'indices' ? 'shares' : event.target.value;
        const tab = qs(`#trendTabs [data-kind="${next}"]`);
        if (tab) tab.click();
    });

    qs('#daysRow').addEventListener('click', event => {
        const button = event.target.closest('.day-button');
        if (!button) return;
        qsa('.day-button').forEach(item => item.classList.remove('is-active'));
        button.classList.add('is-active');
        calendarState.selectedDay = Number(button.dataset.day);
        renderEvents(calendarState.selectedDay);
    });

    qs('#monthSelect').addEventListener('change', event => {
        calendarState.month = Number(event.target.value);
        renderCalendar();
    });

    qs('#yearSelect').addEventListener('change', event => {
        calendarState.year = Number(event.target.value);
        renderCalendar();
    });

    qs('#prevMonth').addEventListener('click', () => {
        if (calendarState.year === 2026 && calendarState.month === 0) return;
        calendarState.month -= 1;
        if (calendarState.month < 0) {
            calendarState.month = 11;
            calendarState.year -= 1;
        }
        renderCalendar();
    });

    qs('#nextMonth').addEventListener('click', () => {
        calendarState.month += 1;
        if (calendarState.month > 11) {
            calendarState.month = 0;
            calendarState.year += 1;
        }
        const yearSelect = qs('#yearSelect');
        if (![...yearSelect.options].some(option => Number(option.value) === calendarState.year)) {
            yearSelect.insertAdjacentHTML('beforeend', `<option value="${calendarState.year}">${calendarState.year}</option>`);
        }
        renderCalendar();
    });

    document.body.addEventListener('click', event => {
        const tile = event.target.closest('.tile');
        if (tile) openInstrument(tile.dataset.ticker);
    });

    qs('#closeModal').addEventListener('click', closeInstrument);
    qs('#instrumentModal').addEventListener('click', event => {
        if (event.target.id === 'instrumentModal') closeInstrument();
    });
    document.addEventListener('keydown', event => {
        if (event.key === 'Escape') closeInstrument();
    });

    qs('#acceptCookie').addEventListener('click', () => {
        qs('#cookiePanel').style.display = 'none';
    });
}

function init() {
    renderTicker();
    renderHeatmap('#sharesMap', shares);
    renderHeatmap('#futuresMap', futures);
    renderProducts();
    renderTrends();
    fillCalendarSelects();
    renderCalendar();
    renderNews();
    renderIpo();
    bindEvents();
}

init();