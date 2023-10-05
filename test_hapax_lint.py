from hapax_lint import HapaxLinter, HapaxLintException

linter = HapaxLinter()

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