import unittest
import cnf
import math

class Bitstring_Convert_Test(unittest.TestCase):
    bitstrings = []
    expected_clauses = []
    def setUp(self):
        self.bitstrings = ["0","1","00","01","10","11"]
        self.expected_clauses = ["-1 0","1 0","-1 -2 0", "-1 2 0", "1 -2 0", "1 2 0"]

    def test(self):
        for i,bs in enumerate(self.bitstrings):
            self.assertEqual(cnf.bitstring_to_clause(bs),self.expected_clauses[i])

class Negation_Test(unittest.TestCase):
    sizes = []
    all_solutions = []
    expected_bitstrings = []
    expected_negations = []
    def setUp(self):
        self.sizes = [1,2,3,3,3]
        self.all_solutions = [[0],[0,1],[1],[0,2],[0,1,2]]
        self.all_expected_negations = [["1"],["10","11"],\
                ["00","10","11"], ["01","11"],["11"]]
        self.numbits = [math.ceil(math.log(N+1,2)) for N in self.sizes]

    def test(self):
        for i in range(len(self.sizes)):
            size = self.sizes[i]
            curr_numbits = self.numbits[i]
            solutions = list(self.all_solutions[i])
            expected_negs = self.all_expected_negations[i]
            expected_solns = [cnf.make_bitstring(soln,curr_numbits) for soln in solutions]
            #print("test:"+str(i))
            actual_negs, actual_solns = cnf.get_negations(size,solutions)

            # compare negations
            print(actual_negs)
            print(expected_negs)

            # tests that actual is a subset of expected
            for i in range(len(actual_negs)):
                self.assertTrue(actual_negs[i] in expected_negs)
            # tests that actual == subset
            self.assertEqual(len(actual_negs),len(expected_negs))

            # compare solutions

            # tests that actual is a subset of expected
            for i in range(len(actual_solns)):
                self.assertTrue(actual_solns[i] in expected_solns)
            # tests that actual == subset
            self.assertEqual(len(actual_solns),len(expected_solns))

def quick_make_test():
    N = 2
    solutions = [0]
    negs, solns = cnf.get_negations(N,solutions)
    print(solns)
    return cnf.make_cnf(N,negs,solns)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
