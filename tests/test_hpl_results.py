import unittest
import json
from hmxlabs.hplx.hpl_results import HplResult, HplResultsFile


class TestHplResults(unittest.TestCase):

    def test_to_json(self) -> None:
        self.maxDiff = None
        hpl_results = HplResult()
        hpl_results.n = 1000
        hpl_results.nb = 100
        hpl_results.p = 1
        hpl_results.q = 1
        hpl_results.time = 100
        hpl_results.gflops = 100

        hpl_json = hpl_results.to_json()
        expected = json.dumps({
            "n": 1000,
            "nb": 100,
            "p": 1,
            "q": 1,
            "time": 100,
            "gflops": 100
        })

        self.assertEqual(expected, hpl_json, "The HplResults JSON output did not match the expected value")

        hpl_dict = json.loads(hpl_json)
        new_hpl = HplResult()
        new_hpl.update(hpl_dict)
        new_json = new_hpl.to_json()
        self.assertEqual(hpl_json, new_json, "JSON from deserialised HplResults and created HplResults is not equal")

    def test_to_csv(self) -> None:
        hpl_results = HplResult()
        hpl_results.n = 1000
        hpl_results.nb = 100
        hpl_results.p = 2
        hpl_results.q = 4
        hpl_results.time = 111
        hpl_results.gflops = 1123
        hpl_results.cpu_count = 4
        hpl_results.type = "test"

        hpl_csv = hpl_results.to_csv()
        expected = "1000,100,2,4,111,1123,4,test"

        self.assertEqual(expected, hpl_csv, "The HplResults CSV output did not match the expected value")

    def test_read_result_line(self) -> None:
        hpl_results = HplResult()
        # The below line is copy/pasted from a termina output of HPL
        input_line = "WR11C2R4       20000    64     2     4             179.72             2.9679e+01"
        hpl_results.from_hpl_output(input_line)
        self.assertEqual(20000, hpl_results.n)
        self.assertEqual(64, hpl_results.nb)
        self.assertEqual(2, hpl_results.p)
        self.assertEqual(4, hpl_results.q)
        self.assertEqual(179.72, hpl_results.time)
        self.assertEqual(29.679, hpl_results.gflops)


    def test_read_sample_file(self) -> None:
        hpL_results = HplResultsFile.read_result_file("./data/HPL.out")
        self.assertEqual(40, len(hpL_results))


    def test_write_results_to_csv(self) -> None:
        hpL_results = HplResultsFile.read_result_file("./data/HPL.out")
        test_file = "./data/output/hplx.out.csv"
        HplResultsFile.write_results_to_csv(test_file, hpL_results)
        with open("./data/HPL.csv","r") as file:
            expected_csv = file.read()

        with open(test_file,"r") as file:
            generated_csv = file.read()

        self.assertEqual(expected_csv, generated_csv, "The generated CSV file did not match the expected CSV file")


