from __future__ import annotations

from fix_silenced_fixit_error import main


def test_main(tmp_path, capsys):
    src = """\
x = None
# lint-fixme: CollapseIsinstanceChecks
isinstance(x, str) or isinstance(x, int)
isinstance(x, bool) or isinstance(x, float)  # lint-fixme: CollapseIsinstanceChecks

def f(x):
    # lint-ignore: CollapseIsinstanceChecks
    return isinstance(x, str) or isinstance(x, int)
"""  # noqa: E501

    python_module = tmp_path / 't.py'
    python_module.write_text(src)

    ret = main(('fixit.rules:CollapseIsinstanceChecks', str(python_module)))

    assert ret == 0
    assert python_module.read_text() == """\
x = None
isinstance(x, (str, int))
isinstance(x, (bool, float))

def f(x):
    # lint-ignore: CollapseIsinstanceChecks
    return isinstance(x, str) or isinstance(x, int)
"""

    captured = capsys.readouterr()
    assert captured.err == f"""\
-> removing fixme comments
{python_module}
-> running fixit
🛠️  1 file checked, 1 file with errors, 2 auto-fixes available, 2 fixes applied 🛠️
"""  # noqa: E501


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
-> removing fixme comments
no fixme comments found
"""
