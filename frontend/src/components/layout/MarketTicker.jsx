import { marketTicker } from '../../data/market'

export default function MarketTicker() {
  return (
    <section className="top-strip">
      {marketTicker.map((item) => {
        const positive = item.change.startsWith('+')

        return (
          <article className="ticker-card" key={item.symbol}>
            <div className="ticker-symbol">{item.symbol}</div>

            <div className="ticker-row">
              <strong>{item.price}</strong>
              <span className={positive ? 'is-positive' : 'is-negative'}>{item.change}</span>
            </div>
          </article>
        )
      })}
    </section>
  )
}