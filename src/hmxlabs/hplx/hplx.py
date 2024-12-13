import argparse
import os
import sys
import psutil
import subprocess
from pathlib import Path
from hmxlabs.hplx.hpl_input import HplInputFileGenerator
from hmxlabs.hplx.hpl_results import HplResult, HplResultsFile


def main():
    setup_argparse()

def setup_argparse():
    argparser = argparse.ArgumentParser(description="HPLinpack benchmark input and output file tool",
                                        epilog="(C) HMx Labs Limited 2024. All Rights Reserved.")

    subparsers = argparser.add_subparsers()
    parser_output = subparsers.add_parser("output", help="Process HPLinpack output files")
    parser_output.set_defaults(func=process_output)
    parser_output.add_argument("--input", dest="input", required=False, action="store_true", default=False,
                                  help="The HPL output file to process")

    parser_input = subparsers.add_parser("input", help="Generate HPLinpack input files")
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

    try:
        args.func(args)
    except Exception as e:
        print("An error occurred. Exiting")
        print(f"Error: {e}")
        sys.exit(1)

def process_output(args):
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
    print("Finding optimal parameters")
    # Approach here is to
    # 1. Run with multuple process grids and a fixed small problem size
    # 2. From the output select the best performing grid and then run with multiple problem sizes
    # 3. From the output select the best performing problem size

    input_file = "./HPL.dat"
    # Check if the input file exists and delete it if it does
    if Path(input_file).exists():
        Path(input_file).unlink()

    cpu_count = psutil.cpu_count(logical=False)
    available_memory = psutil.virtual_memory()

    proc_grid_file = "./HPL_PROD_GRID.out"
    if Path(proc_grid_file).exists():
        Path(proc_grid_file).unlink()

    hpl_dat = HplInputFileGenerator.generate_input_file_calc_best_process_grid(cpu_count, True, proc_grid_file)
    with open(input_file, "w") as file:
        file.write(hpl_dat)
        file.close()

    if not Path(input_file).exists():
        print(f"Error creating HPL input file {input_file}", file=sys.stderr)
        sys.exit(1)

    print("Running HPL to determine process grid")
    hpl_cmd = get_hpl_exec_command(cpu_count)
    print(f"Running HPL with command: {hpl_cmd}")
    subprocess.Popen(hpl_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()

    if not (Path(proc_grid_file).exists()):
        print(f"HPL output file for process grid calc not found {proc_grid_file}", file=sys.stderr)
        sys.exit(1)

    proc_grid_results = HplResultsFile.read_result_file(proc_grid_file)
    best_grid = HplResult.highest_gflops(proc_grid_results)
    print(f"Best process grid: {best_grid.to_json()}")




if __name__ == "__main__":
    main()