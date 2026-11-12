# Bookshop demo (Docker, Compose and images in CI)

Two services (`catalog`, `orders`), SQL Server and a static UI, as in Assignment 2. Used live in the Docker session.

```bash
cp .env.example .env          # change the passwords
docker compose up --build     # first start takes about 30 s: SQL Server must be healthy before db-init runs
```

- UI: http://localhost:8080 · catalog: http://localhost:8001/products · orders: http://localhost:8002/orders
- Partial failure: `docker compose stop catalog`, then order a product: orders answers 503 with a clear message and `/health` stays 200.
- Reset the data: `docker compose down -v`.
- CI: `.github/workflows/ci.yml` tests each service and builds each image on every push and pull request. On `main` it runs inside the CD workflow and pushes the images to `ghcr.io/<owner>/bookshop-<service>:<sha>`.
- UI: `ui/config.js` holds the services' addresses (localhost, or the Codespace's ports). On Azure the CD workflow overwrites it.

## On Azure

`.github/workflows/cd.yml` runs on every push to `main`. It runs CI, then:

1. points each Container App at the images of this commit;
2. writes `ui/config.js` with the services' Azure addresses;
3. uploads `ui/` to the storage static website;
4. waits for `/health` on both services to return 200.

The deploy job is skipped until the repository has the Azure variables (`PREFIX`, `RESOURCE_GROUP`, `UI_STORAGE`).

The one-time setup is in the guide "Assignment 2: deploying to your own Azure subscription" on Blackboard, steps 3–7. For this demo, use `SVC_A=catalog`, `SVC_B=orders`, port 8000 for both, and `CATALOG_URL` on `orders`. After the first push to `main`, make the two `bookshop-*` packages public. The images are built with `provenance: false`, because Container Apps can't pull a tag that points to an attestation index.

## In GitHub Codespaces (no local Docker)

1. Push this folder to a repository of yours, then *Code → Codespaces → Create codespace* (4 cores, 8 GB: SQL Server needs the memory). `.devcontainer/` installs Docker and creates `.env`.
2. In the terminal: `docker compose up --build`. The SQL Server image is amd64, which is what Codespaces runs, so no emulation is needed.
3. Check that `.env` has a `UI_ORIGIN=` line (`grep UI_ORIGIN .env`). If not (for example after a failed build left a recovery container), run `bash .devcontainer/setup.sh`, then `docker compose up -d` so the services pick it up. Without it the services reject the UI's requests (CORS) and the lists stay empty.
4. Open the **Ports** tab. Port 8080 is the UI. If you open it in a browser tab, set ports **8001** and **8002** to *Public* (the UI calls them from your browser and private ports require a login cookie): right-click the port → *Port Visibility* → *Public*. (`gh codespace ports visibility 8001:public 8002:public -c <codespace>` does the same, but only from your own computer's terminal: inside the codespace `gh` lacks the permission.) With VS Code desktop connected to the codespace the ports appear on `localhost` and nothing needs changing.
5. Stop the codespace when you finish: it bills core-hours while running (4 cores for 1 hour = 4 core-hours).
