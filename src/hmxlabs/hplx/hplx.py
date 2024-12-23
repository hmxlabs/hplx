import argparse
import logging
import os
import sys
from os.path import curdir

import psutil
import subprocess
from pathlib import Path
from hmxlabs.hplx.hpl_input import HplInputFileGenerator
from hmxlabs.hplx.hpl_results import HplResult, HplResultsFile

LOG_FILE = "hplx.log"
MAX_RESULTS_FILE = "highest_gflops"
ALL_RESULTS_FILE = "results"


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
    argparser = argparse.ArgumentParser(description="HPLinpack benchmark input and output file tool",
                                        epilog="(C) HMx Labs Limited 2024. All Rights Reserved.")

    argparser.add_argument("--output-jsonlines", dest="output_jsonlines", required=False,
                                            action=argparse.BooleanOptionalAction, default=False,
                                            help="Output results in JSON lines format")

    subparsers = argparser.add_subparsers()
    parser_output = subparsers.add_parser("parse-output", help="Process HPLinpack output files")
    parser_output.set_defaults(func=parse_output)
    parser_output.add_argument("--input", dest="input", required=False, action="store_true", default=False,
                                  help="The HPL output file to process")

    parser_input = subparsers.add_parser("gen-input", help="Generate HPLinpack input files")
    parser_input.set_defaults(func=generate_input)
    parser_input.add_argument("--output", dest="output", required=False, action="store_true", default=False,
                                  help="The name of HPL input file to generate")

    parser_find_optimal = subparsers.add_parser("calc-optimal", help="Find optimal HPLinpack parameters via exectution")
    parser_find_optimal.set_defaults(func=calc_optimal)

    try:
        args = argparser.parse_args()
    except Exception:
        argparser.print_help()
        sys.exit(1)

    if not hasattr(args, "func"):
        argparser.print_help()
        sys.exit(1)

    return args


def parse_output(args):
    print("Processing output")

def generate_input(args):
    print("Generating input")

def get_hpl_exec_command(cpu_count: int) -> str:
    hpl_cmd = os.environ.get("HPL_EXEC", None)
    if not hpl_cmd:
        print("HPL_EXEC environment variable not set", file=sys.stderr)
        sys.exit(1)

    return hpl_cmd.replace("$CPUS$", str(cpu_count))

def calc_optimal(args):
    logging.info("Calculating maximal gflops experimentally")
    # Approach here is to
    # 1. Run with multuple process grids and a fixed small problem size
    # 2. From the output select the best performing grid and then run with multiple problem sizes
    # 3. From the output select the best performing problem size

    cpu_count = psutil.cpu_count(logical=False)
    available_memory = psutil.virtual_memory().total
    hpl_cmd = get_hpl_exec_command(cpu_count)
    logging.info(f"HPL command: {hpl_cmd}")

    proc_grid_file = "./HPL_PROC_GRID.out"
    if Path(proc_grid_file).exists():
        Path(proc_grid_file).unlink()

    input_file = "./HPL.dat"
    logging.info(f"Creating HPL input file to determine best process grid...")
    hpl_dat = HplInputFileGenerator.generate_input_file_calc_best_process_grid(cpu_count, True, proc_grid_file)
    write_hpl_input_file(hpl_dat, input_file)

    proc_grid_results = run_hpl(hpl_cmd, proc_grid_file)
    best_grid = HplResult.highest_gflops(proc_grid_results)
    logging.info(f"Best process grid: {best_grid}")

    prob_sizes_file = "./HPL_PROB_SIZES.out"
    if Path(prob_sizes_file).exists():
        Path(prob_sizes_file).unlink()

    hpl_dat = HplInputFileGenerator.generate_input_file_calc_best_problem_size(available_memory, best_grid.p, best_grid.q, True, prob_sizes_file)
    write_hpl_input_file(hpl_dat, input_file)
    prob_size_results = run_hpl(hpl_cmd, prob_sizes_file)
    best_prob_size = HplResult.highest_gflops(prob_size_results)
    logging.info(f"Best problem size: {best_prob_size}")

    logging.info(f"Highest GFLOPS: {best_prob_size.gflops}")
    logging.info("Writing highest GFLOPS to file")
    write_results(MAX_RESULTS_FILE, [best_prob_size], args.output_jsonlines)

    logging.info("Writing all results to file")
    all_results = proc_grid_results + prob_size_results
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


def run_hpl(hpl_cmd: str, expected_output_file:str) -> list[HplResult]:
    logging.info(f"Running HPL with command: {hpl_cmd}")
    subprocess.Popen(hpl_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()

    if not (Path(expected_output_file).exists()):
        logging.error(f"The expected output file running HPL: {expected_output_file} was not found. Did the command run?")
        sys.exit(1)

    if not Path(expected_output_file).is_file():
        logging.error(f"The expected output file running HPL: {expected_output_file} is not a file")
        sys.exit(1)

    if Path(expected_output_file).stat().st_size == 0:
        logging.error(f"The expected output file running HPL: {expected_output_file} is empty")
        sys.exit(1)

    results = HplResultsFile.read_result_file(expected_output_file)
    if len(results) == 0:
        logging.error(f"No results found in the expected output file running HPL: {expected_output_file}")
        sys.exit(1)

    return results


def write_results(file_path: str, results: list[HplResult], jsonlines: bool) -> None:

    if jsonlines:
        file_path = file_path + ".json"
        HplResultsFile.write_results_to_json(file_path, results)
    else:
        file_path = file_path + ".csv"
        HplResultsFile.write_results_to_csv(file_path, results)
        

if __name__ == "__main__":
    main()