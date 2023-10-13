# silence-fixit-error

Add `lint-fixme` comments to every occurrence of a `fixit` error.

## Usage

Install with pip:

```shell
python -m pip install silence-fixit-error
```

Call the tool with a rule you want to add `fixme` comments for and the paths to
the files:

```shell
silence-fixit-error fixit.rules:CollapseIsinstanceChecks path/to/files/ path/to/more/files/
```

Once an auto-fix is available for this rule, we can remove the `fixme` comments
and run that auto-fix:

```shell
fix-silenced-fixit-error fixit.rules:CollapseIsinstanceChecks path/to/files/ path/to/more/files/
```

## Rationale

When adding a new rule (or enabling more rules) in `fixit` on a large code-base,
fixing the existing violations can be too large a task to do quickly. However,
starting to check the rule sooner will prevent new violations from being
introduced.

Ignoring existing violations is a quick way to allow new rules to be enabled.
You can then burn down the existing violations over time.

This tool makes it easy to find and ignore all current violations of a rule so
that it can be enabled.
