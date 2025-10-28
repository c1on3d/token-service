# Token Service

Service for handling new token creation events from pump.fun and bonk.fun.

## Deploy to Render

1. Push this folder to a GitHub repository
2. Go to https://render.com
3. Click "New +" → "Web Service"
4. Connect your GitHub repo
5. Configure:
   - **Name**: token-service
   - **Root Directory**: token-service (if in a monorepo)
   - **Build Command**: `npm install`
   - **Start Command**: `npm start`

6. Add Environment Variables:
   - `DB_HOST` - Your database host
   - `DB_PORT` - Database port (usually 5432)
   - `DB_USER` - Database username
   - `DB_PASSWORD` - Database password
   - `DB_NAME` - Database name
   - `DB_SSL` - Set to `true` if using SSL

7. Click "Create Web Service"

## Database Schema

Run this SQL to create the tokens table:

```sql
CREATE TABLE IF NOT EXISTS tokens (
  id SERIAL PRIMARY KEY,
  mint VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  symbol VARCHAR(255),
  signature VARCHAR(255),
  trader_public_key VARCHAR(255),
  initial_buy NUMERIC,
  sol_amount NUMERIC,
  market_cap_sol NUMERIC,
  bonding_curve_key VARCHAR(255),
  v_tokens_in_bonding_curve NUMERIC,
  v_sol_in_bonding_curve NUMERIC,
  uri TEXT,
  pool VARCHAR(50),
  tx_type VARCHAR(50),
  twitter TEXT,
  telegram TEXT,
  website TEXT,
  image TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tokens_mint ON tokens(mint);
CREATE INDEX idx_tokens_created_at ON tokens(created_at DESC);
```

## Update Listener

After deploying, update the `ENRICHER_URL` in your `pumpportal_listener.py`:

```python
ENRICHER_URL = "https://your-service-name.onrender.com/tokens/add"
```
