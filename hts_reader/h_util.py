#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 truong-d <truong-d@truongd-XPS13-9333>
#
# Distributed under terms of the MIT license.

"""

"""

from hts_reader.h_model import HMMSet
from hts_reader.mythread import ThreadPool


def read_mul_hmm(file_list):
    for fn in file_list:
        tmp = HMMSet()
        tmp.read(fn, forced=True)
    # data = [open(fn).read() for fn in file_list]

    # pool = ThreadPool(len(data))
    # hmm_sets = []
    # for d in data:
        # tmp_hmm = HMMSet()
        # hmm_sets.append(tmp_hmm)
        # pool.add_task(tmp_hmm.read_from_stream, d, forced=True)
    # pool.wait_completion()
    # return hmm_sets
