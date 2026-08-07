require('dotenv').config();

const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8000;
const APP_NAME = process.env.APP_NAME || 'project-scaffold';
const DEBUG = process.env.DEBUG === 'true';

// Security headers (CSP, X-Frame-Options, X-Content-Type-Options, etc.)
app.use(helmet());

// CORS: allow-list of origins. Defaults to same-origin only (no CORS headers).
const allowedOrigins = (process.env.CORS_ORIGINS || '').split(',').map((o) => o.trim()).filter(Boolean);
app.use(
  cors({
    origin: allowedOrigins.length ? allowedOrigins : false,
  })
);

// Rate limiting for API endpoints (brute-force / DoS protection)
const apiLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 60, // limit each IP to 60 requests per window
  standardHeaders: true,
  legacyHeaders: false,
});
app.use('/api', apiLimiter);

// Serve static files from the public directory
app.use(express.static(path.join(__dirname, 'public')));

// Simple API endpoint demonstrating usage of configured values
app.get('/api/config', (req, res) => {
  res.json({
    appName: APP_NAME,
    debug: DEBUG,
    // NOTE: never expose the real API key publicly in production
    apiKeyConfigured: Boolean(process.env.API_KEY && process.env.API_KEY !== 'replace-me')
  });
});

// Fallback to the main page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

if (DEBUG) {
  console.log(`[${APP_NAME}] Running in DEBUG mode`);
}

app.listen(PORT, () => {
  console.log(`${APP_NAME} is running on http://localhost:${PORT}`);
});
