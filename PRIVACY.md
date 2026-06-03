# Privacy

`markdown-link-auditor` is designed to run locally and read Markdown files from the path you provide.

It does not:

- Send telemetry.
- Upload documents.
- Call remote APIs.
- Check external links online.
- Store a database.
- Modify Markdown files.

Reports may include file paths, line numbers, rule names, summaries, and link targets. Use `--no-values` to hide raw link targets in generated reports. Local absolute paths and local file URLs are redacted in normal report output, but this is a narrow reporting safeguard and not a full secret detection system.
