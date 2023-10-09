from hapax_lint import HapaxInstrumentLinter, HapaxLintException, HapaxLintWarning

linter = HapaxInstrumentLinter()

def test_is_in_range_true():
    result = linter.is_in_range(55, 1, 100)
    assert result == True


def test_is_in_range_false():
    result = linter.is_in_range(450, 1, 100)
    assert result == False

def test_is_in_range_false_when_string():
    result = linter.is_in_range("cheese", 1, 100)
    assert result == False

def test_depth_is_valid():
    result = linter.depth_is_valid(7)
    assert result == True
    result = linter.depth_is_valid(14)
    assert result == True
    result = linter.depth_is_valid(5)
    assert result == False

def test_lint_NRPN():
    line = "23:55:7 Something"
    result = linter.lint_NRPN(line)
    assert result == True

    line = "23:55:7:DEFAULT=122 Something Else"
    result = linter.lint_NRPN(line)
    assert result == True

def test_lint_CC():
    line = "1:DEFAULT=64 Modulation Wheel"
    result = linter.lint_CC(line)
    assert result == True

    line = "5 PORTAMENTO TIME"
    result = linter.lint_CC(line)
    assert result == True

def test_lint_PC():
    line = "111:1:0 NAME WITH SPACES"
    result = linter.lint_PC(line)
    assert result == True

    line = "114 NAME"
    result = linter.lint_PC(line)
    assert result == True

def test_lint_drumlanes():
    line = "3:45:8:89 DRUMLANE 1"
    result = linter.lint_drumlanes(line)
    assert result == True

    line = "7:22:CVG1:122 DRUMLANE 2"
    result = linter.lint_drumlanes(line)
    assert result == True
