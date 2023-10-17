from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import defaultdict
from collections.abc import Iterator
from collections.abc import Sequence
from typing import NamedTuple


ERROR_LINE_RE = re.compile(r'^.*?@\d+:\d+ ')


class Violation(NamedTuple):
    filename: str
    rule_name: str
    lineno: int


def _parse_output_line(line: str) -> Violation | None:
    if not ERROR_LINE_RE.match(line):
        return None

    location, violated_rule_name, *__ = line.split(maxsplit=2)
    filename, position = location.split('@', maxsplit=1)
    lineno, *__ = position.split(':', maxsplit=1)

    rule_name_ = violated_rule_name.removesuffix(':')
    return Violation(filename, rule_name_, int(lineno))


def _find_violations(
        rule_name: str, filenames: Sequence[str],
) -> dict[str, list[Violation]]:
    proc = subprocess.run(
        (
            sys.executable, '-mfixit',
            '--rules', rule_name,
            'lint', *filenames,
        ),
        capture_output=True,
        text=True,
    )

    # extract filenames and line numbers
    results: dict[str, list[Violation]] = defaultdict(list)
    for line in proc.stdout.splitlines():
        violation = _parse_output_line(line)
        if violation:
            results[violation.filename].append(violation)
        else:  # pragma: no cover
            pass

    return results


def _add_comments(
        lines: Sequence[str],
        linenos_to_silence: set[int], rule_name: str,
) -> Iterator[str]:
    for current_lineno, line in enumerate(lines, start=1):
        if current_lineno in linenos_to_silence:
            leading_ws = line.removesuffix(line.lstrip())
            yield f'{leading_ws}# lint-fixme: {rule_name}\n'
        yield line


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('rule_name')
    parser.add_argument('filenames', nargs='*')
    args = parser.parse_args(argv)

    print('-> running fixit', file=sys.stderr)
    violations = _find_violations(args.rule_name, args.filenames)

    if not violations:
        print('no violations found', file=sys.stderr)
        return 0

    print(f'found violations in {len(violations)} files', file=sys.stderr)

    violation_names = {
        violation.rule_name
        for file_violations in violations.values()
        for violation in file_violations
    }
    if len(violation_names) != 1:
        print(
            'ERROR: errors found for multiple rules:',
            sorted(violation_names),
            file=sys.stderr,
        )
        return 1

    [violation_name] = violation_names

    print('-> adding fixme comments', file=sys.stderr)
    ret = 0
    for filename, file_violations in violations.items():
        print(filename, file=sys.stderr)
        with open(filename) as f:
            src = f.read()

        lines = src.splitlines(keepends=True)
        src_with_comments = ''.join(
            _add_comments(
                lines, {v.lineno for v in file_violations}, violation_name,
            ),
        )

        with open(filename, 'w') as f:
            f.write(src_with_comments)

        ret |= src_with_comments != src

    return ret


if __name__ == '__main__':
    raise SystemExit(main())
