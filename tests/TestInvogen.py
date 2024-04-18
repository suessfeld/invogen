from typer.testing import CliRunner
from invogen import app

runner = CliRunner()
def test_cli_with_valid_inputs():
    result = runner.invoke(app,
                           ["--input_html", "C:/Users/evoil/PycharmProjects/invogen/sample_invoice/invoice_example2.html" ,
                            "--input_css", "C:/Users/evoil/PycharmProjects/invogen/sample_invoice/invoice_example2.css"])
    assert result.exit_code == 0
    assert "Expected Success Output" in result.stdout

def test_cli_negative_amount():
    result = runner.invoke(app, ["--amount", "-1"])
    assert result.exit_code != 0
    assert "Error: Amount must be greater than or equal to 0" in result.stdout

def test_cli_with_wrong_html_path():
    result = runner.invoke(app, ["--input_html", "nonexistent.html", "--input_css", "valid_path.css"])
    assert result.exit_code != 0
    assert "Error: The specified HTML file does not exist." in result.stdout

def test_cli_with_wrong_css_path():
    result = runner.invoke(app, ["--input_html", "valid_path.html", "--input_css", "nonexistent.css"])
    assert result.exit_code != 0
    assert "Error: The specified CSS file does not exist." in result.stdout

def test_cli_with_both_wrong_paths():
    result = runner.invoke(app, ["--input_html", "nonexistent.html", "--input_css", "nonexistent.css"])
    assert result.exit_code != 0
    assert "Error: The specified HTML and CSS files do not exist." in result.stdout

