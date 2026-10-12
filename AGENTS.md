# Ramos application repository

- Keep runtime application code in Ramos. Python is setup/test tooling only.
- Target the version and source commit in `upstream.json`.
- Treat `stdlib/` as a pinned upstream snapshot; review before updating it.
- Preserve checked arithmetic, UTF-8 strings and fallible I/O contracts.
- Keep examples simple and portable to Linux x64 and Windows x64.
- Label proposed capabilities and historical measurements accurately.
- Run `python tools/check.py` before publishing changes.
- Follow the hub at https://github.com/zackmsa777-a11y/ramos/blob/main/docs/ecosystem.md.
