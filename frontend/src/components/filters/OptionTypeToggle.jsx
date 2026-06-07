import './OptionTypeToggle.css'

const OPTIONS = [
  { value: '', label: 'Все', color: '' },
  { value: 'C', label: 'Call', color: '#22C55E' },
  { value: 'P', label: 'Put', color: '#E879F9' },
]

export default function OptionTypeToggle({ value, onChange }) {
  return (
    <div className="option-type-toggle">
      <div className="option-type-toggle-label">Тип опциона</div>
      <div className="option-type-toggle-group">
        {OPTIONS.map((opt) => (
          <button
            key={opt.value}
            className={`option-toggle-btn${value === opt.value ? ' active' : ''}`}
            onClick={() => onChange(opt.value)}
            style={value === opt.value && opt.color ? { '--opt-color': opt.color } : {}}
          >
            <span className="option-toggle-dot" style={{ background: opt.color || 'var(--text3)' }} />
            {opt.label}
          </button>
        ))}
      </div>
    </div>
  )
}
