from __future__ import annotations

import pytest

from silence_fixit_error import _find_violations
from silence_fixit_error import _parse_output_line
from silence_fixit_error import main
from silence_fixit_error import Violation


@pytest.mark.parametrize(
    'lines, expected_violations', (
        pytest.param(
            ['t.py@1:2 MyRuleName: the error message'],
            [Violation('t.py', 'MyRuleName', 1)],
            id='single-line',
        ),
        pytest.param(
            [
                't.py@1:2 MyRuleName: the error message',
                'which continue over multiple lines',
                'just like this one does.',
            ],
            [Violation('t.py', 'MyRuleName', 1), None, None],
            id='multi-line',
        ),
        pytest.param(
            [
                't.py@1:2 MyRuleName: ',
                'the error message on a new line',
                'which continue over multiple lines',
                'just like this one does.',
            ],
            [Violation('t.py', 'MyRuleName', 1), None, None, None],
            id='multi-line-leading-ws',
        ),
        pytest.param(
            [
                't.py@1:2 MyRuleName: the error message',
                'which continue over multiple lines',
                'just like this one does.',
                '',
            ],
            [Violation('t.py', 'MyRuleName', 1), None, None, None],
            id='multi-line-trailing-ws',
        ),
        pytest.param(
            ['t.py@1:2 MyRuleName: '],
            [Violation('t.py', 'MyRuleName', 1)],
            id='no-message',
        ),
    ),
)
def test_parse_output_line(lines, expected_violations):
    violations = [
        _parse_output_line(line)
        for line in lines
    ]

    assert violations == expected_violations


def test_find_violations(tmp_path, capsys):
    python_module = tmp_path / 't.py'
    python_module.write_text("""\
x = None
isinstance(x, str) or isinstance(x, int)
""")

    violations = _find_violations(
        'fixit.rules:CollapseIsinstanceChecks', [str(python_module)],
    )

    assert violations == {
        str(python_module): [
            Violation(str(python_module), 'CollapseIsinstanceChecks', 2),
        ],
    }


def test_main(tmp_path, capsys):
    python_module = tmp_path / 't.py'
    python_module.write_text("""\
x = None
isinstance(x, str) or isinstance(x, int)

def f(x):
    return isinstance(x, str) or isinstance(x, int)
""")

    ret = main(('fixit.rules:CollapseIsinstanceChecks', str(python_module)))

    assert ret == 1
    assert python_module.read_text() == """\
x = None
# lint-fixme: CollapseIsinstanceChecks
isinstance(x, str) or isinstance(x, int)

def f(x):
    # lint-fixme: CollapseIsinstanceChecks
    return isinstance(x, str) or isinstance(x, int)
"""

    captured = capsys.readouterr()
    assert captured.err == f"""\
-> running fixit
found violations in 1 files
-> adding fixme comments
{python_module}
"""


def test_main_no_violations(tmp_path, capsys):
    src = """\
def foo():
    print('hello there')
"""

    python_module = tmp_path / 't.py'
    python_module.write_text(src)

    ret = main(('fixit.rules:CollapseIsinstanceChecks', str(python_module)))

    assert ret == 0
    assert python_module.read_text() == src

    captured = capsys.readouterr()
    assert captured.err == """\
-> running fixit
no violations found
"""


def test_main_multiple_different_violations(tmp_path, capsys):
    src = """\
x = None
isinstance(x, str) or isinstance(x, int)

if True:
    pass
"""

    python_module = tmp_path / 't.py'
    python_module.write_text(src)

    ret = main(('fixit.rules', str(python_module)))

    assert ret == 1

    captured = capsys.readouterr()
    assert captured.err == """\
-> running fixit
found violations in 1 files
ERROR: errors found for multiple rules: ['CollapseIsinstanceChecks', 'NoStaticIfCondition']
"""  # noqa: E501
