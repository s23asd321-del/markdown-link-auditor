# Rules

| Rule | Severity | Description |
| --- | --- | --- |
| `missing-file` | error | A local Markdown link points to a missing file. |
| `missing-image` | error | A Markdown image points to a missing file. |
| `missing-anchor` | error | A same-file or cross-file Markdown anchor does not match a target heading. |
| `empty-link` | error | A Markdown link target is empty. |
| `undefined-reference` | error | A reference-style link has no matching definition. |
| `duplicate-heading` | warning | A heading may produce the same base anchor as an earlier heading. |
| `local-absolute-path` | warning | A local absolute path appears in Markdown content or a link target. |
| `local-file-url` | warning | A local file URL appears in Markdown content or a link target. |
| `todo-link` | warning | A link target looks like a TODO, FIXME, TBD, or placeholder value. |
| `unsupported-scheme` | warning | A Markdown link uses a scheme that the tool does not check. |
| `file-too-large` | warning | A Markdown file was skipped because it exceeded the configured size limit. |
| `unchecked-anchor` | warning | A fragment target is not a Markdown file, so the anchor was not checked. |

External links are skipped by default. The tool does not check whether remote pages are online.

Warnings can fail CI by using `--strict` or `--fail-on warning`.
