#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 truong-d <truong-d@truongd-XPS13-9333>
#
# Distributed under terms of the MIT license.

"""

"""
from os.path import exists
import logging
import struct
import sys
import time
import io
from py_io import read_input

# import numpy as np
from hmmdefs_structure import Tmat, Var, StateInfo, SWeights, StreamInfo, StreamElem, \
    MixtureElem, MixPdf, Hmm

PI = 3.14159265358979
TPI = 6.28318530717959     # PI*2 */
LZERO = -1.0e10   # ~log(0) */
LSMALL = -0.5e10   # log values < LSMALL are set to LZERO */
MINEARG = -708.3   # lowest exp() arg  = log(MINLARG) */
MINLARG = 2.45e-308  # lowest log() arg  = exp(MINEARG) */

MACRO_TYPE = ['s', 'm', 'u', 'x', 'd', 'c',
              'r', 'a', 'b', 'g', 'f', 'y',
              'j', 'p', 'v', 'i', 't', 'w', 'h', 'o']

BEGINHMM = 0
USEMAC = 1
ENDHMM = 2
NUMMIXES = 3
NUMSTATES = 4
STREAMINFO = 5
VECSIZE = 6
MSDINFO = 7
NDUR = 8
PDUR = 9
GDUR = 10
RELDUR = 11
GENDUR = 12
DIAGCOV = 13
FULLCOV = 14
XFORMCOV = 15
STATE = 16
TMIX = 17
MIXTURE = 18
STREAM = 19
SWEIGHTS = 20
MEAN = 21
VARIANCE = 22
INVCOVAR = 23
XFORM = 24
GCONST = 25
DURATION = 26
INVDIAGCOV = 27
TRANSP = 28
DPROB = 29
LLTCOV = 30
LLTCOVAR = 31
PROJSIZE = 32
XFORMKIND = 90
PARENTXFORM = 91
NUMXFORMS = 92
XFORMSET = 93
LINXFORM = 94
OFFSET = 95
BIAS = 96
LOGDET = 97
BLOCKINFO = 98
BLOCK = 99
BASECLASS = 100
CLASS = 101
XFORMWGTSET = 102
CLASSXFORM = 103
MMFIDMASK = 104
PARAMETERS = 105
NUMCLASSES = 106
ADAPTKIND = 107
PREQUAL = 108
INPUTXFORM = 109
RCLASS = 110
REGTREE = 111
NODE = 112
TNODE = 113
HMMSETID = 191
PARMKIND = 120
MACRO = 121
EOFSYM = 122
NULLSYM = 123

DIAGC = 0         # diagonal covariance */
INVDIAGC = 1      # inverse diagonal covariance */
FULLC = 2         # inverse full rank covariance */
XFORMC = 3        # arbitrary rectangular transform */
LLTC = 4          # L' part of Choleski decomposition */
NULLC = 5         # none - implies Euclidean in distance metrics */
NUMCKIND = 6      # DON'T TOUCH -- always leave as final element */


class Token:

    def __init__(self, sym=None, tok_type=None, macro_type=None):
        self.sym = sym
        self.binForm = False
        self.macro_type = macro_type
        self.pkind = None

SYM_MAP = { "BEGINHMM": BEGINHMM, "USE": USEMAC,
            "ENDHMM": ENDHMM, "NUMMIXES": NUMMIXES,
            "NUMSTATES": NUMSTATES, "STREAMINFO": STREAMINFO,
            "VECSIZE": VECSIZE, "MSDINFO": MSDINFO, "NULLD": NDUR,
            "POISSOND": PDUR, "GAMMAD": GDUR,
            "RELD": RELDUR, "GEND": GENDUR,
            "DIAGC": DIAGCOV, "FULLC": FULLCOV,
            "XFORMC": XFORMCOV, "STATE": STATE,
            "TMIX": TMIX, "MIXTURE": MIXTURE,
            "STREAM": STREAM, "SWEIGHTS": SWEIGHTS,
            "MEAN": MEAN, "VARIANCE": VARIANCE,
            "INVCOVAR": INVCOVAR, "XFORM": XFORM,
            "GCONST": GCONST, "DURATION": DURATION,
            "INVDIAGC": INVDIAGCOV, "TRANSP": TRANSP,
            "DPROB": DPROB, "LLTC": LLTCOV,
            "LLTCOVAR": LLTCOVAR, "PROJSIZE": PROJSIZE,
            "RCLASS": RCLASS, "REGTREE": REGTREE,
            "NODE": NODE, "TNODE": TNODE,
            "HMMSETID": HMMSETID,
            "PARMKIND": PARMKIND, "MACRO": MACRO,
            "EOF": EOFSYM,
            "XFORMKIND": XFORMKIND, "PARENTXFORM": PARENTXFORM,
            "NUMXFORMS": NUMXFORMS, "XFORMSET": XFORMSET,
            "LINXFORM": LINXFORM, "OFFSET": OFFSET,
            "BIAS": BIAS, "LOGDET": LOGDET, "BLOCKINFO": BLOCKINFO, "BLOCK": BLOCK,
            "BASECLASS": BASECLASS, "CLASS": CLASS,
            "XFORMWGTSET": XFORMWGTSET, "CLASSXFORM": CLASSXFORM,
            "MMFIDMASK": MMFIDMASK, "PARAMETERS": PARAMETERS,
            "NUMCLASSES": NUMCLASSES, "ADAPTKIND": ADAPTKIND,
            "PREQUAL": PREQUAL, "INPUTXFORM": INPUTXFORM,
            "": NULLSYM}


quote_char = {'"': 1, '\'': 2}


class HMMSet():

    """Docstring for HMMSet. """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        """TODO: to be defined1. """
        self.hmm_fd = None
        self.swidth = []
        self.msdflag = []
        self.hmm_list = {}
        self.structures = {'h': {}, 't': {}, 'p': {}, 'v': {}, 's': {}, 'w': {}}
        self.vecSize = None
        self.pkind = None
        self.ckind = DIAGC   # Default is diagonal covariance

    def read_char(self):
        c = self.hmm_fd.read(1)

        if not c:
            return EOFSYM
        return c

    def read_string(self):
        isquote = False
        quote_type = None
        c = self.read_char()
        data = ""
        while c.isspace():
            c = self.read_char()

        if c in quote_char:
            isquote = True
            quote_type = c

        while True:
            c = self.read_char()
            if isquote:
                if c == quote_type:
                    return data
            else:
                if not c or c.isspace():
                    return data
            data += c
        return data

    def read_float(self, size=1):
        """ Read n short value. Default n = 1"""
        data = []
        for i in range(0, size):
            d = self.hmm_fd.read(4)
            try:
                d, = struct.unpack("<f", d)
                data.append(d)
            except:
                return None
        if size == 1:
            return data[0]
        else:
            return data

    def read_vector(self, size):
        data = self.read_float(size=size)
        if not isinstance(data, list):   # if size == 1
            return [data]
        else:
            return data

    def read_smatrix(self, nrow, ncol):
        data = []
        for i in range(0, nrow):
            data.append(self.read_vector(ncol))
        return data

    def read_short(self, size=1):
        """ Read n short value. Default n = 1"""
        data = []
        for i in range(0, size):
            d = self.hmm_fd.read(2)
            try:
                d, = struct.unpack("<h", d)
                data.append(d)
            except:
                return None
        if size == 1:
            return data[0]
        else:
            return data

    def read_int(self, size=1):
        """ Read n short value. Default n = 1"""
        data = []
        for i in range(0, size):
            d = self.hmm_fd.read(4)
            try:
                d, = struct.unpack("<i", d)
                data.append(d)
            except:
                return None
        if size == 1:
            return data[0]
        else:
            return data

    def GetToken(self, tok):
        """ Ported from Gettok in HModel.c. But this is a very
        simple version. Need to be updated"""
        c = self.read_char()
        if c == EOFSYM:
            tok.sym = EOFSYM
            return

        while c.isspace():
            c = self.read_char()

        if not c:
            tok.sym = EOFSYM

        if c == "~":  # If macro sym
            c = self.read_char()
            if c not in MACRO_TYPE:
                self.logger.error("Gettok: Illegal macro type " + c)
                exit(1)
            tok.sym = MACRO
            tok.macro_type = c
        elif c == "<":
            buf = ""
            c = self.read_char()
            while c != ">":
                buf += c
                c = self.read_char()
            if buf in SYM_MAP:
                tok.sym = SYM_MAP[buf]
            else:
                # if symbol not in symMap then it may be a sampkind
                # We have to find which parm, but to symplified, choose 9 which is
                # USER. Need to fix sometimes. See HModel.c:638:Gettok
                tok.sym = PARMKIND
                tok.pkind = 9
        else:
            tok.binForm = True
            sym = ord(self.read_char())
            tok.sym = sym

    # To allow pass by reference, nstate will be array, later we need to take only the first value
    def GetOption(self, tok, nstate):
        """ Will return nstate if it is presented, None otherwise"""
        if tok.sym == NUMSTATES:
            nstate[0] = self.read_short()
        elif tok.sym == STREAMINFO:
            num_stream = self.read_short()  # Read_short return a array
            if not num_stream:
                self.logger.error("Num Streams Expected")
                return None

            self.swidth.append(num_stream)
            sw = self.read_short(size=num_stream)
            self.swidth += sw
        elif tok.sym == MSDINFO:
            mf = self.read_short()
            self.msdflag.append(mf)
            mw = self.read_short(size=mf)
            self.msdflag += mw
        elif tok.sym == PARMKIND:
            self.pkind = tok.pkind
        elif tok.sym == VECSIZE:
            vs = self.read_short()
            self.vecSize = vs
        elif tok.sym == DIAGCOV:
            self.ckind = DIAGC
        elif tok.sym == INPUTXFORM:
            self.logger.info("Does not support INPUTXFORM macro. HModel.c:697")
            exit(1)

        self.GetToken(tok)

    # To allow pass by reference, nstate will be array, later we need to take only the first value
    def GetOptions(self, tok, nstate):
        self.GetToken(tok)

        while (tok.sym in [PARMKIND, INVDIAGCOV, HMMSETID, INPUTXFORM,
            PARENTXFORM, PROJSIZE]) or (tok.sym >= NUMSTATES and tok.sym <= XFORMCOV):
            self.GetOption(tok, nstate)

    def GetTransMat(self, token):
        if token.sym == TRANSP:
            tmat = Tmat()
            mat_size = self.read_short()
            matrix = self.read_smatrix(mat_size, mat_size)
            tmat.msize = mat_size
            tmat.matrix = matrix
        else:
            tmat = self.GetStructure(token.macro_type, self.read_string())

        self.GetToken(token)
        return tmat

    def GetStructure(self, macro_type, name):
        if macro_type not in self.structures:
            return None

        if name not in self.structures[macro_type]:
            return None
        self.structures[macro_type][name].n_use += 1
        return self.structures[macro_type][name]

    def GetVariance(self, token):
        if token.sym == VARIANCE:
            var_size = self.read_short()
            if var_size > 0:
                var_vec = self.read_vector(var_size)
            elif var_size == 0:
                var_vec = [0.]

            s_var = Var()
            s_var.vec_size = var_size
            s_var.vector = var_vec
        elif token.sym == MACRO and token.macro_type == 'v':
            s_var = self.GetStructure(token.macro_type, self.read_string())
        self.GetToken(token)
        return s_var

    def GetSweights(self, token):
        size = None
        vector = None

        if token.sym == SWEIGHTS:
            v = SWeights()
            size = self.read_short()
            vector = self.read_vector(size)
            v.size = size
            v.vector = vector
        elif token.sym == MACRO and token.macro_type == "w":
            v = self.GetStructure(token.macro_type, self.read_string())
            v.n_use += 1
        self.GetToken(token)
        return v

    def GetDiscreteWeights(self, dpdf, token, nMix=1):
        weight = 0
        repCount = 0

        for m in range(1, nMix + 1):
            if repCount > 0:
                repCount -= 1
            else:
                weight = self.read_short()
                if weight < 0:
                    self.logger.info("Weight is < 0. Check HModel.c:1035 to fix")
                    exit(1)
                dpdf[m] = weight
        self.GetToken(token)

    def GetMean(self, token):
        m = None
        size = None
        if token.sym == MEAN:
            size = self.read_short()
            if size > 0:
                m = self.read_vector(size)
            elif size == 0:
                m = [0.]
        elif token.sym == MACRO and token.macro_type == 'u':
            self.logger.info("Not support u macro yet")
            exit(1)
        self.GetToken(token)
        return m

    def GetMixPdf(self, token):
        if token.sym == MACRO and token.macro_type == "m":
            name = self.read_string()
            mp = self.GetStructure(token.macro_type, self.read_string())

            if not mp:
                self.logger.info("Can not find structure " + name)
                exit(1)
            self.GetToken(token)
        else:
            mp = MixPdf()
            mp.stream = 0
            mp.gConst = LZERO
            mp.mIdx = 0
            mp.mean = self.GetMean(token)
            if token.sym == VARIANCE or (token.sym == MACRO and token.macro_type == "v"):
                mp.cov.var = self.GetVariance(token)
            elif token.sym == INVCOVAR or (token.sym == MACRO and token.macro_type == 'i'):
                self.logger.info("Not support for INVCOVAR.")
                exit(1)
            elif token.sym == LLTCOVAR or (token.sym == MACRO and token.macro_type == 'c'):
                self.logger.info("Not support for LLTCOVAR.")
                exit(1)
            elif token.sym == XFORM or (token.sym == MACRO and token.macro_type == 'x'):
                self.logger.info("Not support for XFORM.")
                exit(1)
            if token.sym == GCONST:
                mp.gConst = self.read_float()
                self.GetToken(token)
        return mp

    def GetMixture(self, spdf, token, nMix=1):
        w = 1.0
        m = 1
        if token.sym == MIXTURE:
            m = self.read_short()
            w = self.read_float()
            self.GetToken(token)

        spdf[m] = MixtureElem()
        spdf[m].weight = w
        spdf[m].mpdf = self.GetMixPdf(token)
        # return spdf

    def GetStreamInfo(self, token, default_stream=1):
        if token.sym == MACRO and token.macro_type == 'p':
            sti = self.GetStructure(token.macro_type, self.read_string())
            sti.n_use += 1
            self.GetToken(token)
        else:
            sti = StreamInfo()
            if token.sym == STREAM:
                sti.stream = self.read_short()
                self.GetToken(token)
            else:
                sti.stream = default_stream
            if token.sym == NUMMIXES:
                sti.nMix = self.read_int()
                self.GetToken(token)
            else:
                sti.nMix = 1

            if token.sym == TMIX:  # Tied Mixture, HModel.c:2048
                self.logger.info("Does not support Tied Mixture")
                exit(1)
            else:  # Discrete model
                if token.sym == DPROB:
                    self.GetDiscreteWeights(sti.spdf.dpdf, token, nMix=sti.nMix)
                else:  # PLAIN/SHARED Mixture
                    self.GetMixture(sti.spdf.cpdf, token, nMix=sti.nMix)
                    while token.sym == MIXTURE:
                        self.GetMixture(sti.spdf.cpdf, token, nMix=sti.nMix)
                    for m in range(1, sti.nMix + 1):
                        if sti.spdf.cpdf[m] is None:
                            self.logger.info("None MixPdf. See HModel.c:2089 to fix")
                            self.logger.info("EmptyMixPdf failed")
                            exit(1)
        return sti

    def GetStream(self, pdf, token):
        s = 1

        if token.sym == STREAM:
            s = self.read_short()
            self.GetToken(token)
        pdf[s] = StreamElem()
        pdf[s].info = self.GetStreamInfo(token, default_stream=s)

    def GetStateInfo(self, token):
        S = self.swidth[0]
        if token.sym == MACRO and token.macro_type == 's':
            name = self.read_string()
            si = self.GetStructure(token.macro_type, name)
            si.n_use = 1
            self.GetToken(token)
        else:
            si = StateInfo()
            if token.sym == SWEIGHTS or (token.sym == MACRO and token.macro_type == 'w'):
                si.weights = self.GetSweights(token)

            self.GetStream(si.pdf, token)
            while token.sym == STREAM:
                self.GetStream(si.pdf, token)

            if token.sym == DURATION:
                self.logger.info("Not support for duration macro yet")
                exit(1)
            else:
                si.dur = None
        if (S > 1 and si.weights is None):
            si.weights = [1 for x in range(S + 2)]
            # for i in range(1, S + 1):
                # si.weights[i] = 1.0
        return si

    # To allow pass by reference, nstate will be array, later we need to take only the first value
    def GetHMMDef(self, hmm, nstate, token):
        state = 0

        if token.sym != BEGINHMM:
            self.logger.info("<BEGINHMM> symbol expected")
            exit(1)
        self.GetToken(token)
        if token.sym == USEMAC:
            self.logger.info("Does not support USEMAC macro")
            exit(1)
        while token.sym != STATE:
            self.GetOption(token, nstate)

        if nstate[0] == 0:
            self.logger.info("NumStates not set")
            exit(1)

        hmm.numStates = nstate[0]
        hmm.hIdx = 0

        while token.sym == STATE:
            state = self.read_short()
            if state < 2 or state > nstate[0]:
                self.logger.info("State index out of range")
                exit(1)
            self.GetToken(token)
            hmm.svec[state] = self.GetStateInfo(token)

        if token.sym == TRANSP or (token.sym == MACRO and token.macro_type == 't'):
            hmm.transP = self.GetTransMat(token)
        else:
            self.logger.info("Transition Matrix Missing")
            exit(1)

        if token.sym == DURATION or (token.sym == MACRO and token.macro_type == 'd'):
            self.logger.info("Does not support duration macro yet")
            exit(1)
        else:
            hmm.dur = None

        if token.sym != ENDHMM:
            self.logger.info("<ENDHMM> symbol expected")
            exit(1)

        self.GetToken(token)

    def LoadAllMacros(self, forced=False):
        token = Token()
        self.GetToken(token)
        nstate = [None]
        while token.sym != EOFSYM:
            tok_type = token.macro_type
            if token.macro_type != "o":
                string = self.read_string()
                if tok_type == 'h':  # Load hmm
                    if string not in self.hmm_list:
                        if forced:
                            self.hmm_list[string] = Hmm()
                        else:
                            self.logger.info(string + " not found")
                            exit(1)

                    self.GetToken(token)
                    self.GetHMMDef(self.hmm_list[string], nstate, token)
                    self.hmm_list[string].name = string
                    self.structures['h'][string] = self.hmm_list[string]

                else:  # Load shared model
                    self.GetToken(token)
                    if tok_type == 't':
                        structure = self.GetTransMat(token)
                    if tok_type == 'v':
                        structure = self.GetVariance(token)
                    if tok_type == 's':
                        structure = self.GetStateInfo(token)
                    if tok_type == 'w':
                        structure = self.GetSweights(token)
                    if tok_type == 'p':
                        structure = self.GetStreamInfo(token, 0)
                    structure.name = string
                    self.structures[tok_type][string] = structure
            else:
                self.GetOptions(token, nstate)

    def STREAMINFO(self):
        # Write o macro
        sinfo = ["<STREAMINFO>"]
        for sw in self.swidth:
            sinfo.append(str(sw))
        return " ".join(sinfo)

    def MSDINFO(self):
        if len(self.msdflag) == 0:
            return ""

        # Write o macro
        msdinfo = ["<MSDINFO>"]
        for sw in self.msdflag:
            msdinfo.append(str(sw))
        return " ".join(msdinfo)

    def VECSIZE(self):
        if not self.vecSize:
            return ""

        # Write o macro
        info = ["<VECSIZE>", str(self.vecSize)]
        return " ".join(info)

    def PARAM(self):
        return "<NULLD><USER><DIAGC>"

    def write(self, ostream, unt=False):
        # Write o macro
        print >> ostream, "~o", "\n",
        text = []
        text.append(self.STREAMINFO())
        text.append(self.MSDINFO())
        text.append(self.VECSIZE() + self.PARAM())
        if unt:
            # Print out TransP
            for name, s in self.structures['t'].items():
                if s.n_use > 0:
                    text.append(s.to_string())

            # Print out SWeights
            for name, s in self.structures['w'].items():
                if s.n_use > 0:
                    text.append(s.to_string())

            # Print out VarFloor
            for name, s in self.structures['v'].items():
                if s.n_use > 0:
                    text.append(s.to_string())

            # Print out HMM info
            for name, s in self.structures['h'].items():
                text.append(s.to_string_unt())

        else:
            # Print out TransP
            for name, s in sorted(self.structures['t'].items()):
                if s.n_use > 0:
                    text.append(s.to_string())

            # Print out SWeights
            for name, s in sorted(self.structures['w'].items()):
                if s.n_use > 0:
                    text.append(s.to_string())

            # Print out VarFloor
            for name, s in sorted(self.structures['v'].items()):
                if s.n_use > 0:
                    text.append(s.to_string())

            # Print out Shared StateInfo
            for name, s in sorted(self.structures['p'].items()):
                if s.n_use > 0:
                    text.append(s.to_string())

            # Print out Shared StateInfo
            for name, s in sorted(self.structures['s'].items()):
                if s.n_use > 0:
                    text.append(s.to_string())

            # Print out HMM info
            for name, s in sorted(self.structures['h'].items()):
                text.append(s.to_string())

        if "" in text:
            text.remove("")

        print >> ostream, "\n".join(text)

        pass

    def read(self, fn_hmm=None, fn_list=None, forced=False, from_pipe=False, from_stdin=False):
        """ Read HMMSet from file (binary)
        Args:
            fn (string): filename or None(stdin), or command(pipe)
            from_pipe: bool, True if fn is cmd. When the character '|' is appear at the end
                        of fn, this argument will be activated
            from_stdin: bool, True if fn is None

        Note that from_pip and from_stdin cannot be set True together

        Return:
            0 if OK, otherwise 1 for failed

        Examples:
        >>> hmm_set.read(forced=True, from_stdin=True)
        """
        # TODO, check fn_hmm is binary
        if fn_hmm and ("|" not in fn_hmm) and (not exists(fn_hmm)):
            self.logger.info(fn_hmm + " is not exists")
            exit(1)

        if "|" in fn_hmm:
            from_pipe = True

        if fn_list:
            if isinstance(fn_list, list):
                for line in fn_list:
                    line = line.strip()
                    if line in self.hmm_list:
                        self.logger.info("Duplicated hmm " + line)
                        exit(1)
                    self.hmm_list[line] = Hmm()
            else:
                for line in open(fn_list):
                    line = line.strip()
                    if line in self.hmm_list:
                        self.logger.info("Duplicated hmm " + line)
                        exit(1)
                    self.hmm_list[line] = Hmm()

        if (not from_pipe) and (not from_stdin):
                self.hmm_fd = io.BytesIO(open(fn_hmm, 'rb').read())
        elif from_pipe:
            self.hmm_fd = io.BytesIO(bytearray(read_input(fn_hmm)))
        elif from_stdin:
            if sys.version_info[0] >= 3:
                self.hmm_fd = sys.stdin.detach()
            else:
                self.hmm_fd = io.BytesIO(bytearray(sys.stdin.read()))

        self.LoadAllMacros(forced=forced)
        return 0
