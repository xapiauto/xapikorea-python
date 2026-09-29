# Releasing xapikorea

Releases are built and published by `.github/workflows/release.yml`. The
workflow uses PyPI Trusted Publishing, so no API token is stored in GitHub.

## One-time setup

Create the `testpypi` and `pypi` environments in the GitHub repository. Then
configure a Trusted Publisher on both TestPyPI and PyPI with these values:

- PyPI project name: `xapikorea`
- GitHub owner: `xapiauto`
- GitHub repository: `xapikorea-python`
- Workflow filename: `release.yml`
- Environment: `testpypi` on TestPyPI and `pypi` on PyPI

For the first PyPI release, configure a pending Trusted Publisher if the
project does not exist yet.

## Publish a release

1. Set the new version in `src/xapikorea/_version.py`.
2. Run the local checks:

   ```bash
   python -m pytest
   python -m build
   python -m twine check dist/*
   ```

3. Commit and push the release changes.
4. Run the `Release` workflow manually to publish to TestPyPI.
5. Create a GitHub Release with a tag matching the package version, such as
   `v0.1.0`. Publishing that GitHub Release publishes the same artifacts to
   PyPI.

PyPI does not allow a published filename to be reused. Increase the version
before retrying a release that already reached the package index.
