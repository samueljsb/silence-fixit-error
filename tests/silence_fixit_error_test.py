from __future__ import annotations

from silence_fixit_error import _find_violations
from silence_fixit_error import main
from silence_fixit_error import Violation


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
