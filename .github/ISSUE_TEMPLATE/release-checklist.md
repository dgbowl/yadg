---
name: Release Checklist
about: Release checklist for minor and major dgpost releases.
title: Release checklist for `yadg-vX.Y`
labels: ''
assignees: ''

---

## Release checklist

### Preparing a release candidate:
- [ ] tests pass on `main` branch
- [ ] `dgbowl-schemas` released and updated in `pyproject.toml`
- [ ] `__latest_dataschema__` in `src/yadg/dgutils/schemautils.py` updated
- [ ] `docs/source/version.rst` updated to include new version file
- [ ] `docs/source/version.vX.Y.rst` created

### Preparing a full release
- [ ] `docs/source/version.vX.Y.rst` release date updated
- [ ] a tagged release candidate passes `integration-test`

### After release
- [ ] pypi packages built and uploaded
- [ ] docs built and deployed
