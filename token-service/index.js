import express from 'express';
import pkg from 'pg';
const { Pool } = pkg;

const app = express();
app.use(express.json());

// Database connection
const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT || 5432,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  ssl: process.env.DB_SSL === 'true' ? { rejectUnauthorized: false } : false
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Add new token
app.post('/tokens/add', async (req, res) => {
  try {
    const tokenData = req.body;
    
    console.log('Received token:', tokenData.name, tokenData.mint);
    
    const query = `
      INSERT INTO tokens (
        mint, name, symbol, signature, trader_public_key,
        initial_buy, sol_amount, market_cap_sol, bonding_curve_key,
        v_tokens_in_bonding_curve, v_sol_in_bonding_curve,
        uri, pool, tx_type, twitter, telegram, website, image,
        created_at
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, NOW())
      ON CONFLICT (mint) DO UPDATE SET
        name = EXCLUDED.name,
        symbol = EXCLUDED.symbol,
        twitter = EXCLUDED.twitter,
        telegram = EXCLUDED.telegram,
        website = EXCLUDED.website,
        image = EXCLUDED.image,
        updated_at = NOW()
      RETURNING id
    `;
    
    const values = [
      tokenData.mint,
      tokenData.name,
      tokenData.symbol,
      tokenData.signature,
      tokenData.traderPublicKey,
      tokenData.initialBuy,
      tokenData.solAmount,
      tokenData.marketCapSol,
      tokenData.bondingCurveKey,
      tokenData.vTokensInBondingCurve,
      tokenData.vSolInBondingCurve,
      tokenData.uri,
      tokenData.pool,
      tokenData.txType,
      tokenData.twitter || null,
      tokenData.telegram || null,
      tokenData.website || null,
      tokenData.image || null
    ];
    
    const result = await pool.query(query, values);
    
    console.log('Token saved:', result.rows[0].id);
    res.json({ ok: true, id: result.rows[0].id });
    
  } catch (error) {
    console.error('Token insert error:', error);
    res.status(500).json({ error: 'internal' });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Token service running on port ${PORT}`);
});
