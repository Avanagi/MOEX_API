CREATE TABLE IF NOT EXISTS instruments (
    ticker VARCHAR(50) PRIMARY KEY,
    name VARCHAR(500),
    type VARCHAR(20),
    sector VARCHAR(200),
    price NUMERIC,
    volume BIGINT,
    currency VARCHAR(10),
    updated_at TIMESTAMP,
    yield NUMERIC,
    maturity_date DATE,
    market_cap BIGINT,
    issuer VARCHAR(300),
    volatility NUMERIC,
    strike_price NUMERIC,
    option_type VARCHAR(5)
);