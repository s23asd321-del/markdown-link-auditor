# Overview

`markdown-link-auditor` checks local Markdown files for common link and anchor problems before documentation is published.

It is useful for:

- README checks before publishing a repository.
- Documentation folder checks in CI.
- Local validation of image paths and relative links.
- Finding local absolute paths that are not suitable for public docs.

The first version is intentionally small and local. It does not fetch URLs, crawl sites, call GitHub, or modify Markdown files.

## Related Docs

- [Design](design.md)
- [Rules](rules.md)
- [Anchor slugs](anchor-slugs.md)
- [Report format](report-format.md)
- [Security and privacy](security-and-privacy.md)
- [Release checklist](release-checklist.md)
