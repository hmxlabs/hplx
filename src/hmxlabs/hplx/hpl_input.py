# This class is responsible for generating the input file for the HPL benchmark
# It will do this in accordance with the definition of the HPL input file format
# Details on this may be found at https://www.netlib.org/benchmark/hpl/tuning.html
# See also https://www.netlib.org/benchmark/hpl/faqs.html#grid
# This will generate only the first 12 lines of the input file.
# The rest of the file has a defaulted value. This can be overridden by the user
import math


class HplInputFileGenerator:

    MIN_N = 1000
    MAX_N = 1000000
    STEP_N = 1000

    LINE_1_HEADER = "HPLinpack benchmark input file. Generated by hmxlabs.hplx"
    LINE_2_HEADER = "See https://github.com/hmc-labs/hplx for more information"
    LINE_3_COMMENT = " \t\tName of the output file"
    LINE_4_COMMENT = " \t\t\tDestination of the output. Stdout, Stderr or file"
    LINE_5_COMMENT = " \t\t\tNumber of problem sizes to solve for"
    LINE_6_COMMENT = " \t\tProblem sizes to solve for"
    LINE_7_COMMENT = " \t\t\tNumber of block sizes to solve for"
    LINE_8_COMMENT = " \t\tBlock sizes to solve for"
    LINE_9_COMMENT = " \t\t\tPMAP process mapping (0=Row-,1=Column-major)"
    LINE_10_COMMENT = " \t\t\tNumber of process grids to solve for"
    LINE_11_COMMENT = " \t\t\tProcess grid definition. P"
    LINE_12_COMMENT = " \t\t\tProcess grid definition. Q"
    LINES_13_36 = """16.0         threshold
1            # of panel fact
2            PFACTs (0=left, 1=Crout, 2=Right)
1            # of recursive stopping criterium
4            NBMINs (>= 1)
1            # of panels in recursion
2            NDIVs
1            # of recursive panel fact.
1            RFACTs (0=left, 1=Crout, 2=Right)
1            # of broadcast
1            BCASTs (0=1rg,1=1rM,2=2rg,3=2rM,4=Lng,5=LnM)
1            # of lookahead depth
1            DEPTHs (>=0)
2            SWAP (0=bin-exch,1=long,2=mix)
64           swapping threshold
0            L1 in (0=transposed,1=no-transposed) form
0            U  in (0=transposed,1=no-transposed) form
1            Equilibration (0=no,1=yes)
8            memory alignment in double (> 0)
##### This line (no. 32) is ignored (it serves as a separator). ######
0                               Number of additional problem sizes for PTRANS
1200 10000 30000                values of N
0                               number of additional blocking sizes for PTRANS
40 9 8 13 13 20 16 32 64        values of NB
"""

    output_lines_13_36 = LINES_13_36

    @staticmethod
    def generate_theoretical_best_inputs(  cpu_count: int,
                                           available_memory: int,
                                           min_n: int = MIN_N,
                                           max_n:int = 0,
                                           step_n:int = STEP_N,
                                           prob_size_cap = 0) -> (int, int, int, int):

        # Assuming HPL will need 8 bytes per double precision element
        available_memory_gb = available_memory / (1024**3)
        double_precision_size = 8  # bytes per double
        memory_per_core_gb = available_memory_gb / cpu_count
        if 0 == max_n:
            max_n = HplInputFileGenerator.calculate_max_problem_size(available_memory, prob_size_cap)

        best_params = None
        best_performance = 0

        proc_grids = HplInputFileGenerator.generate_possible_process_grids(cpu_count)
        p_vals = proc_grids[0]
        q_vals = proc_grids[1]

        for N in range(min_n, max_n + 1, step_n):
            # Calculate the optimal NB based on memory per core (rule of thumb)
            # Generally, NB is around sqrt(N) for optimal performance
            NB = int(math.sqrt(N))
            # NB is generally in the range 32..256 though so if its outside that range fit to it
            if 32 > NB:
                NB = 32

            if 256 < NB:
                NB = 256

            required_memory = (N * double_precision_size) / (1024 ** 3)  # in GB
            if required_memory <= memory_per_core_gb:

                # Try to balance P and Q. The number of processes (P * Q) should be close to the number of cores
                for idx in range(0, len(p_vals)):
                    P = p_vals[idx]
                    Q = q_vals[idx]
                    performance_metric = required_memory / (P+Q)
                    if performance_metric > best_performance:
                        best_performance = performance_metric
                        best_params = (N, NB, P, Q)

        return best_params


    @staticmethod
    def generate_possible_process_grids(cpu_count: int) -> ([int], [int]):
        """
            This function generates all possible combinations of P and Q that can be used to solve the HPL problem
            given a number of cpus
        """
        process_grids: ([int], [int]) = ([], [])
        for P in range(1, int(cpu_count/2) + 1):
            for Q in range(1, cpu_count + 1):
                if P * Q == cpu_count:
                    process_grids[0].append(P)
                    process_grids[1].append(Q)
        return process_grids


    @staticmethod
    def calculate_max_problem_size(available_memory: int, prob_size_cap:int = 0) -> int:
        # Apply a conservative estimate of 80% of memory can actually be used
        # without starving the system. Assume a double precision matrix and a double is 8 bytes
        num_doubles = available_memory*0.8 / 8
        max_prob_size = int(math.sqrt(num_doubles))
        if 0 != prob_size_cap and max_prob_size > prob_size_cap:
            max_prob_size = prob_size_cap

        return max_prob_size;


    @staticmethod
    def generate_input_file_calc_best_process_grid(cpu_count: int, write_file: bool, output_file: str, row_major: bool = True) -> str:
        process_grid = HplInputFileGenerator.generate_possible_process_grids(cpu_count)
        # Use a very small problem size to calculate the best process grid to minimise compute time
        # as the variation due to block size and problem size is minimal in determining the best grid
        return HplInputFileGenerator.generate_input_file([1000], [64], process_grid[0], process_grid[1], write_file, output_file, row_major)


    @staticmethod
    def generate_possible_problem_sizes(available_memory: int, num_sizes: int = 10, prob_size_cap: int = 0) -> [int]:
        max_problem_size = HplInputFileGenerator.calculate_max_problem_size(available_memory, prob_size_cap)
        # Bit of a random guess here but use 1/8th of the max problem size as the minimum to try and guess a range
        min_problem_size = int(max_problem_size / num_sizes)
        if 1000 > min_problem_size:
            min_problem_size = 1000

        if 1 == num_sizes:
            return [max_problem_size]

        if 2 == num_sizes:
            return [min_problem_size, max_problem_size]

        step_size = int((max_problem_size - min_problem_size) / (num_sizes-1))
        return list(range(min_problem_size, max_problem_size, step_size))


    @staticmethod
    def generate_possible_block_sizes(n: int, num_block_sizes: int = 10) -> [int]:
        # The most likely theoretical best block size is sqrt(n)
        theoretical_best_block_size = int(math.sqrt(n))
        min_nb = int(theoretical_best_block_size/4)
        max_nb = int(theoretical_best_block_size * 2)

        if 32 > theoretical_best_block_size:
            theoretical_best_block_size = 32
        if 256 < theoretical_best_block_size:
            theoretical_best_block_size = 256

        if 32 > min_nb:
            min_nb = 32
        if 256 < max_nb:
            max_nb = 256

        if 1 == num_block_sizes:
            return [theoretical_best_block_size]

        if 2 == num_block_sizes:
            return [min_nb, theoretical_best_block_size]

        if 3 == num_block_sizes:
            return [min_nb, theoretical_best_block_size, max_nb]

        step = int((max_nb-min_nb) / (num_block_sizes - 1))
        return list(range(min_nb, max_nb, step))

    @staticmethod
    def generate_input_file_calc_best_problem_size(available_memory: int, p: [int], q: [int], write_file: bool,
                                                   output_file: str,
                                                   num_prob_sizes: int = 10, num_block_sizes: int = 10,
                                                   prob_size_cap = 0, row_major: bool = True) -> str:
        problem_sizes = HplInputFileGenerator.generate_possible_problem_sizes(available_memory, num_prob_sizes, prob_size_cap)
        max_problem_size = problem_sizes[-1]
        block_sizes = HplInputFileGenerator.generate_possible_block_sizes(max_problem_size, num_block_sizes)

        return HplInputFileGenerator.generate_input_file(problem_sizes, block_sizes, p, q, write_file, output_file, row_major)

    @staticmethod
    def generate_input_file(n: [int], nb: [int], p: [int], q: [int], write_file: bool, output_file: str, row_major: bool = True) -> str:

        if len(p) != len(q):
            raise ValueError("The number of elements in p and q must be the same")

        if not n:
            raise ValueError("The array of problem sizes cannot be empty")

        if len(n) == 0:
            raise ValueError("The array of problem sizes cannot be empty")

        if not nb:
            raise ValueError("The array of block sizes cannot be empty")

        if len(nb) == 0:
            raise ValueError("The array of block sizes cannot be empty")

        if not output_file:
            output_file = "HPL.dat"

        # For our purposes, we either need to write the output to a file or to stdout
        # don't really care about writing to stderr so ignoring that as possible option
        # doing so also simplifies the argument list.
        write_file_line:str = "6"
        if write_file:
            write_file_line = "1"

        # The first two lines of the file are a header
        output = HplInputFileGenerator.LINE_1_HEADER + "\n"
        output += HplInputFileGenerator.LINE_2_HEADER+ "\n"

        # Line 3 is the name of the output file if one were to be used
        output += output_file + HplInputFileGenerator.LINE_3_COMMENT + "\n"
        # Line 4 is the output destination. For this generator that is either file or stdout only.
        output += write_file_line + HplInputFileGenerator.LINE_4_COMMENT + "\n"

        # Line 5 is the number of problem sizes to solve for. This is the length of the n array
        output += str(len(n)) + HplInputFileGenerator.LINE_5_COMMENT + "\n"
        # Line 6 is the problem sizes to solve, space separated
        prob_sizes: str = ""
        for size in n:
            prob_sizes += f"{size} "
        output += prob_sizes + HplInputFileGenerator.LINE_6_COMMENT + "\n"

        # Line 7 is the number of block sizes to solve for. This is the length of the nb array
        output += str(len(nb)) + HplInputFileGenerator.LINE_7_COMMENT + "\n"
        # Line 8 is the block sizes to solve, space separated
        block_sizes: str = ""
        for block in nb:
            block_sizes += f"{block} "
        output += block_sizes + HplInputFileGenerator.LINE_8_COMMENT + "\n"

        # Line 9 is the PMAP process mapping.
        row_major_str = "0"
        if not row_major:
            row_major_str = "1"

        output += row_major_str + HplInputFileGenerator.LINE_9_COMMENT + "\n"

        # Line 10 is the number of process grids to solve for. This is the length of the p or q arrays
        output += str(len(p)) + HplInputFileGenerator.LINE_10_COMMENT + "\n"

        # Line 11 is the process grid definition for P
        p_str: str = ""
        for p_val in p:
            p_str += f"{p_val} "
        output += p_str + HplInputFileGenerator.LINE_11_COMMENT +"\n"

        # Line 12 is the process grid definition for Q
        q_str: str = ""
        for q_val in q:
            q_str += f"{q_val} "
        output += q_str + HplInputFileGenerator.LINE_12_COMMENT + "\n"

        # The rest of the file is a default value. This can be overridden by the user
        output += HplInputFileGenerator.output_lines_13_36
        return output
