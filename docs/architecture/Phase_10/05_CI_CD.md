================================================================================
# 05 CI/CD
================================================================================

# CI/CD

## Purpose

Automated CI/CD pipelines ensure every change to Project DNA is tested, built, and published consistently. This document defines the pipeline stages, triggers, and artifact publication.

---

## CI Pipeline (GitHub Actions)

| Trigger | Stages | Artifacts |
|---|---|---|
| Push to any branch | Lint → Type check → Unit test | None |
| PR to develop | Lint → Type check → Unit test → Integration test | Test report |
| Push to develop | Full CI + Build | Docker image (dev tag) |
| Tag `v*` | Full CI + Build + Publish | Docker image (release), npm package, Tauri release |

## CI Stages

```yaml
# .github/workflows/ci.yml (abbreviated)
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ruff check . && eslint . && cargo clippy

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest && vitest run && cargo test

  build:
    needs: [lint, test]
    steps:
      - run: docker build -t project-dna/dna-server .
      - run: npm run build:cli
      - run: npm run tauri build

  publish:
    needs: [build]
    if: startsWith(github.ref, 'refs/tags/v')
    steps:
      - run: docker push project-dna/dna-server:${{ github.ref_name }}
      - run: npm publish
      - uses: softprops/action-gh-release@v1
        with:
          files: src-tauri/target/release/*.{msi,dmg,AppImage}
```

## CD Pipeline

| Event | Action |
|---|---|
| Tag pushed (`v1.2.3`) | Build all artifacts → Publish to npm, Docker Hub, GitHub Releases |
| Weekly schedule | Run AI evaluation benchmark → Publish report |
| Manual trigger | Publish docs site, update changelog |
