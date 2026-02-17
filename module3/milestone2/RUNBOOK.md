# Operations Runbook — ML Sentiment Inference Service

This document provides a comprehensive guide to building, deploying, and maintaining the containerized sentiment-analysis service.

---

## 1. Dependency Pinning Strategy

All Python dependencies are pinned to exact versions in `app/requirements.txt`:

```
flask==3.0.3
gunicorn==22.0.0
```

**Why pin?** Pinning prevents unexpected breakage when upstream packages release new versions. Every `pip install` resolves to the same package set, guaranteeing reproducible builds across developer machines, CI runners, and production containers.

**How to update dependencies:**

```bash
# 1. Create a virtualenv
python -m venv .venv && source .venv/bin/activate

# 2. Install current pins
pip install -r app/requirements.txt

# 3. Upgrade a specific package
pip install --upgrade flask

# 4. Freeze the new state
pip freeze | grep -i flask  # verify version
# Update app/requirements.txt with the new pin

# 5. Run tests to validate
pytest tests/ -v
```

Always update one dependency at a time and run the full test suite before committing.

---

## 2. Image Optimization

### Multi-Stage Build

The Dockerfile uses a two-stage build to keep the runtime image lean:

| Stage    | Purpose                                  | Includes                         |
|----------|------------------------------------------|----------------------------------|
| `builder`| Install and compile Python packages      | pip, wheel, build tools, caches  |
| `runtime`| Serve the application                    | Python runtime + installed libs  |

Only the installed packages (`/root/.local`) are copied from the builder into the runtime stage. Build caches, compilers, and header files are discarded.

### Size Metrics

| Metric                               | Value      |
|---------------------------------------|------------|
| Base image (`python:3.11-slim`)       | ~150 MB    |
| **Single-stage build (unoptimized)**  | **~420 MB**|
| **Multi-stage build (optimized)**     | **~180 MB**|
| Size reduction                        | ~57%       |

### Techniques Used

- **Multi-stage build** — eliminates build-time-only files from the final image.
- **`--no-cache-dir`** — prevents pip from storing wheel/download caches in the image.
- **`.dockerignore`** — excludes tests, docs, `.git`, and other non-essential files from the build context.
- **Layer ordering** — dependency installation runs before code copy so that layers are cached when only application code changes.
- **Slim base image** — `python:3.11-slim` instead of the full `python:3.11` image (saves ~600 MB).

---

## 3. Security Considerations

### Non-Root Execution

The Dockerfile creates a dedicated `appuser` with no login shell and switches to it before the `CMD` directive. This limits the blast radius of any container escape.

### Minimal Attack Surface

- The runtime stage contains only the Python interpreter and the two application dependencies (Flask, Gunicorn). No compilers, package managers (beyond pip), or development headers are present.
- `.dockerignore` ensures secrets, tests, and Git history are never baked into the image.

### Secrets Management

- No credentials are committed to the repository.
- Registry authentication uses `secrets.GITHUB_TOKEN`, a short-lived token scoped to the workflow run.
- Environment-specific secrets (API keys, DB passwords) should be injected at runtime via environment variables or a secrets manager — never hardcoded.

### Vulnerability Scanning (Recommended)

Integrate Trivy into the CI pipeline for automated CVE scanning:

```bash
# Local scan
trivy image ghcr.io/tcyuen2/ids568-mlops-milestone2/ml-service:v1.0.0
```

---

## 4. CI/CD Workflow — Step-by-Step

The pipeline is defined in `.github/workflows/build.yml` and runs on every push to `main` or when a version tag (`v*.*.*`) is created.

### Job 1: `test`

1. **Checkout** — clones the repository at the triggering commit.
2. **Setup Python 3.11** — installs the correct interpreter on the runner.
3. **Install dependencies** — installs application requirements plus `pytest`.
4. **Run pytest** — executes `tests/test_app.py`. If any test fails the job exits with a non-zero code and the pipeline stops.

### Job 2: `build` (depends on `test`)

1. **Checkout** — clones the repo again on a fresh runner.
2. **Set up Docker Buildx** — enables advanced build features and layer caching.
3. **Authenticate** — logs in to GitHub Container Registry (GHCR) using `secrets.GITHUB_TOKEN`.
4. **Extract metadata** — computes image tags from the Git ref:
   - Semantic version tags (`v1.0.0`, `v1.0`)
   - Short SHA for traceability
   - `latest` on the default branch
5. **Build & push** — builds the multi-stage Dockerfile, tags the resulting image, and pushes it to GHCR.

**Key safety net:** the `needs: test` directive ensures images are never pushed unless every test passes.

### Pipeline Trigger Summary

| Event                    | `test` runs? | `build` runs? |
|--------------------------|:------------:|:-------------:|
| Push to `main`           | Yes          | Yes           |
| Push tag `v1.2.3`        | Yes          | Yes           |
| Pull request to `main`   | Yes          | No            |

---

## 5. Versioning Strategy

This project follows [Semantic Versioning 2.0.0](https://semver.org/):

```
v MAJOR . MINOR . PATCH
  |        |        └── Bug fixes, documentation updates
  |        └─────────── New features, backward-compatible
  └──────────────────── Breaking API changes
```

### Examples

| Change                                | Version bump         |
|---------------------------------------|----------------------|
| Fix a typo in an error message        | `v1.0.0` → `v1.0.1` |
| Add a new `/batch-predict` endpoint   | `v1.0.1` → `v1.1.0` |
| Change the response JSON schema       | `v1.1.0` → `v2.0.0` |

### Creating a Release

```bash
# Tag the commit
git tag v1.0.0

# Push the tag (triggers CI/CD build + publish)
git push --tags
```

The CI pipeline automatically derives image tags from the Git tag, so `v1.0.0` produces images tagged `v1.0.0`, `v1.0`, and `latest`.

---

## 6. Troubleshooting

### Image push fails with "authentication required"

**Cause:** GitHub token is missing or the workflow lacks `packages: write` permission.

**Fix:**

1. Confirm the `build` job includes:
   ```yaml
   permissions:
     contents: read
     packages: write
   ```
2. Ensure `secrets.GITHUB_TOKEN` is referenced (not a personal token).
3. For an external registry, verify that the corresponding secret is set under **Settings → Secrets and variables → Actions**.

### Tests pass locally but fail in CI

**Cause:** Environment differences — OS libraries, Python version, or file paths.

**Fix:**

- Lock the Python version in the workflow (`python-version: "3.11"`).
- Avoid absolute paths in tests; use `os.path` relative to `__file__`.
- Run `pytest` locally inside a clean virtualenv to simulate CI.

### Docker build fails on dependency installation

**Cause:** Network issues or incompatible package versions.

**Fix:**

```bash
# Verify the requirements file resolves locally
pip install --dry-run -r app/requirements.txt
```

If a package requires system libraries (e.g., `libpq-dev`), add an `apt-get install` step in the builder stage only.

### Image size is too large (> 500 MB)

**Cause:** Build artifacts or dev dependencies leaking into the runtime stage.

**Fix:**

- Confirm the runtime `FROM` line does not reference the builder.
- Add `--no-cache-dir` to every `pip install`.
- Use `docker history <image>` to identify the largest layers.
- Ensure `.dockerignore` excludes unnecessary files.

### Container crashes on startup

**Cause:** Incorrect `CMD`, missing module, or port conflict.

**Fix:**

```bash
# Check logs
docker logs <container_id>

# Run interactively to debug
docker run -it --entrypoint /bin/bash ghcr.io/tcyuen2/ids568-mlops-milestone2/ml-service:v1.0.0
```

### Health check fails

**Cause:** The app hasn't started yet or is listening on the wrong port.

**Fix:**

- Verify the `PORT` environment variable matches the exposed port.
- Increase `start_period` in the Docker Compose health check.
- Confirm Gunicorn workers are binding to `0.0.0.0`, not `127.0.0.1`.
