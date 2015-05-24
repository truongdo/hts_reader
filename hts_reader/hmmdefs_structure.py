# This file contains classes to represent the HTK model structure.
#
from collections import OrderedDict
import copy

class HtkModelError(Exception):
    pass

class NoneTypeVector(Exception):
    pass
class HmmModelError(Exception):
    pass
class GlobalInfo:
    def __init__(self,streaminfo,vecsize,nulld,user,diagc,msdinfo=None):
        self.streaminfo = streaminfo
        self.msdinfo = msdinfo
        self.vecsize = vecsize
    def display(self,unt=None):
        string = "~o\n"
        string += "<STREAMINFO> "+' '.join([str(f) for f in self.streaminfo])+"\n"
        if self.msdinfo:
            string += "<MSDINFO> "+' '.join([str(f) for f in self.msdinfo])+"\n"
        string +="<VECSIZE> "+str(self.vecsize)+"<NULLD><USER><DIAGC>"
        return string
# TODO:    It would be nice to parse the HMM name here, set an attribute
# indicating the 'gramness' (n=1, n=3) and splitting the name if n=3.


class StateElem():

    """Docstring for StateElem. """

    def __init__(self):
        """TODO: to be defined1. """
        self.info = StateInfo()
        pass


class Hmm:
    # @param states A list containing 2-tuples, consisting of the state index and an instance of State.
    # @param tmat An instance of Tmat.
    def __init__(self, states=None, tmat=None):
        self.numStates = 0
        self.hIdx = 0
        self.svec = [None, None, None, None, None, None, None]
        # self.svec = [StateElem() for x in range(10)]
        self.name = None
        self.transP = None  # This
        self.dur = None

    def to_string(self):
        string = []
        string.append('~h ' + '"' + self.name + '"')
        string.append('<BEGINHMM>')
        string.append('<NUMSTATES> ' + str(self.numStates))

        for idx, si in enumerate(self.svec):
            if si:
                string.append('<STATE> %s' % idx)
                string.append(si.WriteSweights())
                if not isinstance(si.weights, list):   # this is cmp model, duration model has sweight as a list, let's print all stream
                    string.append(si.to_string_ste_tied())
                else:
                    string.append(si.WriteName())

        string.append(self.transP.WriteName())
        string.append('<ENDHMM>')
        if "" in string:
            string.remove("")
        return "\n".join(string)

    def to_string_unt(self):
        string = []
        string.append('~h ' + '"' + self.name + '"')
        string.append('<BEGINHMM>')
        string.append('<NUMSTATES> ' + str(self.numStates))

        for idx, si in enumerate(self.svec):
            if si:
                string.append('<STATE> %s' % idx)
                string.append(si.WriteSweights())
                string.append(si.to_string_unt())

        string.append(self.transP.WriteName())
        string.append('<ENDHMM>')
        if "" in string:
            string.remove("")
        return "\n".join(string)


    def GetStateWithId(self,id):
        if self.states is None:
            raise Exception("self.states is None")
        for state in self.states:
            if state.GetId() == id:
                return state
        return None
    def SetStreamWeights(self,sweight):
        for i in range(len(self.states)):
            self.states[i].SetStreamWeights(sweight)
    def GetStreamSize(self):
        return self.states[2].GetStreamSize()
    def GetPdfs(self,state_id,stream_id=None):
        state = None
        for sm in self.states:
            if sm.GetId() == state_id:
                state = sm
                break
        if not state:
            raise Exception("Can not get state pdf "+str(state_id))

        if not stream_id:
            pdfs = state.GetPdfs()
        else:
            stream = state.GetStream(stream_id)
            if not stream:
                return None
            pdfs = stream.GetPdfs()
        return pdfs
    def GetAllPdfsOrdered(self):
        """Return all pdfs in ordered"""
        state = None
        hmm_pdfs = []
        for state in self.states:
            pdfs = state.GetPdfs()
            hmm_pdfs.append(pdfs)
        return hmm_pdfs
    def GetStates(self):
        return self.states
    def GetName(self):
        return self.name


class SWeights:
    def __init__(self, size=None, vector=None):
        self.size = size
        self.vector = vector
        self.name = ""
        self.n_use = 0

    def SetName(self, name):
        self.name = name

    def WriteName(self):
        return '~w ' + '"' + self.name + '"'

    def to_string(self):
        string = '~w ' + '"' + self.name + '"\n'
        string += '<SWEIGHTS> %s\n' % (str(self.size))
        string += ' %s' % (' '.join(['{:.6e}'.format(f) for f in self.vector]))
        return string


class Mean:
    # @param vector A list containing floats.
    def __init__(self, vec_len, vector):
        #if vector:
        #    self.vector = np.array(vector)
        #else:
        if vector is None:
            raise NoneTypeVector("Parameter vector must be not None")
        self.vector = vector
        self.vec_len = vec_len
    def GetVector(self):
        if self.vector is None:
            raise NoneTypeVector({"Mean has None type vector"})
        if self.vec_len == 0:
            return [0.]
        return  self.vector
    def display(self,unt=None):
        string = ""
        if self.vec_len == 0:
            string += "<MEAN> 0"
        else:
            string += "<MEAN> %s\n"%(str(len((self.vector))))
            string += ' %s' % (' '.join(['{:.6e}'.format(f) for f in self.vector]))
        return string


class Covariance:
    def __init__(self):
        self.var = None  # Var
        self.inv = None  # STriMat

    def copy(self):
        a = Covariance()
        a.var = self.var.copy()
        return a


class MixPdf:
    def __init__(self):
        self.mean = None  # Svector
        self.ckind = None  # Kind of coveriance
        self.cov = Covariance()
        self.gConst = None  # Precompute component of b(x)
        self.mIdx = None  # MixPdf index
        self.stream = None  # enables multi-stream
        self.vFloor = None
        self.info = None  # hook to hang information
        self.hook = None  # general hook
        self.param = (self.mean, self.ckind, self.cov,
                      self.gConst, self.mIdx, self.stream,
                      self.vFloor, self.info, self.hook)
        pass

    def copy(self):
        a = MixPdf()
        a.mean = copy.deepcopy(self.mean)
        a.ckind = self.ckind
        a.cov = self.cov.copy()
        a.gConst = self.gConst
        a.mIdx = self.mIdx
        a.stream = self.stream
        a.vFloor = self.vFloor
        a.info = self.info
        a.hook = self.hook
        return a

    def to_string(self):
        string = []
        if len(self.mean) == 1 and self.mean[0] == 0:
            string.append("<MEAN> 0")
        else:
            string.append("<MEAN> " + str(len(self.mean)))
            if len(self.mean) > 0:
                string.append(' %s' % (' '.join(['{:.6e}'.format(f) for f in self.mean])))

        if len(self.cov.var.vector) == 1 and self.cov.var.vector[0] == 0:
            string.append("<VARIANCE> 0")
        else:
            string.append("<VARIANCE> " + str(self.cov.var.vec_size))
            if self.cov.var.vec_size > 0:
                string.append(' %s' % (' '.join(['{:.6e}'.format(f) for f in self.cov.var.vector])))

        # string.append("<GCONST> %s" % '{:.6e}'.format(self.gConst))
        return "\n".join(string)


class MixtureElem:
    def __init__(self):
        self.weight = None
        self.mpdf = None  # MixPdf
        pass

    def copy(self):
        a = MixtureElem()
        a.weight = self.weight
        a.mpdf = self.mpdf.copy()
        return a

    def to_string(self):
        string = []
        string.append('{:.6e}'.format(self.weight))
        string.append(self.mpdf.to_string())
        if "" in string:
            string.remove("")
        return "\n".join(string)


class MixtureVector:
    def __init__(self):
        self.cpdf = [None, None, None, None, None, None, None]  # MixtureElem
        self.tpdf = []  # Vector type in HModel.h
        # dpdf will be indexed from 1
        # so the first value will be always None
        self.dpdf = [None, None, None, None, None, None, None]  # ShortVec in Hmodel.h
        pass

    def copy(self):
        a = MixtureVector()
        a.cpdf = [c.copy() if c else None for c in self.cpdf]
        return a

    def to_string(self):
        string = []
        cpdf = []
        for mix_elem in self.cpdf:
            if mix_elem is not None:
                cpdf.append(mix_elem)
        if len(cpdf) > 1:
            for mixid, mix_elem in enumerate(cpdf):
                mixid += 1
                if mix_elem:
                    string.append("<MIXTURE> " + str(mixid) + " " + mix_elem.to_string())
        else:
            string.append(cpdf[0].mpdf.to_string())

        if "" in string:
            string.remove("")
        return "\n".join(string)


class StreamInfo:
    def __init__(self):
        self.stream = 0
        self.nMix = 1
        self.spdf = MixtureVector()
        self.n_use = 0
        self.name = ""

    def copy(self):
        a = StreamInfo()
        a.stream = self.stream
        a.nMix = self.nMix
        a.spdf = self.spdf.copy()
        a.n_use = self.n_use
        a.name = self.name
        return a

    def SetName(self, name):
        self.name = name

    def WriteName(self):
        return "~p" + ' "' + self.name + '"'

    def to_string(self):
        string = []
        if self.name:
            string.append("~p" + ' "' + self.name + '"')
        string.append("<STREAM> " + str(self.stream))
        if self.nMix > 1:
            string.append("<NUMMIXES> " + str(self.nMix))
        string.append(self.spdf.to_string())
        if "" in string:
            string.remove("")
        return "\n".join(string)

    def to_string_unt(self):
        string = []
        string.append("<STREAM> " + str(self.stream))
        if self.nMix > 1:
            string.append("<NUMMIXES> " + str(self.nMix))
        string.append(self.spdf.to_string())
        if "" in string:
            string.remove("")
        return "\n".join(string)


class StreamElem:

    def __init__(self):
        self.info = StreamInfo()
        self.n_use = 1
        pass

    def copy(self):
        a = StreamElem()
        a.n_use = self.n_use
        a.info = self.info.copy()
        return a

    def to_string(self):
        return self.info.to_string()

    def to_string_unt(self):
        return self.info.to_string_unt()


class StateInfo:
    # obj can be a list of Stream containing  stream_pdf <StreamPdf>
    def __init__(self):
        self.weights = None  # SWeights component
        # self.pdf = [StreamElem() for x in range(10)]
        self.pdf = [None, None, None,
                    None, None, None]
        self.name = ""
        self.dur = None
        self.n_use = 0

    def copy(self):
        a = StateInfo()
        if isinstance(self.weights, list):
            a.weights = copy.deepcopy(self.weights)
        else:
            a.weights = self.weights.copy()
        a.pdf = [c.copy() if c else None for c in self.pdf]
        a.name = self.name
        a.n_use = self.n_use
        return a

    def WriteName(self):
        return "~s" + ' "' + self.name + '"'

    def WriteSweights(self):
        if not isinstance(self.weights, list):
            return self.weights.WriteName()
        return ""

    def to_string_ste_tied(self):
        """ Return the StatePdf in text format
            E.g:
        """
        string = []

        for ste in self.pdf:
            if ste:
                string.append("<STREAM> " + str(ste.info.stream))
                string.append(ste.info.WriteName())

        if "" in string:
            string.remove("")

        return "\n".join(string)

    def to_string(self):
        """ Return the StatePdf in text format
            E.g:
        """
        string = []

        if isinstance(self.weights, list):  # This State is belong to dur model, print name only
            string.append("~s" + ' "' + self.name + '"')
        for ste in self.pdf:
            if ste:
                string.append(ste.to_string())

        if "" in string:
            string.remove("")

        return "\n".join(string)

    def to_string_unt(self):
        """ Return the StatePdf in text format
            E.g:
        """
        string = []

        for ste in self.pdf:
            if ste:
                string.append(ste.to_string_unt())

        if "" in string:
            string.remove("")

        return "\n".join(string)


class Tmat:
    # @param vector A list containing floats.
    def __init__(self):
        self.matrix = None
        self.msize = 0
        self.name = ""
        self.n_use = 0

    def WriteName(self):
        return '~t ' + '"' + self.name + '"'

    def to_string(self):
        string = '~t ' + '"' + self.name + '"\n'
        string += "<TRANSP> %s\n" % str(len(self.matrix))
        mat = []
        for vec in self.matrix:
            mat.append(' %s' % ' '.join(['{:.6e}'.format(m) for m in vec]))
        return string + "\n".join(mat)

    def SetName(self,name):
        self.name = name

    def GetName(self):
        return self.name

    def GetMatrix(self):
        return self.vector


class Var:
    # @param vector A list containing floats.
    def __init__(self):
        self.vector = None
        self.vec_size = 0
        self.name = ""
        self.n_use = 1

    def copy(self):
        a = Var()
        a.vector = copy.deepcopy(self.vector)
        a.vec_size = self.vec_size
        a.name = self.name
        a.n_use = self.n_use
        return a

    def SetName(self, name):
        self.name = name

    def GetName(self):
        return self.name

    def GetVector(self):
        if self.vector is None:
            raise NoneTypeVector("Var has None type Var")
        if self.vec_len == 0:
            return [0.]
        return self.vector

    def to_string(self):
        string = '~v ' + '"' + self.name + '"\n'
        if self.vec_size == 0:
            string += '<VARIANCE> 0'
        else:
            string += '<VARIANCE> %s\n' % str(len(self.vector))
            string += ' %s' % (' '.join(['{:.6e}'.format(f) for f in self.vector]))
        return string
