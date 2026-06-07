import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import FiltersPage from './pages/FiltersPage';

const tickerData = [
  ['¥', '10,435', 'down', '-2.4%'],
  ['₺', '1,56', 'down', '-2.1%'],
  ['T', '15,65', 'up', '+1.8%'],
  ['Br', '25,805', 'down', '-0.9%'],
  ['SARE', '0,751', 'down', '-1.5%'],
  ['ZVEZ', '6,12', 'down', '-2.3%'],
  ['LVHK', '23,20', 'down', '-0.5%'],
  ['SOFL', '61,60', 'down', '-1.1%'],
  ['RU000A106N57', '1025,00', 'down', '-0.2%']
];

function Home() {
  return (
    <div className="moex-app">
      {/* Бегущая строка */}
      <div className="ticker-strip">
        <div className="page ticker-line">
          {tickerData.map(([name, value, direction, percentage], idx) => (
            <span key={idx} className="ticker-item">
              <b>{name}</b>
              <span>{value}</span>
              <span className={direction}>{direction === 'up' ? '↑' : '↓'}</span>
              <small className="badge-change">{percentage}</small>
            </span>
          ))}
        </div>
      </div>

      <div style={{
        fontFamily: 'Arial, sans-serif',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '80vh',
        background: '#f5f7fa',
        color: '#26313d',
        textAlign: 'center',
        padding: '20px',
        boxSizing: 'border-box'
      }}>
        <h1 style={{ fontSize: '36px', marginBottom: '10px', color: '#101828' }}>Московская Биржа</h1>
        <p style={{ color: '#667085', fontSize: '18px', marginBottom: '30px', maxWidth: '500px' }}>
          Добро пожаловать в веб-интерфейс терминала. Перейдите к нашей системе умного подбора активов.
        </p>

        <Link to="/filters" style={{
          display: 'inline-block',
          padding: '14px 32px',
          background: '#4168ff',
          color: '#ffffff',
          textDecoration: 'none',
          borderRadius: '8px',
          fontWeight: 'bold',
          fontSize: '18px',
          boxShadow: '0 4px 14px rgba(65, 104, 255, 0.3)',
          transition: 'all 0.2s ease'
        }}>
          Перейти к подбору инструментов →
        </Link>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/filters" element={<FiltersPage />} />
      </Routes>
    </BrowserRouter>
  );
}