# docker

Owner: Adrian

WordPress in a single container, connected to the separate MariaDB VM.

Planned contents:

- Docker or compose configuration with a pinned image tag.
- `.env.example` with placeholder database settings. The real `.env` is ignored by Git.
- Explicit CPU and memory limits, matching the agreed resource budget.
- PHP, web server, worker, and caching settings matched to the native deployment, with any differences listed.
- Instructions for starting, stopping, and checking the deployment.
- Steps for switching between native and Docker.

Do not run a second database inside this deployment.
