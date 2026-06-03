# Security Policy

`markdown-link-auditor` is a documentation quality tool. It is not a security scanner, secret scanner, malware scanner, privacy compliance product, or access-control tool.

## Reporting Issues

For a suspected vulnerability in the tool itself, open a private report through the repository's security advisory feature if available. If that is not available, open a minimal public issue that describes the affected behavior without including private documents or sensitive values.

## Scope

In scope:

- Bugs that cause the CLI to read files outside the requested local path unexpectedly.
- Bugs that expose redacted values in reports when `--no-values` or redaction should hide them.
- Crashes caused by ordinary Markdown input.

Out of scope:

- Requests to check whether external links are online.
- Requests to scan for all secrets.
- Claims that a document is secure, compliant, or safe to publish.
- Issues caused by running the tool on untrusted files in a hostile environment.
