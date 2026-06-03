# Anchor Slugs

Heading anchors are generated with approximate GitHub-style behavior:

- Trim heading text.
- Remove simple Markdown formatting.
- Lowercase text.
- Remove punctuation.
- Replace whitespace with hyphens.
- Add numeric suffixes for duplicate generated anchors.

This behavior is useful for common README and docs links, but it is not a guarantee of exact GitHub renderer compatibility.

## Duplicate Headings

Duplicate headings are reported as warnings because generated anchor suffixes can surprise readers and reviewers. A link to the suffixed anchor can still pass if it matches the generated value.
