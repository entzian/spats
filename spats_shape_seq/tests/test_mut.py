import unittest

from spats_shape_seq import Spats
from spats_shape_seq.pair import Pair

# [ id, r1, r2, end, site, muts ]
cases = [

    # basic test case
    [ '89', 'TTCACAACAAGAATTGGGACAACTCCAGTGAAAAGTTCTTCTCCTTTGCTCATCATTAACCTCCTGAATCACTAT', 'GGACAAGCAATGCTTACCTTGATGTTGAACTTTTGAATAGTGATTCAGGAGGTTAATGATGAGCAAAGGAGAAGA', 107, 0, [ 16 ] ],

    # basic test case
    [ '961', 'AGATCAACAAGAATTAGGACAACTCCAGTGAAAAGTTCTTCTCCTTTGCTCATCATTAACCTCCTGAATCACTAT', 'ACAAGCAATGCTTGCCTTGATGTTGAACTTTTGAATAGTGATTCAGGAGGTTAATGATGAGCAAAGGAGAAGAAC', 107, 2, [ 96 ] ],

    # r1/r2 nearly overlap
    [ '535', 'AAATCAACAAGAATTGGGACAACTCCAGTGAAAAGTTCTTCTCCTTTGCTCATCATTAACCTCCTGAATCACTAT', 'AATAGTGATTCAGGAGGTTAATGATGAGCAAAGGAGAAGAACTTTTCACTGGAGTTGTCCCAATTCTTGTTGATT', 107, 35, None ],

    # r1/r2 overlap
    [ '793', 'TCCGCAACAAGAATTGGGACAACTCCAGTGAAAAGTTCTTCTCCTTTGCTCATCATTAACCTCCTGAATCACTAT', 'ATAGTGATTCAGGAGGTTAATGATGAGCAAAGGAGAAGAACTTTTCACTGGAGTTGTCCCAATTCTTGTTGCGGA', 107, 36, None ],

    # r1 mutation case -- disagree on overlap
    [ '216', 'TCCACAACAAGAATTGGGACAACTCCAGTGAAAAGTTCTTCTCATTTGCTCATCATTAACCTCCTGAATCACTAT', 'GGACAAGCAATGCTTGCCTTGATGTTGAACTTTTGAATAGTGATTCAGGAGGTTAATGATGAGCAAAGGAGAAGA', 107, None, None ],

    # r1 mutation case
    [ '216*', 'TCCACAACAAGAATTGGGACAACTCCAGTGAAATGTTCTTCTCCTTTGCTCATCATTAACCTCCTGAATCACTAT', 'GGACAAGCAATGCTTGCCTTGATGTTGAACTTTTGAATAGTGATTCAGGAGGTTAATGATGAGCAAAGGAGAAGA', 107, 0, [ 78 ] ],

    # r1 mutation with adapter trim
    [ '377', 'GGGTCAACAAGAATTGGGACAACTCCAGTGAAAAGTTCTTCTCCTTTGCTCATCATTTAGATCGGAAGAGCACAC', 'AAATGATGAGCAAAGGAGAAGAACTTTTCACTGGAGTTGTCCCAATTCTTGTTGACCCAGATCGGAAGAGCGTCG', 107, 53, [ 54] ],

    # r1 mutation on edge with trim
    [ '978', 'GAACCAACAAGAATTGGGACAACTCCAGTGAAAGGTTCTTCTCCTTTGCTCATCATTAACCTCCTGAAGATCGGA', 'TCAGGAGGTTAATGATGAGCAAAGGAGAAGAACCTTTCACTGGAGTTGTCCCAATTCTTGTTGGTTCAGATCGGA', 107, 44, [ 78 ] ],

    # trim/mut edge case
    [ '159712', 'CCTACAACAAGAATTGGGACAACTCCAGTGAGAAGTTCTTCTCCTTTGCTCATCATTAAGATCGGAAGAGCACAC', 'TAATGATGAGCAAAGGAGAAGAACTTCTCACTGGAGTTGTCCCAATTCTTGTTGTAGGAGATCGGAAGAGCGTCG', 107, 53, [ 80 ] ],

    # trim/mut edge case (but they disagree on overlap)
    [ '35123*', 'CTTGCAACAAGAATTGGGACAACTCCAGTGAAAAGTTCTTCTCCTTTGCTCATCTTTAACCTCCTGAATCACTAA', 'TAGTGATTCAGGAGGTTAATGATGAGCAAAGGAGAAGAACTTTTCACTGGAGTTGTCCCAATTCTTGTTGCAAGA', 107, None, None ],

    # trim/mut edge case
    [ '35123', 'CTTGCAACAAGAATTGGGACAACTCCAGTGAAAAGTTCTTCTCCTTTGCTCATCATTAACCTCCTGAATCACTAA', 'TAGTGATTCAGGAGGTTAATGATGAGCAAAGGAGAAGAACTTTTCACTGGAGTTGTCCCAATTCTTGTTGCAAGA', 107, 37, None ],



    # basic quality check test case
    [ '89', 'TTCACAACAAGAATTGGGACAACTCCAGTGAAAAGTTCTTCTCCTTTGCTCATCATTAACCTCCTGAATCACTAT', 'GGACAAGCAATGCTTACCTTGATGTTGAACTTTTGAATAGTGATTCAGGAGGTTAATGATGAGCAAAGGAGAAGA', 107, 0, [ 16 ], 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' ],

    # basic quality check test case
    [ '961', 'AGATCAACAAGAATTAGGACAACTCCAGTGAAAAGTTCTTCTCCTTTGCTCATCATTAACCTCCTGAATCACTAT', 'ACAAGCAATGCTTGCCTTGATGTTGAACTTTTGAATAGTGATTCAGGAGGTTAATGATGAGCAAAGGAGAAGAAC', 107, 2, [ 96 ], 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' ],

    # r1 mutation quality check case
    [ '216', 'TCCACAACAAGAATTGGGACAACTCCAGTGAAATGTTCTTCTCCTTTGCTCATCATTAACCTCCTGAATCACTAT', 'GGACAAGCAATGCTTGCCTTGATGTTGAACTTTTGAATAGTGATTCAGGAGGTTAATGATGAGCAAAGGAGAAGA', 107, 0, [ 78 ], 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' ],

    # basic quality check test case
    [ '89', 'TTCACAACAAGAATTGGGACAACTCCAGTGAAAAGTTCTTCTCCTTTGCTCATCATTAACCTCCTGAATCACTAT', 'GGACAAGCAATGCTTACCTTGATGTTGAACTTTTGAATAGTGATTCAGGAGGTTAATGATGAGCAAAGGAGAAGA', 107, 0, [], '(((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((', '(((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((' ],

    # basic quality check test case
    [ '961', 'AGATCAACAAGAATTAGGACAACTCCAGTGAAAAGTTCTTCTCCTTTGCTCATCATTAACCTCCTGAATCACTAT', 'ACAAGCAATGCTTGCCTTGATGTTGAACTTTTGAATAGTGATTCAGGAGGTTAATGATGAGCAAAGGAGAAGAAC', 107, 2, [], '(((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((', '(((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((' ],

    # r1 mutation quality check case
    [ '216', 'TCCACAACAAGAATTGGGACAACTCCAGTGAAATGTTCTTCTCCTTTGCTCATCATTAACCTCCTGAATCACTAT', 'GGACAAGCAATGCTTGCCTTGATGTTGAACTTTTGAATAGTGATTCAGGAGGTTAATGATGAGCAAAGGAGAAGA', 107, 0, [], '(((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((', '(((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((' ],

    # basic quality check test case
    [ '89', 'TTCACAACAAGAATTGGGACAACTCCAGTGAAAAGTTCTTCTCCTTTGCTCATCATTAACCTCCTGAATCACTAT', 'GGACAAGCAATGCTTACCTTGATGTTGAACTTTTGAATAGTGATTCAGGAGGTTAATGATGAGCAAAGGAGAAGA', 107, 0, [ ], 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', 'AAAAAAAAAAAAAAA!AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' ],

    # basic quality check test case
    [ '961', 'AGATCAACAAGAATTAGGACAACTCCAGTGAAAAGTTCTTCTCCTTTGCTCATCATTAACCTCCTGAATCACTAT', 'ACAAGCAATGCTTGCCTTGATGTTGAACTTTTGAATAGTGATTCAGGAGGTTAATGATGAGCAAAGGAGAAGAAC', 107, 2, [ ], 'AAAAAAAAAAAAAAA!AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' ],

    # basic quality check test case
    [ '89', 'TTCACAACAAGAATTGGGACAACTCCAGTGAAAAGTTCTTCTCCTTTGCTCATCATTAACCTCCTGAATCACTAT', 'GGACAAGCAATGCTTACCTTGATGTTGAACTTTTGAATAGTGATTCAGGAGGTTAATGATGAGCAAAGGAGAAGA', 107, 0, [ 16 ], 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', 'AAAAAAAAAAAAAAAA!AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' ],

    # basic quality check test case
    [ '961', 'AGATCAACAAGAATTAGGACAACTCCAGTGAAAAGTTCTTCTCCTTTGCTCATCATTAACCTCCTGAATCACTAT', 'ACAAGCAATGCTTGCCTTGATGTTGAACTTTTGAATAGTGATTCAGGAGGTTAATGATGAGCAAAGGAGAAGAAC', 107, 2, [ 96 ], 'AAAAAAAAAAAAAAAA!AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' ],

]


cotrans_cases = [

    # indexing convention, xref https://trello.com/c/2qIGo9ZR/201-stop-map-mutation-indexing-convention
    [ 'x1', 'TTCAGTCCTTGGTGCCCGAGTCAGCCAGCTACATCCCGGCACACGCGTCATCTGCCTTGGCTGCTTCCTTCCGGA', 'AGGTCAGATCCGGAAGGAAGCAGCCAAGGCAGATGACGCGTGTGCCGGGATGTAGCTGGCTGACTCGGGCACCAA', 103, 44, [52] ],

    # R1/R2 disagree on overlap; similar to x3, may need to factor in quality at some point
    [ 'x2', 'AGGCGTCCTTGGTGCCCGAGTCAGCCTTGGCTGCTTCCTTCCGGACCTGACCTGGTAAACAGAGTAGCGTTGCGG', 'ATCGGGGGCTCTGTTGGTTCCCCCGCAACGCTACTCTGTTTACCAGGTCAGGTCCGGAAGGAAGCAGCCAAGTCT', None, None, None, ],

    # note: on this one, the quality score on R1 vs. R2 indicates that mut 73 really is a misread on R2, so this case may change in the future (to be 88, 0, [88])...
    # for now it should be tossed b/c R1 and R2 disagree where they overlap
    # xref https://trello.com/c/35mBHvPA/197-stop-map-r1-r2-disagree-case
    [ 'x3', 'GAATGTCCTTGGTGCCCGAGTCAGGACACGCGTCATCTGCCTTGGCTGCTTCCTTCCGGACCTGACCTGGTAAAC', 'ATCGGGGGCTCTGTTGGTTCCCCCGCAACGCTACTCTGTTTACCAGGTCAGGTCCGGAAGGAAGCAGCCAAGTCA', None, None, None ],

    [ 'x4', 'GAGCGTCCTTGGTGCCCGAGTCAGATGCCGACCCGGGTGGGGGCCCTGCCAGCTACATCCCGGCACACGCGTCAT', 'TAGGTCAGGTCCGGAAGGAAGCAGCCAAGGCAGATGACGCGTGTGCCGGGATGTAGCTGGCAGGGCCCCCACCCG', 127, 43, [44] ],

    [ 'x5', 'GAATGTCCTTGGTGCCCGAGTCAGTCCTTGGTGCCCGAGTCAGTCCTTGGTTCCCGAGTCACTCCTTTGTTCCCC', 'AGGACTGACTCGGGCACCAAGGACTTTCTCGTTCACCTATTTCTTTCTCTTCCCCCTTTTTCTTTCTCTTTCTCC', None, None, None ],

    # this one is slightly ambiguous due to mutation at the site. the code reports it the same as the rest for consistency, 
    # but it's counted separately in counters for further analysis
    # xref https://trello.com/c/FulYfVjT/200-stop-map-mutation-on-edge-case
    ['18112', 'AAATGTCCTTGGTGCCCGAGTCAGATCTGCCTTAAGATCGGAAGAGCACACGTCTGAACTCCAGTCACATCACGA', 'TAAGGCAGATCTGACTCGGGCACCAAGGACATTTAGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGTAGATCTCG', 78, 68, [69] ],

    # relatively short target match with one bp toggle
    [ '11555', 'CTCAGTCCTTGGTGCCCGAGTCAGTGAGCTAGATCGGAAGAGCACACGTCTGAACTCCAGTCACATCACGATCTC', 'AGCTCACTGACTCGGGCACCAAGGACTGAGAGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGTAGATCTCGGTGG', 50, 44, [47] ],

    # matches more than one site-end-toggle combination in the target
    # https://trello.com/c/fxS3L7aM/202-stop-map-ambiguous-match-minimum-target-match-length
    [ '16610', 'AAGCGTCCTTGGTGCCCGAGTCAGTGGAGGTAGATCGGAAGAGCACACGTCTGAACTCCAGTCACATCACGATCT', 'ACCTCCACTGACTCGGGCACCAAGGACGCTTAGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGTAGATCTCGGTG', None, None, None ],

    # one mutation on R1 and one on R2, nonoverlapping. should not match due to multiple target errors
    [ '76514', 'AAGCGTCCTTGGTGCCCGAGTCAGTGGCACACGCGTCATCTGCCTTGGCTGCTTCCTTCCGGACCTGACCTGGTA', 'AGGGGGCTCTGTTGGTTCCCCCGCAACGCTACTCTGTTTACCAGGTCAGGTCCGGAAGGAAGCAGCCAAGGCAGA', None, None, None ],

    # corner case for find_partial, short target match
    [ '138391', 'TCCGGTCCTTGGTGCCCGAGTCAGATGTAGATCGGAAGAGCACACGTCTGAACTCCAGTCACATCACGATCTCGT', 'ACATCTGACTCGGGCACCAAGGACCGGAAGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGTAGATCTCGGTGGTC', None, None, None ],

    # extra BP on the end of R1, should fail
    [ '268392', 'TTTAAGTCCTTGGTGCCCGAGTCAGGTCATCTGCCTTGGCTGCTTCCTTCCGGACCTGACCTGGTAAACAGAGTA', 'TACTCTGTTTACCAGGTCAGGTCCGGAAGGAAGCAGCCAAGGCAGATGACCTGACTCGGGCACCAAGGACTTAAA', None, None, None ],


]


# [ id, r1, r2, end, site, muts ]
multiple_mut_cases = [

    [ '89-2', 'TTCACAACAAGAATTGGGACAACTCCAGTGAAAAGTTCTTCTCCTTTGCTCATCATTAACCTCCTGAATCACTAT', 'GCACAAGCAATGCTTACCTTGATGTTGAACTTTTGAATAGTGATTCAGGAGGTTAATGATGAGCAAAGGAGAAGA', 107, 0, [ 2, 16 ] ],

    [ '89-3', 'TTCACAACAAGAATTGGGACAACTCCAGTGAAAAGTTCTTCTCCTTTGCTCATCATTAACCTCCTGAATCACTAT', 'GTACTAGCAATGCTTACCTTGATGTTGAACTTTTGAATAGTGATTCAGGAGGTTAATGATGAGCAAAGGAGAAGA', 107, 0, [ 2, 5, 16 ] ],

    [ '89-4', 'TTCACAACAAGAATTGGGACAACTCCAGTGAAAAGTTCTTCTCCTTTGCTCATCATTAACCTCCTGAATCACTAT', 'GTACTAGCAATACTTACCTTGATGTTGAACTTTTGAATAGTGATTCAGGAGGTTAATGATGAGCAAAGGAGAAGA', 107, 0, [ 2, 5, 12, 16 ] ],

    [ '89-5', 'TTCACAACAAGAATTGGGACAACTCCAGTGAAAAGTTCTTCTCCTTTGCTCATCATTAACCTCCTGAATCACTAT', 'GTACTAGCCATACTTACCTTGATGTTGAACTTTTGAATAGTGATTCAGGAGGTTAATGATGAGCAAAGGAGAAGA', 107, 0, [ 2, 5, 9, 12,16 ] ],

    [ '89-6', 'TTCACAACAAGAATTGGGACAACTCCAGTGAAAAGTTCTTCTCCTTTGCTCATCATTAACCTCCTGAATCACTAT', 'GTATTAGCCATACTTACCTTGATGTTGAACTTTTGAATAGTGATTCAGGAGGTTAATGATGAGCAAAGGAGAAGA', None, None, None ],

]

class TestMutPairs(unittest.TestCase):
    
    def setUp(self):
        self.spats = Spats()
        self.spats.run.count_mutations = True
        self.spats.run.mutations_require_quality_score = ord('.') - ord('!')
        self.spats.run.allowed_target_errors = 1
        self.spats.run.ignore_stops_with_mismatched_overlap = True
        self.spats.run.adapter_b = "AGATCGGAAGAGCACACGTCTGAACTCCAGTCACATCACGATCTCGTATGCCGTCTTCTGCTTG"
        self.setup_processor()

    def setup_processor(self):
        self.spats.run.algorithm = "find_partial"
        self.spats.addTargets("test/mut/mut_single.fa")

    def tearDown(self):
        self.spats = None

    def pair_for_case(self, case):
        pair = Pair()
        pair.set_from_data(case[0], case[1], case[2])
        if len(case) > 6:
            pair.r1.quality = case[6]
            pair.r2.quality = case[7]
        else:
            pair.r1.quality = 'K' * len(case[1])
            pair.r2.quality = 'K' * len(case[2])
        return pair

    def run_case(self, case):
        pair = self.pair_for_case(case)
        self.spats.process_pair(pair)
        self.assertEqual(case[4], pair.site, "res={} != {} ({}, {}, {})".format(pair.site, case[4], self.__class__.__name__, case[0], pair.failure))
        if pair.site is not None:
            self.assertEqual(case[3], pair.end, "end={} != {} ({}, {}, {})".format(pair.end, case[3], self.__class__.__name__, case[0], pair.failure))
            self.assertEqual(case[5], sorted(pair.mutations) if pair.mutations else pair.mutations, "muts={} != {} ({}, {}, {})".format(pair.mutations, case[5], self.__class__.__name__, case[0], pair.failure))
        return pair

    def cases(self):
        return cotrans_cases if self.spats.run.cotrans else cases

    def test_pairs(self):
        self.spats.run.pair_length = len(cases[0][1])
        for case in self.cases():
            self.run_case(case)
        print("Ran {} pair->site cases.".format(len(cases)))


class TestMultipleMuts(TestMutPairs):

    def setup_processor(self):
        self.spats.run.algorithm = "find_partial"
        self.spats.run.allowed_target_errors = 5
        self.spats.run._unsafe_skip_error_restrictions = True
        self.spats.addTargets("test/mut/mut_single.fa")

    def cases(self):
        return multiple_mut_cases

    def test_pairs(self):
        for case in multiple_mut_cases:
            self.run_case(case)


class TestMutPairsLookup(TestMutPairs):

    def setup_processor(self):
        self.spats.run.algorithm = "lookup"
        self.spats.addTargets("test/mut/mut_single.fa")


class TestMutPairsCotrans(TestMutPairs):

    def setup_processor(self):
        self.spats.run.cotrans = True
        self.spats.run.cotrans_linker = 'CTGACTCGGGCACCAAGGAC'
        self.spats.run.algorithm = "find_partial"
        self.spats.addTargets("test/mut/mut_cotrans.fa")


class TestMutPairsCotransLookup(TestMutPairs):

    def setup_processor(self):
        self.spats.run.cotrans = True
        self.spats.run.cotrans_linker = 'CTGACTCGGGCACCAAGGAC'
        self.spats.run.algorithm = "lookup"
        self.spats.addTargets("test/mut/mut_cotrans.fa")


# [ id, r1, r2, end, site, muts ]
mismatched_overlap_cases = [

    # was [117], now [] due to checking against high-quality overlap
    [ '81_0', 'GGGCGTCCTTGGTGCCCGAGTCAGCGGTGGGGGCCC', 'GCGTGTGCCGGGATGTAGCTGGCAGGGCCCCCACCT', 137, 81, [  ] ],

    # was [117], now [] due to checking against high-quality overlap
    [ '92_0', 'GGGCGTCCTTGGTGCCCGAGTCAGTGGTGGGGGCCC', 'GATGTAGCTGGCAGGGCCCCCACCGCTGACTCGGGC', 137, 92, [  ] ],

    # was [117], now [] due to checking against high-quality overlap
    [ '116_1', 'CCCGGTCCTTGGTGCCCGAGTCAGTAGATCGGAAGA', 'TCTGACTCGGGCACCAAGGACCGGGAGATCGGAAGA', 137, 116, [  ] ],

]

class TestOverlapMut(TestMutPairs):

    def setup_processor(self):
        self.spats.run.algorithm = "find_partial"
        self.spats.run.allowed_target_errors = 2
        self.spats.run.ignore_stops_with_mismatched_overlap = False
        self.spats.addTargets("test/SRP/SRP.fa")

    def test_pairs(self):
        for case in mismatched_overlap_cases:
            self.run_case(case)

        self.spats.run.ignore_stops_with_mismatched_overlap = True
        for case in mismatched_overlap_cases:
            case[4] = None
            self.run_case(case)


# [ id, r1, r2, end, site, muts ]
prefix_mut_cases = [
    [ 'sah1', 'CTCAGGGCTTTGGGAGCATTATCGTCGGCTTTATCGGCCGAAGCAGGTAGAGGCATAGTTGATGCTCGGACTTTC', 'TGGACCCGATGCCGGACGAAAGTCCGAGCATCAACTATGCCTCTACCTGCTTCGGCCGATAAAGCCGACGATAAT', 87, 0, [ 75 ] ],
]

class TestPrefixMut(TestMutPairs):

    def setup_processor(self):
        self.spats.run.algorithm = "find_partial"
        self.spats.run.count_mutations = True
        self.spats.run.count_edge_mutations = "stop_and_mut"
        self.spats.run.allowed_target_errors = 4
        self.spats.run.mutations_require_quality_score = 30
        self.spats.run.count_left_prefixes = True
        self.spats.run.collapse_left_prefixes = True
        self.spats.run.ignore_stops_with_mismatched_overlap = False
        self.spats.addTargets("test/hairpin/hairpinA_circ.fa")

    def test_pairs(self):
        for case in prefix_mut_cases:
            self.run_case(case)
