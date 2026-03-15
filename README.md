# APEX Trading API

Lightweight API for APEX trading system deployed on Render.

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `/` | API info |
| `/ping` | Health check - keep alive |
| `/health` | Full system health |
| `/state` | Current trading state |
| `/market-regime` | Market regime & VIX |
| `/vix` | India VIX data |
| `/signal` | Trade signal |

## Deployment

1. Connect this repo to Render.com as a Web Service
2. Start command: `gunicorn apex_api:app --bind 0.0.0.0:$PORT`
3. Set up cron-job.org to ping `/ping` every 10 minutes

## Local Development

```bash
pip install -r requirements.txt
python apex_api.py
```

## Environment Variables

- `PORT` - Server port (default: 10000)
- `STATE_FILE` - Path to state.json (default: state.json)