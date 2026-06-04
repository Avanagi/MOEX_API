export default function StatPill({ label, value, note }) {
  return (
    <article className="stat-pill">
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
      <div className="stat-note">{note}</div>
    </article>
  )
}