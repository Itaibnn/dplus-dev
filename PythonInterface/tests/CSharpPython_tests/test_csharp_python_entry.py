#  tests the functions called from CSharpPythonEntry
import os
from dplus.CalculationRunner import LocalRunner
from dplus.CalculationInput import CalculationInput

from tests.test_settings import exe_directory, session_dir, python_dir, test_files_dir
test_dir=os.path.join(test_files_dir, "CSharpPython_tests", "files")

calc_runner = LocalRunner(exe_directory, session_dir)


def test_init():
    from CSharpPythonEntry import AsyncFit

    filename = os.path.join(test_dir, "sphere.state")
    calc_input = CalculationInput.load_from_state_file(filename)
    async_fit = AsyncFit(exe_directory,session_dir,python_dir,calc_input)