---
title: Remote GUI
description: Architecture and developer reference for the AnyLog Remote GUI.
layout: page
---
<!--
## Changelog
- 2026-04-17 | Created document
- 2026-04-24 | Added Remote Console SSH plugin section; added macOS Docker networking note
--> 

> **Audience:** This page covers the internal architecture of the Remote GUI and is primarily intended for developers extending or contributing to it. For end-user usage, refer to the GUI itself.

## What is the Remote GUI?

The Remote GUI is a browser-based control panel for working with AnyLog nodes. It supports command execution, monitoring, SQL queries, file management, and bookmarks/presets — with an optional plugin system for additional capabilities.

It is split into two components:
- **React frontend** — the browser UI (`CLI/local-cli-fe-full`)
- **FastAPI backend** — the API server, node access layer, and plugin router (`CLI/local-cli-backend`)

---

## Architecture

```
[ User / Browser ]
       │
       ▼
[ React SPA (Frontend) ]
       │  HTTP requests
       ▼
[ FastAPI Backend ]
       │  AnyLog commands
       ▼
[ AnyLog Node (host:port) ]
```

1. The user interacts with frontend features to send commands or queries
2. Requests are sent from the frontend to the FastAPI backend
3. The backend routes commands to the target AnyLog node
4. The node executes the command and returns output
5. The backend may parse the output before returning it
6. Results are displayed in the frontend

---

## Key terminology

| Term | Description |
|---|---|
| `Remote-GUI` | This product/repo — web UI + API server |
| `Backend` | `CLI/local-cli-backend` — FastAPI app (`main.py`), mounts routers and `/static` |
| `Frontend` | `CLI/local-cli-fe-full` — React/Vite SPA |
| `Feature` | A first-class UI area (client, monitor, sqlquery, bookmarks…) toggled in `feature_config.json` |
| `Plugin` | An optional vertical: a folder under `plugins/` on both backend and frontend with extra routes and a `*Page.js` screen |
| `Connection / node` | A target `host:port` the user selects; the backend runs commands against it |
| `VITE_API_URL` | Base URL for API calls (build-time for Vite; Docker `start.sh` writes `config.js` for runtime) |
| `feature_config.json` | Enables/disables features and plugins; frontend reads `/feature-config` |
| `plugin_order.json` | Optional ordering for sidebar loading |
| `api_router` | The `FastAPI APIRouter` instance each backend plugin must export for auto-loading |

---

## Backend architecture

`main.py` hosts the FastAPI app, CORS configuration, middleware, and core routes (e.g. `send-command`, `monitor`). It also includes routers for core functionality such as `sql_router`.

New features are built as **plugins** in the `plugins/` folder:
- `plugins/loader.py` scans for `plugins/<pluginname>/<pluginname>_router.py`, imports the `api_router`, and respects `plugin_order.json` and `feature_config.json`
- Middleware blocks paths when a feature is disabled
- `helpers.py` and `parsers.py` handle JSON parsing and shared utilities

> **Note:** Always install the `anylog-api` pip package — the Remote GUI is built on top of it.

---

## Frontend architecture

The frontend is a standard React app under `CLI/local-cli-fe-full/src/`:

```
src/
├── assets/        — images, logo
├── components/    — reusable elements and tables
├── pages/         — core pages (corresponding to main.py routes)
├── services/      — API endpoint functions + feature config for plugins
├── styles/        — CSS files
└── plugins/       — frontend equivalents of backend plugins
    └── loader.js  — autodiscovers src/plugins/*/**Page.js
```

`services/featureConfig.js` fetches `/feature-config`, caches it, and uses `isPluginEnabled` to filter plugin routes.

Each plugin's `*Page.js` can export a `pluginMetadata` object (`{ name, icon }`) for sidebar labeling. The route path matches the folder name.

---

## Running locally (development)

You'll need two terminals.

**Terminal 1 — Backend:**

```bash
cd CLI/local-cli-backend/
python -m venv venv && source venv/bin/activate
cd ../..
pip install -r requirements.txt
# Also install the anylog-api pip package
uvicorn CLI.local-cli-backend.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**

```bash
cd CLI/local-cli-fe-full/
npm install
npm start
# If needed, set VITE_API_URL to point at the backend port
```

Alternatively, use `make up` or build with Docker:

```bash
docker build -f Dockerfile . -t anylogco/remote-gui:latest
docker compose -f docker-compose.yaml up -d
```

> **macOS users:** Docker Desktop on Mac only binds forwarded ports to `127.0.0.1` by default. If the frontend cannot reach the backend via your LAN IP, see [macOS Docker port binding](#macos-docker-port-binding) below.

---

## Plugin system

### Creating a new plugin

**Backend** — create `CLI/local-cli-backend/plugins/<name>/<name>_router.py` exporting `api_router`:

```python
from fastapi import APIRouter
api_router = APIRouter(prefix="/<name>", tags=["<name>"])

@api_router.get("/example")
def example():
    return {"status": "ok"}
```

**Frontend** — create `CLI/local-cli-fe-full/src/plugins/<name>/<name>Page.js`:

```js
export const pluginMetadata = { name: 'My Plugin', icon: '🔌' }

export default function MyPluginPage() {
  return <div>My Plugin</div>
}
```

**Register in `feature_config.json`** (both backend and frontend):

```json
{
  "plugins": {
    "<name>": { "enabled": true, "description": "My plugin" }
  }
}
```

**Optional:** Add `<name>` to `plugin_order.json` to control sidebar position.

**API calls in frontend:** Use `window._env_?.VITE_API_URL` (or generated `*_api.js` wrappers) with paths under your router prefix.

After changes: restart the backend; rebuild the frontend if running a production build (dev server hot-reloads automatically).

---

## Remote Console plugin (SSH)

The Remote Console is a built-in plugin that provides live SSH terminal sessions directly in the browser. It is the primary way to interact with AnyLog nodes or their host machines without leaving the GUI.

### What it provides

- **Live SSH terminal** rendered via [xterm.js](https://xtermjs.org/) over a WebSocket connection to the backend
- **Multi-session support** — multiple SSH connections can be open simultaneously, each with its own terminal
- **Encrypted credential vault** — passwords and SSH key files are stored locally using AES encryption (Dexie + dexie-encrypted, unlocked with a master password)
- **Temporary connections** — ad-hoc connections can be added for the current session without persisting to the vault

### How it connects

The frontend opens a WebSocket to `ws://<VITE_API_URL>/sshclient/ws`. On connect it sends a JSON payload:

```json
{
  "action": "direct_ssh",
  "host": "your-server.com",
  "user": "ubuntu",
  "conn_method": {
    "method": "key-string",
    "data": "-----BEGIN OPENSSH PRIVATE KEY-----\n..."
  }
}
```

Supported `action` values: `direct_ssh`, `docker_attach`, `docker_exec`.  
Supported `conn_method.method` values: `password`, `key-string`, `keyfile`.

The backend (FastAPI + Paramiko) authenticates, opens an SSH channel, and streams output back to the terminal in real time. User keystrokes are forwarded from xterm.js → WebSocket → SSH channel.

### Credential vault

The vault is a browser-local encrypted database (Dexie.js + dexie-encrypted). The encryption key is derived from a master password via PBKDF2 (1,000,000 iterations, SHA-256). Credentials are only decrypted into memory after the user unlocks the vault — they are never stored in plaintext. The vault can be accessed from the **Manage Credentials** button in the GUI header.

### Backend plugin files

| Path | Purpose |
|---|---|
| `CLI/local-cli-backend/plugins/sshclient/sshclient_router.py` | FastAPI router, exports `api_router` |
| `CLI/local-cli-fe-full/src/plugins/cli/` | React plugin — `CliPage.js`, `TerminalView.js`, vault components |

---

## macOS Docker port binding

When running via Docker on macOS, the frontend may fail to reach the backend via a LAN IP even though `curl 127.0.0.1:8080` works. This affects both the main GUI and the SSH terminal WebSocket.

**Root cause:** Docker Desktop on Mac runs inside a Linux VM and only forwards ports to the loopback interface by default. `VITE_API_URL` is resolved by the **user's browser**, not the container — so the browser needs a reachable address.

**Fix — both steps are required:**

1\. Add `"ip": "0.0.0.0"` to `~/.docker/daemon.json`:

```json
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false,
  "ip": "0.0.0.0"
}
```

2\. Restart Docker Desktop, then use your Mac's LAN IP (not `127.0.0.1`) in `VITE_API_URL`:

```bash
killall Docker && open /Applications/Docker.app
```

```yaml
environment:
  - VITE_API_URL=http://192.168.x.x:8080   # find with: ipconfig getifaddr en0
```

> This is macOS-only. Linux and Windows Docker bind to all interfaces by default.

---

## Long-term roadmap

- Mobile application support
- Dashboard integration (Grafana or in-app)
- Full plugin modularization — every feature becomes a plugin; the base Remote GUI becomes a minimal image with a downloadable plugin catalog