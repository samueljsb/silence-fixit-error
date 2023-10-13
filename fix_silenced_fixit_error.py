from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from collections.abc import Iterator
from collections.abc import Sequence

logging.basicConfig(level=logging.DEBUG)


def _remove_comments(
        lines: Sequence[str],
        rule_name: str,
) -> Iterator[str]:
    __, rule_id = rule_name.rsplit(':', maxsplit=1)
    fixme_comment = f'# lint-fixme: {rule_id}'
    for line in lines:
        if line.strip() == fixme_comment:  # fixme comment only
            continue
        elif line.rstrip().endswith(fixme_comment):  # code then fixme comment
            trailing_ws = line.removeprefix(line.rstrip())
            line_without_comment = (
                line.rstrip().removesuffix(fixme_comment)  # remove comment
                .rstrip()  # and remove any intermediate ws
            )
            yield line_without_comment + trailing_ws
        else:
            yield line


def _run_fixit_fix(
        rule_name: str, filenames: Sequence[str],
) -> tuple[int, str]:
    proc = subprocess.run(
        (
            sys.executable, '-mfixit',
            '--rules', rule_name,
            'fix', '--automatic', *filenames,
        ),
        capture_output=True, text=True,
    )
    return proc.returncode, proc.stderr.strip()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('rule_name')
    parser.add_argument('filenames', nargs='*')
    args = parser.parse_args(argv)

    print('-> removing fixme comments', file=sys.stderr)
    filenames_with_fixme_comments = []
    for filename in args.filenames:
        with open(filename) as f:
            src = f.read()

        lines = src.splitlines(keepends=True)
        src_without_comments = ''.join(
            _remove_comments(
                lines, args.rule_name,
            ),
        )

        if src_without_comments == src:
            continue

        with open(filename, 'w') as f:
            f.write(src_without_comments)

        print(filename, file=sys.stderr)
        filenames_with_fixme_comments.append(filename)

    if not filenames_with_fixme_comments:
        print('no fixme comments found', file=sys.stderr)
        return 0

    print('-> running fixit', file=sys.stderr)
    ret, message = _run_fixit_fix(
        args.rule_name, filenames_with_fixme_comments,
    )
    print(message, file=sys.stderr)

    return ret


if __name__ == '__main__':
    raise SystemExit(main())
