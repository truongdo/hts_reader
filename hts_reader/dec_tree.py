#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 truong-d <truong-d@truongd-XPS13-9333>
#
# Distributed under terms of the MIT license.

"""

"""
from collections import OrderedDict
import py_io
import logging
import os
import tree_lex
from tree_structure import Tree, get_answer
import tree_parser
import re

logger = logging.getLogger(__name__)
regex_tail = re.compile("\.\*$")
regex_head = re.compile("^\.\*")


def load_tree(fn_tree):
    return 0


class DecisionTree:

    def __init__(self):
        self.qs_list = OrderedDict()
        self.trees = {}
        pass

    def load_tree(self, fn, type='mgc'):
        if not os.path.exists(fn):
            logger.error("File not exists %s" % fn)
            exit(1)
        try:
            models = tree_parser.yacc.parse(open(fn).read())
        except:
            raise Exception("parsing tree error at ", fn)

        if type not in self.qs_list:
            self.qs_list[type] = OrderedDict()

        for m in models:
            if isinstance(m, Tree):
                m.BuildTree()
                state_id, stream_id = m.GetId()
                state_id = int(state_id)
                if ',' in stream_id:
                    for stid in stream_id.split(","):
                        stid = int(stid)
                        self.trees[(state_id, stid)] = m
                else:
                    if stream_id == '':
                        stream_id = "-1"
                    stream_id = int(stream_id)
                    self.trees[(state_id, stream_id)] = m
            else:
                regex_pat = []
                for pat in m.patterns:
                    regex_pattern = pat.replace("*", ".*").replace("\\", "\\\\").replace("+", "\+").replace("^", "\^").replace('$', '\$').replace("|", "\|").replace("?", ".")
                    if not regex_tail.search(regex_pattern):
                        regex_pattern += "$"
                    if not regex_head.search(regex_pattern):
                        regex_pattern = "^" + regex_pattern

                    regex_pat.append(re.compile(regex_pattern))

                m.patterns = regex_pat
                self.qs_list[type][m.name] = m

    def parse(self, ctx, sid=None, stid=None, type="mgc", cache=None):
        """
        Find model for ctx with state id and stream id
        Args:
        ===============================
            ctx: full context label (str)
            sid: state id (int)
            stid: stream id (int)
        """

        assert sid is not None
        assert stid is not None
        # answer = get_answer(ctx, self.qs_list[type])

        if type == "dur":
            cache_id = str(sid) + "-" + "-1"
            if cache_id in cache:
                if ctx in cache[cache_id]:
                    return cache[cache_id][ctx]
                    # raise Exception("cache has key " + str(sid) + "-" + str(stid) + ":" + ctx + ". But no model found. Some bugs exits")
            else:
                cache[cache_id] = {}
            model = self.trees[(sid, -1)].parse(ctx, self.qs_list[type])
            cache[cache_id][ctx] = model
            return model
        else:
            cache_id = str(sid) + "-" + str(stid)
            if cache_id in cache:
                if ctx in cache:
                    return cache[cache_id][ctx]
                # else:
                    # raise Exception("cache has key " + str(sid) + "-" + str(stid) + ". But no model found. Some bugs exits")
            else:
                cache[cache_id] = {}
            model = self.trees[(sid, stid)].parse(ctx, self.qs_list[type])
            cache[cache_id][ctx] = model
            return model

    def parse_has_answer(self, ctx, answer, sid=None, stid=None, type="mgc"):
        """
        Find model for ctx with state id and stream id
        Args:
        ===============================
            ctx: full context label (str)
            sid: state id (int)
            stid: stream id (int)
        """

        assert sid is not None
        assert stid is not None
        if type == "dur":
            #return self.trees[(sid, -1)].parse(ctx, self.qs_list[type])
            return self.trees[(sid, -1)].parse_has_answer(ctx, answer)
        else:
            return self.trees[(sid, stid)].parse_has_answer(ctx, answer)
