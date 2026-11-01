# HR Assistant - Web

A Vite + React chat UI for asking HR policy questions, structured like ChatGPT (conversation history, bottom-anchored composer) but with its own palette and type. Design decisions are documented in the root [DESIGN.md](../../DESIGN.md) and [.impeccable/surfaces/apps-web-src-app-jsx.md](../../.impeccable/surfaces/apps-web-src-app-jsx.md).

## Run locally

Requires Node.js and npm.

```bash
npm install
npm run dev
```

Runs at `http://localhost:5173`. Requires [apps/api](../api) to be running on `http://localhost:8000` - the app calls its `/ask` endpoint directly, and the API's CORS config only allows `http://localhost:5173` as an origin.

To run both apps together with one command, use the root-level `npm run dev` instead (see the [repo root README](../../README.md)).

## Build

```bash
npm run build
```

Outputs to `dist/`.
