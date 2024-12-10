import unittest
from parameterized import parameterized

from hmxlabs.hplx.hpl_input import HplInputFileGenerator

class TestHplInputFileGenerator(unittest.TestCase):

    def test_generate_input_file(self) -> None:
        output = HplInputFileGenerator.generate_input_file([1000], [32], [2],[2], False,
                                                  "HPL.TEST.dat", True)

        with open("./data/HPL.dat", "r") as file:
            expected_output = file.read()

        self.assertEqual(expected_output, output, "The generated HPL input file did not match the expected output")

    def test_generate_theoretical_best_params(self) -> None:
        cpu_count: int = 4
        params = HplInputFileGenerator.generate_theoretical_best_inputs(4, 16)

        self.assertEqual(1000, params[0], "The value of N was not as expected")
        self.assertEqual(31, params[1], "The value of NB was not as expected")
        self.assertEqual(2, params[2], "The value of P was not as expected")
        self.assertEqual(2, params[3], "The value of Q was not as expected")

        self.assertEqual(cpu_count, params[2]*params[3], "The value of P*Q was not as the cpu count")

    @parameterized.expand([
                            ["case1", 4, 16],
                            ["case2", 8, 32],
                            ["case3", 16, 64],
                            ["case4", 32, 128],
                            ["case5", 64, 256],
                            ["case6", 128, 512],
                            ["case6a", 192, 512],
                            ["case7", 256, 1024],
                        ])
    def test_generate_theoretical_best_params_ext(self, _, cpu_count: int, available_memory_gb: int) -> None:
        params = HplInputFileGenerator.generate_theoretical_best_inputs(cpu_count, available_memory_gb)

        self.assertEqual(cpu_count, params[2]*params[3], "The value of P*Q was not as the cpu count")