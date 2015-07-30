#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 truong-d <truong-d@truongd-XPS13-9333>
#
# Distributed under terms of the MIT license.

"""

"""
import unittest
from hts_reader import dec_tree
from hts_reader.tree_structure import get_answer


class TestDecisionTree(unittest.TestCase):

    def setUp(self):
        self.fn_tree = "examples/trees/cmp/mgc.inf.untied"
        self.tree = dec_tree.DecisionTree()
        #self.tree.load_tree(self.fn_tree)
        self.tree.load_tree("examples/trees/cmp/lf0.inf.untied")

    def test_parse(self):
        ctx = "i^i-d+e=s/A:2+3+3/B:20-1_1/C:10_7+2/D:14+xx_xx/E:3_3!xx_xx-1/F:5_1#xx_xx@2_1|4_5/G:xx_xx%xx_xx-xx/H:xx_xx/I:2-8@1+1&1-2|1+8/J:xx_xx/K:1+2-8"
        found_model = self.tree.parse(ctx, 2, 2)
        answer = "lf0_s2_429"
        self.assertEqual(answer, found_model)


def run_test():
    tree = dec_tree.DecisionTree()
    tree.load_tree("examples/trees/cmp/mgc.inf.untied", "mgc")
    tree.load_tree("examples/trees/cmp/lf0.inf.untied", "lf0")
    tree.load_tree("examples/trees/cmp/bap.inf.untied", "bap")
    #tree.load_tree("examples/trees/dur/dur.inf.untied", "dur")

    data = open("/home/truong-d/tmp/hts_reader/examples/trees/test_input").read().split("--")

    for idx, txt in enumerate(data):
        if idx % 100 == 0:
            print "processed", idx, "/", len(data)
        parts = txt.strip().split("\n")
        hmm = parts[0].replace("~h ", "").strip("\"\"").replace("/T:0", "").replace("/T:1", "")
        pdfs = parts[1:]

        for stream_id, pdf_name in enumerate(pdfs):
            stream_id += 1
            pdf_name = pdf_name.strip().replace("~p ", "").strip("\"\"")

            print hmm
            answer_mgc = get_answer(hmm, tree.qs_list["mgc"])
            answer_lf0 = get_answer(hmm, tree.qs_list["lf0"])
            answer_bap = get_answer(hmm, tree.qs_list["bap"])
            if stream_id == 1:
                parsed_pdf = tree.parse_has_answer(hmm, answer_mgc, 2, stream_id, "mgc")
            elif stream_id > 1 and stream_id < 5:
                parsed_pdf = tree.parse_has_answer(hmm, answer_lf0, 2, stream_id, "lf0")
                parsed_pdf += "-" + str(stream_id)
            else:
                parsed_pdf = tree.parse_has_answer(hmm, answer_bap, 2, stream_id, "bap")

            if parsed_pdf != pdf_name:
                print parsed_pdf
                print pdf_name
                print hmm
                exit(1)

if __name__ == '__main__':
    run_test()
    #unittest.main()
