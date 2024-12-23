import unittest
from parameterized import parameterized

from hmxlabs.hplx.hpl_input import HplInputFileGenerator

class TestHplInputFileGenerator(unittest.TestCase):

    def test_generate_process_grid(self) -> None:
        grid = HplInputFileGenerator.generate_possible_process_grids(4)
        self.assertEqual(2, len(grid), "The number of possible grids was not as expected")
        self.assertEqual(1, grid[0][0], "The value of P was not as expected")
        self.assertEqual(2, grid[0][1], "The value of P was not as expected")
        self.assertEqual(4, grid[1][0], "The value of Q was not as expected")
        self.assertEqual(2, grid[1][1], "The value of Q was not as expected")

    def test_generate_input_file(self) -> None:
        output = HplInputFileGenerator.generate_input_file([1000], [32], [2],[2], False,
                                                  "HPL.TEST.out", True)

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

    def test_generate_possible_problem_sizes(self) -> None:
        available_mem = 16 * (1024**3)
        prob_size = 10
        sizes = HplInputFileGenerator.generate_possible_problem_sizes(16*1024*1024*1024, prob_size)
        max_size = HplInputFileGenerator.calculate_max_problem_size(available_mem)
        self.assertEqual(prob_size, len(sizes), "The number of possible problem sizes was not as expected")
        self.assertLess(1000, sizes[0], "The value of N was not as expected")
        self.assertGreater(max_size, sizes[-1], "The largest problem size is greater than the maximum size")

    def test_generate_block_sizes(self) -> None:
        available_mem = 16 * (1024 ** 3)
        prob_sizes  = HplInputFileGenerator.generate_possible_problem_sizes(available_mem)
        num_block_sizes = 5
        block_sizes = HplInputFileGenerator.generate_possible_block_sizes(prob_sizes[-1], num_block_sizes)
        self.assertEqual(num_block_sizes, len(block_sizes), "The number of possible block sizes was not as expected")
        self.assertLess(32, block_sizes[0], "The lowest block size was less than 32")
        self.assertGreater(256, block_sizes[-1], "The highest block size was greater than 256")