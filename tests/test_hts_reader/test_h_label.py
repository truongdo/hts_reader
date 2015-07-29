#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 truong-d <truong-d@truongd-XPS13-9333>
#
# Distributed under terms of the MIT license.

"""

"""
from hts_reader import h_label
import unittest


class TestHLabel(unittest.TestCase):

    def test_reduce_label(self):
        ctx = "i^i-i+r=e/A:1+2+1/B:13-xx_xx/C:20_1+1/D:02+xx_xx/E:4_1!xx_xx-1/F:2_1#xx_xx@3_8|27_16/G:6_1%xx_xx-1/H:xx_xx/I:10-42@1+1&1-10|1+11/J:xx_xx/K:1+10-11"
        ctx, ctx_match = h_label.reduce(ctx)
        self.assertEqual(ctx, "i^i-i+r=e/A:1+2+1/B:13-xx_xx/C:20_1+1/D:02+xx_xx/E:4_1!xx_xx-1/F:2_1#xx_xx@3_8|27_16/G:6_1%xx_xx-1/H:xx_xx/I:10-42@1+1&1-10|1+11/J:xx_xx/K:1+10")
        self.assertEqual(ctx_match, "i^i-i+r=e/A:1+2+1/B:13-xx_xx/C:20_1+1/D:02+xx_xx/E:4_1!xx_xx-1/F:2_1#xx_xx@3_8|27_16/G:6_1%xx_xx-1/H:xx_xx/I:10-42@1+1&1-10|1+11/J:xx_xx/K:1+10-")

        while ctx:
            ctx, ctx_match = h_label.reduce(ctx)
            print ctx_match


if __name__ == '__main__':
    unittest.main()
