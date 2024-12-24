# hplx
This project is a collection of tools to help use the HPL benchmark. 
It has been tested and developed against [HPL 2.3](http://www.netlib.org/benchmark/hpl/).
It may or may not work with other versions of the Linpack benchmark. Please give it a go and
report back.

## Installation
The project is available on PyPi and may be installed as follows:

```pip install hmxlabs.hplx```

## Usage
The project provides a command line tool called `hplx`. The tool provides a number of 
subcommands to help with the usage of HPL. The tool is able to

- Generate HPL.dat files
- Read HPL output files, parse the results and output them in CSV or JSON lines format
- Execute the HPL benchmark

The generation of the `HPL.dat` file can be done in one of two ways:
- A theoretically calculated version to provide the highest performance (gflops)
- A number of permutations designed to experimentally discover the highest performance configuration

Correspondingly, the HPL benchmark can be executed in one of two ways:
- A single run of the benchmark using the theoretically calculated `HPL.dat` file
- A number of runs of the benchmark using the experimentally discovered `HPL.dat` files

### Help Output
The `hplx` tool provides a help output to guide the user on how to use the tool.

```python3 -m hmxlabs.hplx --help```

### Reading Results from HPL Output
The `hplx` tool can read the results from the HPL output file and output them in CSV or JSON lines format.

```python3 -m hmxlabs.hplx  parse-results --input-file HPL.out --output-file results [--output-jsonlines]```

This will parse a file named `HPL.out` and output the results in a file named `results`. 
If the `--output-jsonlines` flag is provided, the results will be output in JSON lines format else
CSV format. The results file will have the corresponding extension `.csv` or `.jsonl`.

The ouput to stdout will also provide the highest gflops achieved.