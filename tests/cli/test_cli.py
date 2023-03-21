from typer.testing import CliRunner

import simple_css_selector_transform as css_transform

runner = CliRunner()


def test_app():
    result = runner.invoke(css_transform.app, ["--classname=class", "-", "-"], input="table{}")
    assert result.exit_code == 0
    assert ".class table{}" == result.stdout
