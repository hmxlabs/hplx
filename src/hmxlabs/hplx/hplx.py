import argparse
import logging
import os
import sys
import psutil
import subprocess
from pathlib import Path
from hmxlabs.hplx.hpl_input import HplInputFileGenerator
from hmxlabs.hplx.hpl_results import HplResult, HplResultsFile

LOG_FILE = "hplx.log"
MAX_RESULTS_FILE = "hplx-highest-gflops"
ALL_RESULTS_FILE = "hplx-all"

def main():
    curdir = os.getcwd()
    logfile = os.path.join(curdir, LOG_FILE)
    logging.basicConfig(filename=logfile, filemode='a', level=logging.DEBUG,
                        format="%(asctime)s-%(levelname)-s-%(name)s::%(message)s")
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    logging.info("STARTING HPLx")
    logging.info(f"Output directory: {curdir}")

    args = setup_argparse()

    try:
        args.func(args)
    except Exception as e:
        logging.error("An unknown and unhandled error occurred. Exiting", exc_info=e)
        sys.exit(1)

def setup_argparse() -> argparse.Namespace:
    argparser = argparse.ArgumentParser(description="HPLinpack benchmark extension tool",
                                        epilog="(C) HMx Labs Limited 2024. All Rights Reserved.")

    # Global options
    argparser.add_argument("--output-jsonlines", dest="output_jsonlines", required=False,
                                            action=argparse.BooleanOptionalAction, default=False,
                                            help="Output results in JSON lines format")
    argparser.add_argument("--cpu-count", dest="cpu_count", required=False, type=int,
                              default=0,
                              help="The number of physical cores to use in the test. Default is the number of physical cores on the machine")
    argparser.add_argument("--available-memory", dest="available_memory", required=False, type=int,
                              default=psutil.virtual_memory().total,
                              help="The total available memory in bytes. Default is the total available memory on the machine")
    argparser.add_argument("--use-smt", dest="use_smt", required=False, type=bool, action=argparse.BooleanOptionalAction,
                           default=False, help="Use SMT (Hyperthreading) if available when counting CPUs. Default is False")

    argparser.add_argument("--max-prob-size", dest="max_prob_size", required=False, type=int,
                              default=0, help="A cap on the problem size to impose on any type of run")

    # Parse HPL output file
    subparsers = argparser.add_subparsers()
    parser_output = subparsers.add_parser("parse-results", help="Parse HPLinpack output files")
    parser_output.set_defaults(func=parse_output)
    parser_output.add_argument("--input-file", dest="input_file", required=True, type=str,
                                  help="The HPL results file to process")
    parser_output.add_argument("--output-file", dest="output_file", required=False, type=str, default=None,
                                  help="The output file to write the processed results to. If not specified no output file is written")

    # Generate input file (theoretical best)
    parser_gen_input_tbest = subparsers.add_parser("gen-input-theoretical-best", help="Generate theoretical best HPLinpack input files")
    parser_gen_input_tbest.add_argument("--filename", dest="output_file", required=False, type=str, default="HPL.dat",
                                  help="The output file to write the generated input to. Default is HPL.dat")
    parser_gen_input_tbest.add_argument("--results-file", dest="results_file", required=False, type=str, default=None,
                                        help="The results file to write the generated input to. HPL results are written to this stdout")
    parser_gen_input_tbest.add_argument("--min-prob-sizes", dest="min_prob_sizes", type=int, required=False,
                                            default=1000,
                                            help="The minimum problem size (N) to evaluate for use. Default is 1000")
    parser_gen_input_tbest.add_argument("--max-prob-sizes", dest="max_prob_sizes", type=int, required=False,
                                            default=0,
                                            help="The maximum problem size (N) to evaluate for use. Default determined N based on available memory")
    parser_gen_input_tbest.add_argument("--prob-sizes-step", dest="prob_sizes_step", type=int, required=False,
                                            default=5000,
                                            help="The maximum problem size (N) step size for theoretical evaluation. Default is 5000")
    parser_gen_input_tbest.set_defaults(func=generate_input_tbest)

    # Generate input file (calc optimal)
    parser_gen_input_calc_optimal = subparsers.add_parser("gen-input-calc-optimal", help="Generate HPLinpack input file to experimentally determine optimal parameters")
    parser_gen_input_calc_optimal.add_argument("--filename", dest="output_file", required=False, type=str, default="HPL.dat",
                                        help="The output file to write the generated input to. Default is HPL.dat")
    parser_gen_input_calc_optimal.add_argument("--results-file", dest="results_file", required=False, type=str, default=None,
                                        help="The results file to write the generated input to. HPL results are written to this stdout")
    parser_gen_input_calc_optimal.add_argument("--num-prob-sizes", dest="n_prob_sizes", type=int, required=False, default=10,
                                     help="The number of problem sizes (N) to use in the test. Default is 10")
    parser_gen_input_calc_optimal.add_argument("--num-block-sizes", dest="n_block_sizes", type=int, required=False, default=10,
                                     help="The number of block sizes (NB) to use in the test. Default is 10")
    parser_gen_input_calc_optimal.set_defaults(func=generate_input_calc_optimal)

    # Calculate optimal
    parser_find_optimal = subparsers.add_parser("calc-optimal", help="Find optimal HPLinpack parameters via exectution")
    parser_find_optimal.add_argument("--num-prob-sizes", dest="n_prob_sizes", type=int, required=False, default=10,
                                    help="The number of problem sizes (N) to use in the test. Default is 10")
    parser_find_optimal.add_argument("--num-block-sizes", dest="n_block_sizes", type=int, required=False, default=10,
                                     help="The number of block sizes (NB) to use in the test. Default is 10")
    parser_find_optimal.set_defaults(func=calc_optimal)

    # Theoretical optimal
    parser_theoretical_optimal = subparsers.add_parser("run-theoretical-optimal",
                                                       help="Use theoretical best input parameters to run HPL")
    parser_theoretical_optimal.add_argument("--min-prob-sizes", dest="min_prob_sizes", type=int, required=False, default=1000,
                                     help="The minimum problem size (N) to evaluate for use. Default is 1000")
    parser_theoretical_optimal.add_argument("--max-prob-sizes", dest="max_prob_sizes", type=int, required=False, default=0,
                                     help="The maximum problem size (N) to evaluate for use. Default determined N based on available memory")
    parser_theoretical_optimal.add_argument("--prob-sizes-step", dest="prob_sizes_step", type=int, required=False, default=1000,
                                     help="The problem size (N) step size for theoretical evaluation. Default is 1000")
    parser_theoretical_optimal.set_defaults(func=run_theoretical_optimal)

    # Run ALL.

    parser_run_all = subparsers.add_parser("run-all", help="Run all theoretical best and experimental optimal tests")
    parser_run_all.add_argument("--num-prob-sizes", dest="n_prob_sizes", type=int, required=False, default=10,
                                     help="The number of problem sizes (N) to use experimentally. Default is 10")
    parser_run_all.add_argument("--num-block-sizes", dest="n_block_sizes", type=int, required=False, default=10,
                                     help="The number of block sizes (NB) to use experimentally. Default is 10")
    parser_run_all.add_argument("--min-prob-sizes", dest="min_prob_sizes", type=int, required=False,
                                            default=1000,
                                            help="The minimum problem size (N) to determine the theoretical max Default is 1000")
    parser_run_all.add_argument("--max-prob-sizes", dest="max_prob_sizes", type=int, required=False,
                                            default=0,
                                            help="The maximum problem size (N) to determine the theoretical max. Default determined N based on available memory")
    parser_run_all.add_argument("--prob-sizes-step", dest="prob_sizes_step", type=int, required=False,
                                            default=1000,
                                            help="The problem size (N) step size for to determine the theoretical max. Default is 1000")
    parser_run_all.set_defaults(func=run_all_calcs)

    try:
        args = argparser.parse_args()
    except Exception:
        argparser.print_help()
        sys.exit(1)

    if not hasattr(args, "func"):
        argparser.print_help()
        sys.exit(1)

    return args


def parse_output(args) -> None:

    input_file = args.input_file
    write_output = False
    output_file = None
    if args.output_file is not None:
        write_output = True
        output_file = args.output_file

    logging.info(f"Parsing HPL results. Input file: {input_file}")
    input_file_path = Path(input_file)
    if not input_file_path.exists():
        logging.error(f"Input file {input_file} does not exist")
        sys.exit(1)

    if not input_file_path.is_file():
        logging.error(f"Input file {input_file} is not a file")
        sys.exit(1)

    if input_file_path.stat().st_size == 0:
        logging.error(f"Input file {input_file} is empty")
        sys.exit(1)

    results = HplResultsFile.read_result_file(input_file)
    if len(results) == 0:
        logging.error(f"No results found in the input file {input_file}")
        sys.exit(1)

    best_result = HplResult.highest_gflops(results)
    logging.info(f"Parsed {len(results)} results. Highest GFLOPS: {best_result.gflops}")

    if write_output:
        logging.info(f"Writing output to file: {output_file}")
        write_results(output_file, results, args.output_jsonlines)


def generate_input_tbest(args):
    logging.info("Generating HPL input file assuming theoretical best parameters")
    cpu_count = get_cpu_count(args)
    available_memory = args.available_memory
    output_file = args.output_file
    output_file_path = Path(output_file)
    if output_file_path.exists():
        logging.debug(f"Deleting existing HPL input file: {output_file}")
        output_file_path.unlink()

    write_results_file = False
    results_file = "HPL.out"
    if args.results_file is not None:
        write_results_file = True
        results_file = args.results_file

    logging.info("Generating input for theoretical best parameters")
    hpl_dat_inputs = HplInputFileGenerator.generate_theoretical_best_inputs(cpu_count, available_memory,
                                                                            args.min_prob_sizes,
                                                                            args.max_prob_sizes,
                                                                            args.prob_sizes_step,
                                                                            args.max_prob_size)

    hpl_dat = HplInputFileGenerator.generate_input_file([hpl_dat_inputs[0]], [hpl_dat_inputs[1]],
                                                        [hpl_dat_inputs[2]],
                                                        [hpl_dat_inputs[3]], write_results_file, results_file)


    write_hpl_input_file(hpl_dat, output_file)


def generate_input_calc_optimal(args) -> None:
    logging.info("Generating HPL input file to determine optimal gflops experimentally")
    cpu_count = get_cpu_count(args)
    available_memory = args.available_memory
    output_file = args.output_file
    output_file_path = Path(output_file)
    if output_file_path.exists():
        logging.debug(f"Deleting existing HPL input file: {output_file}")
        output_file_path.unlink()

    write_results_file = False
    results_file = "HPL.out"
    if args.results_file is not None:
        write_results_file = True
        results_file = args.results_file

    logging.info("Generating input for calculation of optimal parameters")
    proc_grid = HplInputFileGenerator.generate_possible_process_grids(cpu_count)
    hpl_dat = HplInputFileGenerator.generate_input_file_calc_best_problem_size(available_memory, proc_grid[0],
                                                                               proc_grid[1], write_results_file,
                                                                               results_file, args.n_prob_sizes,
                                                                               args.n_block_sizes, args.max_prob_size)
    write_hpl_input_file(hpl_dat, output_file)


def get_hpl_exec_command(cpu_count: int) -> str:
    hpl_cmd = os.environ.get("HPL_EXEC", None)
    if not hpl_cmd:
        print("HPL_EXEC environment variable not set", file=sys.stderr)
        sys.exit(1)

    return hpl_cmd.replace("$CPUS$", str(cpu_count))


def run_theoretical_optimal(args):
    results = _run_theoretical_optimal(args)
    write_results(MAX_RESULTS_FILE, results, args.output_jsonlines)

def calc_optimal(args):
    results = _run_calc_optimal(args)
    highest_gflop_result = HplResult.highest_gflops(results)
    logging.info(f"Best input config size: {highest_gflop_result}")
    logging.info(f"Highest GFLOPS: {highest_gflop_result.gflops}")
    logging.info("Writing highest GFLOPS to file")
    write_results(MAX_RESULTS_FILE, [highest_gflop_result], args.output_jsonlines)
    write_results(ALL_RESULTS_FILE, results, args.output_jsonlines)

def run_all_calcs(args) -> None:
    theoretical_results = _run_theoretical_optimal(args)
    calc_results = _run_calc_optimal(args)
    all_results = theoretical_results + calc_results
    highest_gflop_result = HplResult.highest_gflops(all_results)
    logging.info(f"Best input config size: {highest_gflop_result}")
    logging.info(f"Highest GFLOPS: {highest_gflop_result.gflops}")
    logging.info("Writing highest GFLOPS to file")
    write_results(MAX_RESULTS_FILE, [highest_gflop_result], args.output_jsonlines)
    write_results(ALL_RESULTS_FILE, all_results, args.output_jsonlines)

def write_hpl_input_file(contents: str, filename: str) -> None:
    if Path(filename).exists():
        logging.debug(f"Deleting existing HPL input file: {filename}")
        Path(filename).unlink()

    logging.debug(f"Creating HPL input file: {filename}")
    with open(filename, "w") as file:
        file.write(contents)
        file.close()

    if not Path(filename).exists():
        logging.error(f"Error creating HPL input file {filename}")
        sys.exit(1)


def run_hpl(cpu_count: int, expected_output_file:str, run_type: str = None) -> list[HplResult]:
    logging.info(f"Will run HPL with {cpu_count} CPUs")
    hpl_cmd = get_hpl_exec_command(cpu_count)

    logging.info(f"Running HPL with command: {hpl_cmd}")
    subprocess.Popen(hpl_cmd, shell=True).wait()

    expected_output_path = Path(expected_output_file)
    if not expected_output_path.exists():
        logging.error(f"The expected output file running HPL: {expected_output_file} was not found. Did the command run?")
        sys.exit(1)

    if not expected_output_path.is_file():
        logging.error(f"The expected output file running HPL: {expected_output_file} is not a file")
        sys.exit(1)

    if expected_output_path.stat().st_size == 0:
        logging.error(f"The expected output file running HPL: {expected_output_file} is empty")
        sys.exit(1)

    results = HplResultsFile.read_result_file(expected_output_file)
    if len(results) == 0:
        logging.error(f"No results found in the expected output file running HPL: {expected_output_file}")
        sys.exit(1)

    for result in results:
        result.type = run_type
        result.cpu_count = cpu_count

    return results


def write_results(file_path: str, results: list[HplResult], jsonlines: bool) -> None:

    if jsonlines:
        file_path = file_path + ".json"
        HplResultsFile.write_results_to_json(file_path, results)
    else:
        file_path = file_path + ".csv"
        HplResultsFile.write_results_to_csv(file_path, results)


def _run_theoretical_optimal(args) -> list[HplResult]:
    logging.info("Running HPL with theoretical best parameters")

    cpu_count = get_cpu_count(args)
    available_memory = args.available_memory

    input_file = "./HPL.dat"
    theoretical_max_file = "./HPL_THEORETICAL_MAX.out"
    if Path(theoretical_max_file).exists():
        Path(theoretical_max_file).unlink()

    logging.info(f"Creating HPL input file to determine theoretical best parameters...")
    hpl_dat_inputs = HplInputFileGenerator.generate_theoretical_best_inputs(cpu_count, available_memory,
                                                                            args.min_prob_sizes,
                                                                            args.max_prob_sizes, args.prob_sizes_step,
                                                                            args.max_prob_size)

    hpl_dat = HplInputFileGenerator.generate_input_file([hpl_dat_inputs[0]], [hpl_dat_inputs[1]], [hpl_dat_inputs[2]],
                                                        [hpl_dat_inputs[3]], True, theoretical_max_file)
    write_hpl_input_file(hpl_dat, input_file)
    logging.info(
        f"Running HPL with theoretical best parameters. N={hpl_dat_inputs[0]}, NB={hpl_dat_inputs[1]}, P={hpl_dat_inputs[2]}, Q={hpl_dat_inputs[3]}")
    results = run_hpl(cpu_count, theoretical_max_file, "theoretical_max")
    best_gflops = HplResult.highest_gflops(results)
    logging.info(f"Theoretical best GFLOPS: {best_gflops.gflops}")
    return results

def _run_calc_optimal(args) -> list[HplResult]:
    logging.info(
        f"Calculating maximal gflops experimentally with {args.n_prob_sizes} problem sizes and {args.n_block_sizes} block sizes")
    # Approach here is to
    # 1. Run with multuple process grids and a fixed small problem size
    # 2. From the output select the best performing grid and then run with multiple problem sizes
    # 3. From the output select the best performing problem size

    cpu_count = get_cpu_count(args)
    available_memory = args.available_memory

    proc_grid_file = "./HPL_PROC_GRID.out"
    if Path(proc_grid_file).exists():
        Path(proc_grid_file).unlink()

    input_file = "./HPL.dat"
    logging.info(f"Creating HPL input file to determine best process grid...")
    hpl_dat = HplInputFileGenerator.generate_input_file_calc_best_process_grid(cpu_count, True, proc_grid_file)
    write_hpl_input_file(hpl_dat, input_file)

    proc_grid_results = run_hpl(cpu_count, proc_grid_file, "proc_grid")
    best_grid = HplResult.highest_gflops(proc_grid_results)
    logging.info(f"Best process grid: {best_grid}")

    prob_sizes_file = "./HPL_PROB_SIZES.out"
    if Path(prob_sizes_file).exists():
        Path(prob_sizes_file).unlink()

    hpl_dat = HplInputFileGenerator.generate_input_file_calc_best_problem_size(available_memory, [best_grid.p],
                                                                               [best_grid.q], True,
                                                                               prob_sizes_file, args.n_prob_sizes,
                                                                               args.n_block_sizes, args.max_prob_size)
    write_hpl_input_file(hpl_dat, input_file)
    prob_size_results = run_hpl(cpu_count, prob_sizes_file, "prob_size")
    all_results = proc_grid_results + prob_size_results
    return all_results


def get_cpu_count(args) -> int:
    if args.cpu_count > 0:
        logging.info(f"Using user specified CPU count: {args.cpu_count}")
        return args.cpu_count

    smt_off_cpus = psutil.cpu_count(logical=False)
    smt_on_cpus = psutil.cpu_count(logical=True)
    cpu_count = smt_off_cpus
    if args.use_smt:
        cpu_count = smt_on_cpus

    logging.info(f"Using {cpu_count} CPUs. Use SMT: {args.use_smt}. Physical CPU Cores: {smt_off_cpus}. Logical CPU Cores: {smt_on_cpus}")
    return cpu_count

if __name__ == "__main__":
    main()