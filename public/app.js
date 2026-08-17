async function json(url) {
  const response = await fetch(url, { cache: 'no-store' });
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
  return response.json();
}

function setDot(id, state) {
  const dot = document.getElementById(id);
  dot.classList.remove('green', 'red');
  if (state === 'green') dot.classList.add('green');
  if (state === 'red') dot.classList.add('red');
}

async function refresh() {
  const now = new Date();
  document.getElementById('timestamp').textContent = `Last checked ${now.toLocaleTimeString()}`;

  try {
    const app = await json('/api/health');
    setDot('app-dot', app.status === 'green' ? 'green' : 'red');
    document.getElementById('app-status').textContent = app.status === 'green' ? 'Healthy' : 'Degraded';
  } catch (error) {
    setDot('app-dot', 'red');
    document.getElementById('app-status').textContent = 'Unavailable';
  }

  try {
    const x4 = await json('/api/x4/status');
    const state = x4.status === 'green' ? 'green' : x4.status === 'amber' ? 'amber' : 'red';
    setDot('x4-dot', state);
    document.getElementById('x4-status').textContent = x4.reachable ? 'Reachable' : 'Standby';
  } catch (error) {
    setDot('x4-dot', 'red');
    document.getElementById('x4-status').textContent = 'Unavailable';
  }

  const appGreen = document.getElementById('app-status').textContent === 'Healthy';
  const x4Ready = document.getElementById('x4-status').textContent === 'Reachable';
  const overall = document.getElementById('overall');
  overall.textContent = appGreen && x4Ready ? 'ALL SYSTEMS GREEN' : 'CORE READY / RUNTIME CHECK';
}

refresh();
setInterval(refresh, 10000);
