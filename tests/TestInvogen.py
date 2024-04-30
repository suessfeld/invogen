import os
from os.path import abspath

from typer.testing import CliRunner
from invogen import app

runner = CliRunner()
def test_cli_with_valid_inputs():
    result = runner.invoke(app,
                           ["--input-html", "C:/Users/evoil/PycharmProjects/invogen/sample_invoice/invoice_example1.html" ,
                            "--input-css", "C:/Users/evoil/PycharmProjects/invogen/sample_invoice/invoice_example1.css",
                            "--amount", "1",
                            "--output", "C:/Users/evoil/PycharmProjects/invogen/output"
    ])
    assert result.exit_code == 0

def test_cli_negative_amount():
    result = runner.invoke(app, ["--amount", "-1"])
    assert result.exit_code != 0
    assert "Error: Amount must be greater than or equal to 0" in result.stdout

def test_cli_with_missing_output_path():
    result = runner.invoke(app)
    assert result.exit_code != 0
    assert "Missing option '--output'" in result.stdout

def test_cli_with_wrong_css_path():
    result = runner.invoke(app, ["--input-html", "valid-path.html", "--input-css", "nonexistent.css", "--output", ".", "--amount", "1"])
    assert result.exit_code != 0
    assert "The specified CSS file does not exist." in result.stdout

