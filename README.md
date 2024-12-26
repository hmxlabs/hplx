# hplx
This project is a collection of tools to help use the HPL benchmark. 
It has been tested and developed against [HPL 2.3](http://www.netlib.org/benchmark/hpl/).
It may or may not work with other versions of the Linpack benchmark. Please give it a go and
report back.

## Installation
The project is available on PyPi and may be installed as follows:

```
pip install hmxlabs.hplx
```
or
```
python3 -m pip install hmxlabs.hplx
```

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

```
> python3 -m hmxlabs.hplx --help

usage: python3 -m hmxlabs.hplx [-h] [--output-jsonlines | --no-output-jsonlines] [--cpu-count CPU_COUNT] [--available-memory AVAILABLE_MEMORY]
                   {parse-results,gen-input-theoretical-best,gen-input-calc-optimal,calc-optimal,run-theoretical-optimal} ...
positional arguments:
  {parse-results,gen-input-theoretical-best,gen-input-calc-optimal,calc-optimal,run-theoretical-optimal}
    parse-results       Parse HPLinpack output files
    gen-input-theoretical-best
                        Generate theoretical best HPLinpack input files
    gen-input-calc-optimal
                        Generate HPLinpack input file to experimentally determine optimal parameters
    calc-optimal        Find optimal HPLinpack parameters via exectution
    run-theoretical-optimal
                        Use theoretical best input parameters to run HPL

options:
  -h, --help            show this help message and exit
  --output-jsonlines, --no-output-jsonlines
                        Output results in JSON lines format (default: False)
  --cpu-count CPU_COUNT
                        The number of physical cores to use in the test. Default is the number of physical cores on the machine
  --available-memory AVAILABLE_MEMORY
                        The total available memory in bytes. Default is the total available memory on the machine

(C) HMx Labs Limited 2024. All Rights Reserved.

```

### Global Options
There are a small number of options that apply globally across all subcommands. These must be specified
before the subcommand.

```
  -h, --help            show this help message and exit
  --output-jsonlines, --no-output-jsonlines
                        Output results in JSON lines format (default: False)
  --cpu-count CPU_COUNT
                        The number of physical cores to use in the test. Default is the number of physical cores on the machine
  --available-memory AVAILABLE_MEMORY
                        The total available memory in bytes. Default is the total available memory on the machine
  --use-smt, --no-use-smt
                        Use SMT (Hyperthreading) if available when counting CPUs. Default is False (default: False)
```

Specifying `--cpu-count` will override any automatic detection of the number of CPUs and use the specified values

Specifying `--available-memory` will override any automatic detection of the available memory and use the specified value

Specifying `--use-smt` will count the number of CPUs including SMT (Hyperthreading) if available
Note that if using SMT then the `--use-hwthread-cpus` must be passed to `mpirun` also.


Specifying `--output-jsonlines` will output the results in JSON lines format. If not specified the results will be output in CSV format.

### Reading Results from HPL Output
The `hplx` tool can read the results from the HPL output file and output them in CSV or JSON lines format.

```
python3 -m hmxlabs.hplx  parse-results --input-file HPL.out --output-file results [--output-jsonlines]
```

This will parse a file named `HPL.out` and output the results in a file named `results`. 
If the `--output-jsonlines` flag is provided, the results will be output in JSON lines format else
CSV format. The results file will have the corresponding extension `.csv` or `.jsonl`.

The ouput to stdout will also provide the highest gflops achieved.

```
> python3 -m hmxlabs.hplx parse-results --help

usage: python3 -m hmxlabs.hplx parse-results [-h] --input-file INPUT_FILE [--output-file OUTPUT_FILE]

options:
  -h, --help            show this help message and exit
  --input-file INPUT_FILE
                        The HPL results file to process
  --output-file OUTPUT_FILE
                        The output file to write the processed results to. If not specified no output file is written

```

### Generating Theoretical Best HPL.dat File
The `hplx` tool can generate a `HPL.dat` file with the theoretically best parameters for the HPL benchmark.

```
python3 -m hmxlabs.hplx gen-input-theoretical-best --output-file HPL.dat
```

This will generate a `HPL.dat` file with the theoretically best parameters for the HPL benchmark in
the working directory. Any existing `HPL.dat` file will be overwritten.

```
python3 -m hmxlabs.hplx gen-input-theoretical-best --help
usage: python3 -m hmxlabs.hplx gen-input-theoretical-best [-h] [--filename OUTPUT_FILE] [--results-file RESULTS_FILE] [--min-prob-sizes MIN_PROB_SIZES] [--max-prob-sizes MAX_PROB_SIZES] [--prob-sizes-step PROB_SIZES_STEP]

options:
  -h, --help            show this help message and exit
  --filename OUTPUT_FILE
                        The output file to write the generated input to. Default is HPL.dat
  --results-file RESULTS_FILE
                        The results file to write the generated input to. HPL results are written to this stdout
  --min-prob-sizes MIN_PROB_SIZES
                        The minimum problem size (N) to evaluate for use. Default is 1000
  --max-prob-sizes MAX_PROB_SIZES
                        The maximum problem size (N) to evaluate for use. Default is 1000000
  --prob-sizes-step PROB_SIZES_STEP
                        The maximum problem size (N) step size for theoretical evaluation. Default is 5000
```

### Generating HPL.dat File to Experimentally Determine Optimal Parameters
WARNING: This will potentially generate a very large number of permutations for HPL to run some of
of which may be with large problem sizes (N) and will take a long time to run. 

```
python3 -m hmxlabs.hplx gen-input-calc-optimal
```

This will generate a `HPL.dat` file with the theoretically best parameters for the HPL benchmark in
the working directory. Any existing `HPL.dat` file will be overwritten.

```
python3 -m hmxlabs.hplx gen-input-calc-optimal --help
usage: python3 -m hmxlabs.hplx gen-input-calc-optimal [-h] [--filename OUTPUT_FILE] [--results-file RESULTS_FILE] [--num-prob-sizes N_PROB_SIZES] [--num-block-sizes N_BLOCK_SIZES]

options:
  -h, --help            show this help message and exit
  --filename OUTPUT_FILE
                        The output file to write the generated input to. Default is HPL.dat
  --results-file RESULTS_FILE
                        The results file to write the generated input to. HPL results are written to this stdout
  --num-prob-sizes N_PROB_SIZES
                        The number of problem sizes (N) to use in the test. Default is 10
  --num-block-sizes N_BLOCK_SIZES
                        The number of block sizes (NB) to use in the test. Default is 10
```

### Running HPL with Theoretical Best Parameters
This will generate a `HPL.dat` file with the theoretically best parameters (as per above)
but will then also invoke the HPL benchmark using that file. Upon completion it will parse
the results, print the gflops to stdout and write the results to a the file 'theoretical-max.jsonl'
or 'theoretical-max.csv' depending on the output format.

```
python3 -m hmxlabs.hplx run-theoretical-optimal
```

The command to execute the HPL benchmark must be specified in the environment variable `HPL_EXEC`.
For example

```
export HPL_EXEC='mpirun -n $CPUS$ --map-by l3cache --mca btl self,vader xhpl'
```

The value of `$CPU` will be replaced by the number of physical cores on the machine or the
value specified by the `--cpu-count` option. Please note that if a full path to the executable
is not specified then the executable must be in the path or in the working directory.

The results will be written to two files, `hplx-highest-gflops` which contains a single record.

As with the generation command above it is possible to tweak the input parameters to the 
algorithm to generate the `HPL.dat` file.

```
python3 -m hmxlabs.hplx run-theoretical-optimal --help
usage: python3 -m hmxlabs.hplx run-theoretical-optimal [-h] [--min-prob-sizes MIN_PROB_SIZES] [--max-prob-sizes MAX_PROB_SIZES] [--prob-sizes-step PROB_SIZES_STEP]

options:
  -h, --help            show this help message and exit
  --min-prob-sizes MIN_PROB_SIZES
                        The minimum problem size (N) to evaluate for use. Default is 1000
  --max-prob-sizes MAX_PROB_SIZES
                        The maximum problem size (N) to evaluate for use. Default is 1000000
  --prob-sizes-step PROB_SIZES_STEP
                        The maximum problem size (N) step size for theoretical evaluation. Default is 5000
```

### Running HPL to Experimentally Determine Optimal Parameters
This is similar to running the option above to generate the `HPL.dat` file to experimentally
determine the highest performance configuration. However, this will attempt to reduce the total
runtime but attempting to first determine the ideal process grid with a small problem size (N)
and then use only this process grid to determine the best problem size (N) and block size (NB).

```python3 -m hmxlabs.hplx calc-optimal```

The command to execute the HPL benchmark must be specified in the environment variable `HPL_EXEC`.
For example

```
export HPL_EXEC='mpirun -n $CPUS$ --map-by l3cache --mca btl self,vader xhpl'
```

The value of `$CPU` will be replaced by the number of physical cores on the machine or the
value specified by the `--cpu-count` option. Please note that if a full path to the executable
is not specified then the executable must be in the path or in the working directory.

The results will be written to two files, `hplx-highest-gflops` which contains a single record
with the highest gflops and `hplx-all` which contains all the permutations.
The files will be either in JSON lines or CSV format depending on the output format selected and
will have the corresponding file extension.

The total number of problem size and block size permutations can be adjusted as with the pure
generation command above.

```
python3 -m hmxlabs.hplx calc-optimal --help
usage: python3 -m hmxlabs.hplx calc-optimal [-h] [--num-prob-sizes N_PROB_SIZES] [--num-block-sizes N_BLOCK_SIZES]

options:
  -h, --help            show this help message and exit
  --num-prob-sizes N_PROB_SIZES
                        The number of problem sizes (N) to use in the test. Default is 10
  --num-block-sizes N_BLOCK_SIZES
                        The number of block sizes (NB) to use in the test. Default is 10
```

### Running Experimental and Theoretical Together
It is possible to run the experimental and theoretical runs together. This will first generate
the theoretically best `HPL.dat` file and then run the HPL benchmark using that file. Upon completion
it will run the experimental runs. It is equivalent to running the two commands consecutively but
it will produce a single set of output.

```python3 -m hmxlabs.hplx run-all```

The command to execute the HPL benchmark must be specified in the environment variable `HPL_EXEC`.
For example

```
export HPL_EXEC='mpirun -n $CPUS$ --map-by l3cache --mca btl self,vader xhpl'
```

All other command line options are as per the two commands above.

```
python -m hmxlabs.hplx run-all --help
usage: python -m hmxlabs.hplx run-all [-h] [--num-prob-sizes N_PROB_SIZES] [--num-block-sizes N_BLOCK_SIZES] [--min-prob-sizes MIN_PROB_SIZES] [--max-prob-sizes MAX_PROB_SIZES] [--prob-sizes-step PROB_SIZES_STEP]

options:
  -h, --help            show this help message and exit
  --num-prob-sizes N_PROB_SIZES
                        The number of problem sizes (N) to use experimentally. Default is 10
  --num-block-sizes N_BLOCK_SIZES
                        The number of block sizes (NB) to use experimentally. Default is 10
  --min-prob-sizes MIN_PROB_SIZES
                        The minimum problem size (N) to determine the theoretical max Default is 1000
  --max-prob-sizes MAX_PROB_SIZES
                        The maximum problem size (N) to determine the theoretical max. Default is 1000000
  --prob-sizes-step PROB_SIZES_STEP
                        The problem size (N) step size for to determine the theoretical max. Default is 5000
```
