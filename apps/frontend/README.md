# Frontend

React/Vite interface for drawing and editing LuminariMUD wilderness regions, paths, landmarks, descriptions, and hints.

## Responsibilities

- `src/hooks/useEditor.ts` owns editor and draft state.
- `src/services/api.ts` owns backend wire-format conversion.
- `src/services/chatAPI.ts` and `chatBridge.ts` integrate staged chat actions.
- `@wildeditor/shared` supplies reusable domain types.
- Supabase supplies browser authentication; the wilderness data source is the backend API.

## Run locally

From the repository root:

```bash
nvm use
npm ci
cp apps/frontend/.env.development.example apps/frontend/.env.local
npm run dev
```

The dev server is `http://localhost:5173`. Set `VITE_API_URL=http://localhost:8000/api`. For a local development bypass, set `VITE_DISABLE_AUTH=true`; deployed builds must use authentication.

## Checks

```bash
npm run lint
npm run type-check
npm run build
```

No functional frontend test runner is configured. The workspace `test` script is a placeholder.

## Security status

`VITE_` variables are public. The current mutation flow still reads `VITE_WILDEDITOR_API_KEY`, which is unsuitable as a production secret. See [Configuration](../../docs/configuration.md) and the [active authentication migration plan](../../docs/ongoing-projects/self-hosted-postgres-auth-migration-plan.md).

## Further reading

- [Development setup](../../docs/development.md)
- [User guide](../../docs/user-guide.md)
- [Architecture](../../docs/architecture.md)
