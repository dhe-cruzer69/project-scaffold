# Project Scaffold

A minimal Node.js/Express project scaffold generated from the `.env.example` configuration.

## Getting Started

1. Install dependencies:

   ```bash
   npm install
   ```

2. Configure your environment:

   ```bash
   cp .env.example .env
   ```

   Then edit `.env` and replace the placeholder values.

3. Start the server:

   ```bash
   npm start
   ```

4. Open `http://localhost:8000` in your browser.

## Configuration

| Variable       | Description                                        | Default            |
|----------------|----------------------------------------------------|--------------------|
| APP_NAME       | The name of the application                        | `project-scaffold` |
| DEBUG          | Enable debug mode (`true`/`false`)                 | `true`             |
| PORT           | The port the server listens on                     | `8000`             |
| API_KEY        | Your API key                                       | `replace-me`       |
| CORS_ORIGINS   | Comma-separated allow-list of origins for CORS.    | *(empty = same-origin)* |
|                | Leave empty to disable cross-origin requests.      |                    |

## Project Structure

```text
project-scaffold/
├── .env.example       # Template environment file
├── .env               # Actual environment config (git-ignored)
├── package.json       # Dependencies and scripts
├── server.js          # Express server entry point
├── public/            # Static frontend assets
│   ├── index.html
│   ├── style.css
│   └── app.js
└── README.md
```

## ARIEX AI Service Layer

The project also includes an AriexCore model-fleet engine under `src/arx/ai/` — five
specialized expert profiles (Meaw, Fab, Ops, Sony, Helex) with an auto-router and
model cascading. Run the self-tests with:

```bash
# from the project root, with src/ on the Python path
$env:PYTHONPATH="src"; python test_fleet.py
$env:PYTHONPATH="src"; python test_ai.py
```

## License

MIT

## Deploy to Azure

This project includes Azure Developer CLI (azd) configuration to deploy to Azure App Service.

### Prerequisites

- [Azure Developer CLI (azd)](https://aka.ms/install-azd)
- [Azure CLI (az)](https://aka.ms/install-azure-cli)
- An Azure subscription

### Deploy

```bash
# Set your default Azure subscription
azd config show

# Provision resources and deploy the app
azd up
```

The deployment provisions:
- **Azure App Service** (Linux, Node 20) running the Express app
- **App Service Plan** (B1/S1 tier)
- **Application Insights** for monitoring
- **Log Analytics Workspace** for telemetry storage

The app uses a **system-assigned managed identity** for authentication — no credentials or keys are stored in connection strings.

### Clean up

```bash
azd down
