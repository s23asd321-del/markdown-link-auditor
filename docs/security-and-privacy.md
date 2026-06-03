# Security and Privacy

`markdown-link-auditor` does not access the network, call remote APIs, upload documents, collect telemetry, or modify Markdown files.

The tool may report local file paths and link targets. For public logs, use `--no-values`. Local absolute paths and local file URLs are redacted in normal reports.

This redaction is narrow. It is not secret scanning and should not be relied on to find every sensitive value.

See [Security Policy](../SECURITY.md), [Privacy](../PRIVACY.md), and [Disclaimer](../DISCLAIMER.md).
