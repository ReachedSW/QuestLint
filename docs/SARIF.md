# SARIF

`questlint scripts --format sarif > questlint.sarif` writes SARIF 2.1.0.
The report contains QuestLint's version, metadata for all built-in rules, and
each diagnostic's rule ID, severity, message, URI, line, and column.

For GitHub Code Scanning, upload the generated file with
`github/codeql-action/upload-sarif@v3`. This repository provides an example;
GitHub integration itself is not exercised by local tests.
