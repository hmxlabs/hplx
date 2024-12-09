import unittest
import json
from pathlib import Path

from hmxlabs.hplx.hpl_input import HplInputFileGenerator

class TestHplInputFileGenerator(unittest.TestCase):

    def test_generate_input_file(self) -> None:
        output = HplInputFileGenerator.generate_input_file([1000], [32], [2],[2], False,
                                                  "HPL.TEST.dat", True)

        with open("./data/HPL.dat", "r") as file:
            expected_output = file.readlines()

        self.assertEqual(expected_output, output, "The generated HPL input file did not match the expected output")

