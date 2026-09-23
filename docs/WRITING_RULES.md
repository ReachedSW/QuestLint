# Writing rules

Rules implement the `Rule` protocol in `questlint.rules.base`: stable
`rule_id`, `name`, `description`, `severity`, and `check(context)` returning a
list of `Diagnostic` instances. Add the rule to `RuleRegistry` so selection and
SARIF metadata include it.

`RuleContext` provides the source path, parser model, lexical scope facts,
settings, and state graph. Reuse those shared passes where possible; do not
execute Lua or parse source independently in a rule. Add deterministic tests
for rule IDs, locations, messages, selection, and suppression behavior.
