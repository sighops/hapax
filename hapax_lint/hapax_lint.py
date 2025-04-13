# version 0.9
#
# Linter for Squarp Hapax instrument definition files.
#

import hapaxlint
import sys

if __name__ == "__main__":
    if not sys.version_info >= (3, 10):
        print("FAIL: Python version 3.10 or greater is required.")
    fname = sys.argv[1]
    linter = hapaxlint.HapaxInstrumentLinter(fname)
    linter.lint()
