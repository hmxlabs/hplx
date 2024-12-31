import math
import json
from pathlib import Path


class HplResult:
    JSON_KEY_N = "n"
    JSON_KEY_NB = "nb"
    JSON_KEY_P = "p"
    JSON_KEY_Q = "q"
    JSON_KEY_TIME = "time"
    JSON_KEY_GFLOPS = "gflops"
    JSON_KEY_CPUS = "cpu_count"
    JSON_KEY_TYPE = "type"


    def __init__(self) -> None:
        self._n = math.nan
        self._nb = math.nan
        self._p = math.nan
        self._q = math.nan
        self._time = math.nan
        self._gflops = math.nan
        self._cpu_count = math.nan
        self._type = None

    @property
    def n(self):
        return self._n

    @n.setter
    def n(self, n):
        self._n = n

    @property
    def nb(self):
        return self._nb

    @nb.setter
    def nb(self, nb):
        self._nb = nb

    @property
    def p(self):
        return self._p

    @p.setter
    def p(self, p):
        self._p = p

    @property
    def q(self):
        return self._q

    @q.setter
    def q(self, q):
        self._q = q

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, time):
        self._time = time

    @property
    def gflops(self):
        return self._gflops

    @gflops.setter
    def gflops(self, gflops):
        self._gflops = gflops

    @property
    def cpu_count(self):
        return self._cpu_count

    @cpu_count.setter
    def cpu_count(self, cpu_count):
        self._cpu_count = cpu_count

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        self._type = type

    def __str__(self) -> str:
        return f"n={self.n}, nb={self.nb}, p={self.p}, q={self.q}, time={self.time}, gflops={self.gflops}, cpu_count={self.cpu_count}, type={self.type}"

    def to_dict(self):
        ret_dict = {
            HplResult.JSON_KEY_N: self.n,
            HplResult.JSON_KEY_NB: self.nb,
            HplResult.JSON_KEY_P: self.p,
            HplResult.JSON_KEY_Q: self.q,
            HplResult.JSON_KEY_TIME: self.time,
            HplResult.JSON_KEY_GFLOPS: self.gflops,
        }

        if not math.isnan(self.cpu_count):
            ret_dict[HplResult.JSON_KEY_CPUS] = self.cpu_count

        if self.type:
            ret_dict[HplResult.JSON_KEY_TYPE] = self.type

        return ret_dict

    def to_csv(self):
        return f"{self.n},{self.nb},{self.p},{self.q},{self.time},{self.gflops},{self.cpu_count},{self.type}"

    @staticmethod
    def csv_header():
        return f"{HplResult.JSON_KEY_N},{HplResult.JSON_KEY_NB},{HplResult.JSON_KEY_P},{HplResult.JSON_KEY_Q},{HplResult.JSON_KEY_TIME},{HplResult.JSON_KEY_GFLOPS}, {HplResult.JSON_KEY_CPUS}, {HplResult.JSON_KEY_TYPE}"

    def update(self, data: dict):
        self.n = data[HplResult.JSON_KEY_N]
        self.nb = data[HplResult.JSON_KEY_NB]
        self.p = data[HplResult.JSON_KEY_P]
        self.q = data[HplResult.JSON_KEY_Q]
        self.time = data[HplResult.JSON_KEY_TIME]
        self.gflops = data[HplResult.JSON_KEY_GFLOPS]

    def from_hpl_output(self, line: str):
        parts = line.split()
        self.n = int(parts[1])
        self.nb = int(parts[2])
        self.p = int(parts[3])
        self.q = int(parts[4])
        self.time = float(parts[5])
        self.gflops = float(parts[6])

    def to_json(self):
        return json.dumps(self.to_dict())

    @staticmethod
    def highest_gflops(results: list["HplResult"]) -> "HplResult":
        highest = None
        for result in results:
            if highest is None or result.gflops > highest.gflops:
                highest = result

        return highest


class HplResultsFile:
    @staticmethod
    def write_results_to_csv(file_path: str, results: list[HplResult]):
        if not file_path:
            raise ValueError("file_path cannot be None or empty")

        if not results:
            raise ValueError("results cannot be None or empty")

        output_file = Path(file_path)
        with open(output_file, "w") as file:
            file.write(HplResult.csv_header())
            file.write("\n")
            for result in results:
                file.write(result.to_csv())
                file.write("\n")

    @staticmethod
    def write_results_to_json(file_path: str, results: list[HplResult]):
        if not file_path:
            raise ValueError("file_path cannot be None or empty")

        if not results:
            raise ValueError("results cannot be None or empty")

        output_file = Path(file_path)
        with open(output_file, "w") as file:
            for result in results:
                file.write(result.to_json())
                file.write("\n")


    @staticmethod
    def read_result_file(file_path: str) -> list[HplResult]:
        if not file_path:
            raise ValueError("file_path cannot be None or empty")

        input_file = Path(file_path)
        if not input_file.exists():
            raise FileNotFoundError(f"File {file_path} does not exist")

        if not input_file.is_file():
            raise ValueError(f"{file_path} is not a file")

        results:list[HplResult] = []
        hit_header = False
        hit_seperator = False
        with open(file_path, "r") as file:
            # Frankly we don't care about most of the lines in hpl.out
            # Ww're looking for a pair of line as follows:
            # T/V                N    NB     P     Q               Time                 Gflops
            # --------------------------------------------------------------------------------
            # The next line is the actual result
            for line in file:
                if line.startswith("T/V                N    NB     P     Q               Time                 Gflops"):
                    hit_header = True
                    continue
                if line.startswith("--------------------------"):
                    hit_seperator = True
                    continue

                if hit_header and hit_seperator:
                    result = HplResult()
                    result.from_hpl_output(line)
                    results.append(result)
                    hit_header = False
                    hit_seperator = False

        return results