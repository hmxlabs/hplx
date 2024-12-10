import argparse
import sys

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

    parser_find_optimal = subparsers.add_parser("find_optimal", help="Find optimal HPLinpack parameters via exectution")
    parser_find_optimal.set_defaults(func=find_optimal)

    try:
        args = argparser.parse_args()
        args.func(args)
    except Exception:
        argparser.print_help()
        sys.exit(1)

def process_output(args):
    print("Processing output")

def generate_input(args):
    print("Generating input")

def find_optimal(args):
    print("Finding optimal parameters")

if __name__ == "__main__":
    main()