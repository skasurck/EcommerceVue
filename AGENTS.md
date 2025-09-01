# Repository Guidelines

## Project Structure & Module Organization
- Frontend: `frontend/` (Vite + Vue 3 + Pinia + Tailwind). Source in `frontend/src/` with `components/`, `views/`, `stores/`, `router/`, `services/`, and `utils/`.
- Backend: `backend/` (Django + DRF). Project in `backend/tienda/` with apps `productos/`, `carrito/`, `pedidos/`, `usuarios/`. Media in `backend/media/`.
- VCS & docs: root `.git*`, main `README.md`; keep new docs at the repo root.

## Build, Test, and Development Commands
- Frontend dev: from `frontend/` run `npm install`, then `npm run dev` (Vite at `http://localhost:5173`).
- Frontend build: `npm run build` (outputs to `frontend/dist/`), preview with `npm run preview`.
- Lint/format (FE): `npm run lint` (ESLint) and `npm run format` (Prettier on `src/`).
- Backend setup: create venv, then `pip install -r backend/requirements.txt`.
- Backend migrate: from `backend/` run `python manage.py migrate`.
- Backend run: `python manage.py runserver` (CORS allows `localhost:5173`).
- Backend tests: `python manage.py test` (DRF `APITestCase`).

## Coding Style & Naming Conventions
- Vue: 2‑space indent; component files `PascalCase.vue` (e.g., `ProductCard.vue`), composables/stores `camelCase.js`.
- JS/TS: follow ESLint rules in `frontend/eslint.config.js`; format with Prettier (`.prettierrc.json`).
- Python: PEP 8, 4‑space indent; Django models/views/serializers in their respective app folders.
- CSS: Tailwind utility‑first; add project styles in `frontend/src/assets/`.

## Testing Guidelines
- Backend: keep `APITestCase` coverage for new endpoints and critical flows (orders, cart, auth). Place tests in each app’s `tests.py`.
- Frontend: no test runner is configured; if adding tests, propose Vitest + Testing Library in a separate PR.

## Commit & Pull Request Guidelines
- Commits: prefer Conventional Commits (`feat:`, `fix:`, `refactor:`). Example: `feat(pedidos): calcular total con envío`.
- Scope small, messages imperative and descriptive; avoid generic `cambios`.
- PRs: include summary, linked issues, screenshots for UI, and test steps. Note any migrations and data impacts.

## Security & Configuration Tips
- Do not commit secrets. Use environment variables for keys and API bases; keep `DEBUG=False` for production.
- Media/uploads live in `backend/media/`; ignore local files in VCS.
