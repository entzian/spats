
import unittest

from spats_shape_seq.util import reverse_complement, string_find_errors, string_match_errors, align_strings, AlignmentParams, string_find_with_overlap
from spats_shape_seq.mask import longest_match, base_similarity_ind


class TestUtils(unittest.TestCase):
    def test_longest_match(self):
        self.assertEqual((0, 1), longest_match("ATC", (0, 1), "TTATGA", (2, 1)))
        self.assertEqual((0, 0), longest_match("ATC", (0, 1), "TTAGGA", (2, 1)))
        self.assertEqual((0, 2), longest_match("ATC", (0, 1), "TTATCA", (2, 1)))
        self.assertEqual((0, 2), longest_match("GATC", (1, 1), "TTATCA", (2, 1)))
        self.assertEqual((1, 2), longest_match("GATC", (1, 1), "TGATCA", (2, 1)))
    def test_string_match(self):
        self.assertEqual([], string_match_errors("GATC", "GATC"))
        self.assertEqual([2], string_match_errors("GATC", "GACC"))
        self.assertEqual([0], string_match_errors("GATC", "AATC"))
        self.assertEqual([0, 3], string_match_errors("GATC", "CATG"))
        self.assertEqual(range(4), string_match_errors("GATC", "CTAG"))
    def test_reverse_complement(self):
        self.assertEqual("GATC", reverse_complement("GATC"))
        self.assertEqual("CGTCCAA", reverse_complement("TTGGACG"))
        self.assertEqual("CAACAGAGCCCCCGAT", reverse_complement("ATCGGGGGCTCTGTTG"))
        self.assertEqual("GATNC", reverse_complement("GNATC"))
    def test_string_find_with_overlap(self):
        self.assertEqual(13, string_find_with_overlap("GATC", "GTCATCGAGTCATGATCG"))
        self.assertEqual(13, string_find_with_overlap("GATC", "GTCATCGAGTCATGATC"))
        self.assertEqual(13, string_find_with_overlap("GATC", "GTCATCGAGTCATGAT"))
        self.assertEqual(13, string_find_with_overlap("GATC", "GTCATCGAGTCATGA"))
        self.assertEqual(13, string_find_with_overlap("GATC", "GTCATCGAGTCATG"))
        self.assertEqual(-1, string_find_with_overlap("GATC", "GTCATCGAGTCAT"))
        self.assertEqual(-1, string_find_with_overlap("GATCTAGC", "CC"))
        self.assertEqual(2, string_find_with_overlap("GATCTAGC", "CCG"))
        self.assertEqual(2, string_find_with_overlap("GATCTAGC", "CCGA"))
        self.assertEqual(2, string_find_with_overlap("GATCTAGC", "CCGAT"))
        self.assertEqual(2, string_find_with_overlap("GATCTAGC", "CCGATC"))
        self.assertEqual(2, string_find_with_overlap("GATCTAGC", "CCGATCT"))
        self.assertEqual(2, string_find_with_overlap("GATCTAGC", "CCGATCTA"))
        self.assertEqual(2, string_find_with_overlap("GATCTAGC", "CCGATCTAG"))
        self.assertEqual(2, string_find_with_overlap("GATCTAGC", "CCGATCTAGC"))
        self.assertEqual(2, string_find_with_overlap("GATCTAGC", "CCGATCTAGCG"))
    def test_string_find(self):
        m = string_find_errors("TTTT", "TTATAGGCGATGGAGTTCGCCATAAACGCTGCTTAGCTAATGACTCCTACCAGTATCACTACTGGTAGGAGTCTATTTTTTTAGGAGGAAGGATCTATGAGCAAAGGAGAAGAACTTTTCACTGGAGTTGTC", 0, 1)
        self.assertTrue(len(m) == 1  and  len(set(m) & set([75, 76, 77, 78, 115])) == 1)
        m = string_find_errors("TTTT", "TTATAGGCGATGGAGTTCGCCATAAACGCTGCTTAGCTAATGACTCCTACCAGTATCACTACTGGTAGGAGTCTATTTTTTTAGGAGGAAGGATCTATGAGCAAAGGAGAAGAACTTTTCACTGGAGTTGTC", 0, 4)
        self.assertTrue(len(m) == 4  and  len(set(m) & set([75, 76, 77, 78, 115])) == 4)
        m = string_find_errors("TTTT", "TTATAGGCGATGGAGTTCGCCATAAACGCTGCTTAGCTAATGACTCCTACCAGTATCACTACTGGTAGGAGTCTATTTTTTTAGGAGGAAGGATCTATGAGCAAAGGAGAAGAACTTTTCACTGGAGTTGTC", 0, 6)
        self.assertTrue(len(m) == 5  and  len(set(m) & set([75, 76, 77, 78, 115])) == 5)

        m = string_find_errors("ACAT", "ATCGGGGGCTCTGTTGGTTCCCCCGCAACGCTACTCTGTTTACCAGGTCAGGTCCGGAAGGAAGCAGCCAAGGCAGATGACGCGTGTGCCGGGATGTAGCTGGCAGGGCCCCCACCCGGGTCGGCATGGCATCTCCACCTCCTCGCGGT", 1, 1)
        self.assertTrue(len(m) == 1  and  len(set(m) & set([74, 123, 128, 136])) == 1)
        m = string_find_errors("ACAT", "ATCGGGGGCTCTGTTGGTTCCCCCGCAACGCTACTCTGTTTACCAGGTCAGGTCCGGAAGGAAGCAGCCAAGGCAGATGACGCGTGTGCCGGGATGTAGCTGGCAGGGCCCCCACCCGGGTCGGCATGGCATCTCCACCTCCTCGCGGT", 1, 3)
        self.assertTrue(len(m) == 3  and  len(set(m) & set([74, 123, 128, 136])) == 3)
        m = string_find_errors("ACAT", "ATCGGGGGCTCTGTTGGTTCCCCCGCAACGCTACTCTGTTTACCAGGTCAGGTCCGGAAGGAAGCAGCCAAGGCAGATGACGCGTGTGCCGGGATGTAGCTGGCAGGGCCCCCACCCGGGTCGGCATGGCATCTCCACCTCCTCGCGGT", 1, 4)
        self.assertTrue(len(m) == 4  and  len(set(m) & set([74, 123, 128, 136])) == 4)

        m = string_find_errors("GCAT", "AAAACCCCGGGGTTTTATATACGTCAGCCC", 2, 1)
        self.assertTrue(len(m) == 1  and  len(set(m) & set([9, 10, 11, 14, 16, 20, 23, 26])) == 1)
        m = string_find_errors("GCAT", "AAAACCCCGGGGTTTTATATACGTCAGCCC", 2, 4)
        self.assertTrue(len(m) == 4  and  len(set(m) & set([9, 10, 11, 14, 16, 20, 23, 26])) == 4)
        m = string_find_errors("GCAT", "AAAACCCCGGGGTTTTATATACGTCAGCCC", 2, 8)
        self.assertTrue(len(m) == 8  and  len(set(m) & set([9, 10, 11, 14, 16, 20, 23, 26])) == 8)

    def test_align_strings(self):
        ## Note more testing of this is done in the json test suite.
        ## Values used by spats:
        MV = 3
        MMC = 2
        GOC = 5
        GEC = 1
        simfn = lambda a,b: base_similarity_ind(a, b, MV, MMC, .5*MV)
        ap = AlignmentParams(simfn, GOC, GEC, penalize_front_clip=True)

        R = "GGMCSCGATGCCGNACGATKTAAGTCCGAGCATCAACTATGCCCTACCTGCTTCGRCCGATAAAGCTTTCAAWAGACGAYAAT"
        T = "GGACCCGATGCCGGACGAAAGTCCGCGCATCAACTATGCCTCTACCTGCTTCGGCCGATAAAGCCGACGATAATACTCCCAAAGCCC"
        a = align_strings(R, T, ap)
        self.assertEqual(a.score, 179.5)
        self.assertEqual(a.target_match_start, 0)
        self.assertEqual(a.target_match_end, 73)
        self.assertEqual(a.src_match_start, 0)
        self.assertEqual(a.src_match_end, 82)
        self.assertEqual(a.mismatched, [25])
        self.assertEqual(a.max_run, 23)
        self.assertEqual(a.indels_as_dict(), { '18': { "insert_type": True, "seq": "TKT", "src_index": 18 },
                                               '40': { "insert_type": False, "seq": "T", "src_index": 43 },
                                               '64': { "insert_type": True, "seq": "TTT", "src_index": 66 },
                                               '65': { "insert_type": True, "seq": "AAWA", "src_index": 70 } })
        self.assertEqual(a.indels_delta, 9)

        ## The following tests exercise the 'penalize_ends' part of align_strings()

        ## First we want to try both sides of:
        ##     2*GOC + GEC*(len(prefix1)+len(prefix2)) < MMC * min(len(prefix1), len(prefix2))
        ##     -->  MMC = 5 and 4
        R = "CCCCCAAAAAAAAAAAAAAAAAAAAAACCCC"
        T =  "TTTTAAAAAAAAAAAAAAAAAAAAAATTTTT"

        MMC = 5    # all indels
        ap.simfn = lambda a,b: AlignmentParams.char_sim(a, b, MV, MMC)
        a = align_strings(R, T, ap)
        self.assertEqual(a.score, 32.0)
        self.assertEqual(a.target_match_start, 0)
        self.assertEqual(a.target_match_end, 30)
        self.assertEqual(a.src_match_start, 0)
        self.assertEqual(a.src_match_end, 30)
        self.assertEqual(a.max_run, 22)
        self.assertEqual(len(a.mismatched), 0)
        self.assertEqual(a.indels_as_dict(), { '0': { 'insert_type': True, 'seq': "CCCCC", "src_index": 0 },
                                               '3': { 'insert_type': False, 'seq': "TTTT", "src_index": 5 },
                                              '26': { 'insert_type': True, 'seq': "CCCC", "src_index": 27 },
                                              '30': { 'insert_type': False, 'seq': "TTTTT", "src_index": 31 } })
        self.assertEqual(a.indels_delta, 0)

        MMC = 4    # all mismatches
        ap.penalize_front_clip = False
        ap.simfn = lambda a,b: AlignmentParams.char_sim(a, b, MV, MMC)
        a = align_strings(R, T, ap)
        self.assertEqual(a.score, 34.0)
        self.assertEqual(a.target_match_start, 0)
        self.assertEqual(a.target_match_end, 29)
        self.assertEqual(a.src_match_start, 1)
        self.assertEqual(a.src_match_end, 30)
        self.assertEqual(a.max_run, 22)
        self.assertEqual(len(a.indels), 0)
        self.assertEqual(a.indels_delta, 0)
        self.assertTrue(set(a.mismatched), set([0, 1, 2, 3, 26, 27, 28, 29]))

        R = "TTTCCCCCAAAAGACGATAAT"
        T = "CCCCCGACGATAATACTCCCAAAGCCCACCCAGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGTAGATCTCGGTGGTCGCCGTATCATT"
        MMC = 2
        ap.simfn = lambda a,b: AlignmentParams.char_sim(a, b, MV, MMC)
        a = align_strings(R, T, ap)
        self.assertEqual(a.score, 34.0)
        self.assertEqual(a.target_match_start, 0)
        self.assertEqual(a.target_match_end, 13)
        self.assertEqual(a.src_match_start, 3)
        self.assertEqual(a.src_match_end, 20)
        self.assertEqual(a.max_run, 9)
        self.assertEqual(a.indels_as_dict(), { '5': { 'insert_type': True, 'seq': "AAAA", 'src_index': 8 } })
        self.assertEqual(a.indels_delta, 4)
        self.assertEqual(len(a.mismatched), 0)

        MMC = 2
        ap.simfn = lambda a,b: AlignmentParams.char_sim(a, b, MV, MMC)
        R = "TGXXXCTGAAAGCAGG"
        T = "TGCTGAAAGCAGG"
        a = align_strings(R, T, ap)
        self.assertEqual(a.score, 32.0)
        self.assertEqual(a.target_match_start, 0)
        self.assertEqual(a.target_match_end, 12)
        self.assertEqual(a.src_match_start, 0)
        self.assertEqual(a.src_match_end, 15)
        self.assertEqual(a.max_run, 11)
        self.assertEqual(a.indels_as_dict(), { '2': { 'insert_type': True, 'seq': "XXX", "src_index": 2 } })
        self.assertEqual(a.indels_delta, 3)
        self.assertEqual(len(a.mismatched), 0)
