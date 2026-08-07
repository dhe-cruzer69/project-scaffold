async function loadConfig() {
  try {
    const res = await fetch('/api/config');
    const config = await res.json();

    document.getElementById('app-name').textContent = config.appName;
    document.getElementById('debug-mode').textContent = config.debug ? 'On' : 'Off';
    document.getElementById('api-key').textContent = config.apiKeyConfigured ? 'Yes' : 'No';
  } catch (err) {
    console.error('Failed to load config:', err);
  }
}

loadConfig();
