# Roadmap

## 0.1.x

- Stabilize the first CLI surface.
- Keep all runtime behavior local, read-only, and dependency-light.
- Expand tests for Markdown edge cases.
- Improve CI ergonomics without making reports noisy by default.

## Later Ideas

- Optional configuration for include and exclude paths.
- More complete CommonMark compatibility, if it can stay small and predictable.
- Optional external link checking behind an explicit flag such as `--check-external`, with timeout, cache, retry, and domain allowlist controls. The default should remain no-network.
- GitHub and GitLab anchor slug modes, with fixtures for CJK text, emoji, punctuation, and duplicate headings.
- SARIF, JUnit XML, or GitHub annotation output for CI systems.
- Better handling for generated documentation folders.

These are possibilities, not promises. The project should remain a local Markdown auditor rather than a crawler, web monitor, or documentation site generator.
