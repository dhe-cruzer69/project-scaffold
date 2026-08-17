require('dotenv').config();

const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8000;
const APP_NAME = process.env.APP_NAME || 'X4-ARX369 Omega';
const DEBUG = process.env.DEBUG === 'true';
const X4_HEALTH_URL = process.env.X4_HEALTH_URL || 'http://127.0.0.1:8080/health';

app.use(helmet());
const allowedOrigins = (process.env.CORS_ORIGINS || '').split(',').map((o) => o.trim()).filter(Boolean);
app.use(cors({ origin: allowedOrigins.length ? allowedOrigins : false }));
app.use(rateLimit({
  windowMs: 60 * 1000,
  max: 60,
  standardHeaders: true,
  legacyHeaders: false,
}));
app.use(express.static(path.join(__dirname, 'public')));

app.get('/api/config', (req, res) => {
  res.json({
    appName: APP_NAME,
    debug: DEBUG,
    apiKeyConfigured: Boolean(process.env.API_KEY && process.env.API_KEY !== 'replace-me'),
  });
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'green', service: APP_NAME, timestamp: new Date().toISOString() });
});

app.get('/api/x4/status', async (req, res) => {
  try {
    const response = await fetch(X4_HEALTH_URL, { signal: AbortSignal.timeout(1200) });
    const body = await response.json().catch(() => ({}));
    res.status(200).json({
      status: response.ok ? 'green' : 'red',
      reachable: response.ok,
      url: X4_HEALTH_URL,
      upstream: body,
    });
  } catch (error) {
    res.status(200).json({
      status: 'amber',
      reachable: false,
      url: X4_HEALTH_URL,
      reason: error instanceof Error ? error.message : 'unreachable',
    });
  }
});

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

if (DEBUG) console.log(`[${APP_NAME}] Running in DEBUG mode`);
app.listen(PORT, () => console.log(`${APP_NAME} is running on http://localhost:${PORT}`));
