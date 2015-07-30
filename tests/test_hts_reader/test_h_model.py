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

import time

if __name__ == '__main__':
    hset = HMMSet()
    start = time.time()
    hset.read("examples/re_clustered.mmf", forced=True)
    end = time.time()
    print "Total time:", end - start
