# Release Checklist

- Run `python -m pytest`.
- Run `python -m markdown_link_auditor.cli check .`.
- Run `python -m markdown_link_auditor.cli check examples/good-docs`.
- Confirm `python -m markdown_link_auditor.cli check examples/bad-docs` exits with code 1.
- Confirm `--output` does not overwrite an existing report unless `--force` is used.
- Review README and docs for conservative wording.
- Check that generated files are ignored.
- Check that no real private values are included in examples or tests.
- Update [CHANGELOG](../CHANGELOG.md).
