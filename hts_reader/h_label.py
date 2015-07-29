#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 truong-d <truong-d@truongd-XPS13-9333>
#
# Distributed under terms of the MIT license.

"""

"""


def reduce(ctx):
    """
    Reduce the label
    """
    idx = -1
    x = ctx[idx]
    while x not in list('^-+=:+_!#@%&|'):
        if x == ctx[0]:
            return None, None
        idx -= 1
        if 0 - idx == len(ctx):
            break
        x = ctx[idx]

    new = ctx[:idx]
    return new, new + x


def reverse(ctx):
    ctx = list(ctx)
    ctx.reverse()
    return "".join(ctx)
