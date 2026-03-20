# Releasing Skilgen

## Local Release Checklist

1. Update version strings if needed:
   - `python3 scripts/bump_version.py 0.1.1`
2. Run the full test suite:
   - `python3 -m unittest discover -s tests`
3. Build distributions:
   - `python3 -m pip install .[dev]`
   - `python3 -m build`
4. Validate package metadata:
   - `python3 -m twine check dist/*`
5. Create and push a release tag:
   - `git tag v0.1.0`
   - `git push origin v0.1.0`

## GitHub Automation

- `.github/workflows/ci.yml` runs tests and packaging checks on pushes and pull requests.
- `.github/workflows/release.yml` builds and publishes to PyPI when a `v*` tag is pushed.

## Notes

- The public package remains `skilgen`.
- Maintainer-only automation stays under `maintainers/` and is not part of the installable surface.
