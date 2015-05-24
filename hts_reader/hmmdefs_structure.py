# This file contains classes to represent the HTK model structure.
#
# @author W.J. Maaskant
from collections import OrderedDict

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

    def to_string(self):
        string = []
        string.append("<MEAN> " + str(len(self.mean)))
        if len(self.mean) > 0:
            string.append(' %s' % (' '.join(['{:.6e}'.format(f) for f in self.mean])))

        string.append("<VARIANCE> " + str(self.cov.var.vec_size))
        if self.cov.var.vec_size > 0:
            string.append(' %s' % (' '.join(['{:.6e}'.format(f) for f in self.cov.var.vector])))

        return "\n".join(string)


class MixtureElem:
    def __init__(self):
        self.weight = None
        self.mpdf = None  # MixPdf
        pass

    def to_string(self):
        string = []
        string.append(str(self.weight))
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

    def GetStreamSize(self):
        return len(self.obj)
    def SetName(self,name) :
        self.name = name
    def SetPdf(self,pdf):
        if not isinstance(pdf,StreamPdf):
            raise Exception("input param is not StreamPdf. got"+type(pdf).__name__)
        if self.obj is None:
            self.obj = []
        else:
            self.obj.append(pdf)
    def GetName(self):
        return self.name
    def GetPdfName(self):
        return self.name
    def GetStream(self,stream_id):
        for stream in self.obj:
            if stream.GetId() == stream_id:
                return stream
        raise Exception("can not get pdf for stream",stream_id)
    def _verify(self):
        if self.obj is None:
            print "State_pdf", self.name, "has None obj"
            exit(1)

        for stream_pdf in self.obj:
            if stream_pdf is None:
                print "StreamPdf in statepdf",self.name,"is None type"
    def GetStreamPdfs(self):
        return self.obj
    def GetPdfs(self):
        pdfs = OrderedDict()
        for stream_pdf in self.obj:
            pdfs[stream_pdf.GetId()] = stream_pdf.GetPdfs()
        return pdfs
    def copy(self):
        spdf = StatePdf(self.obj, self.shared)
        spdf.SetName(self.name)
        return spdf


class StreamPdf:
    # obj can be Mixture or singel gaussian pdf
    def __init__(self,sid,obj,num_mix=0, shared=False):
        self.sid = sid
        self.obj = obj
        self.name = ""
        self.type = "p" # Shared Stream or Shared State
        self.shared=False
        if isinstance(self.obj,list):
            self.num_mix = len(self.obj)
        self.num_mix = 0
    def GetId(self):
        return self.sid
    def GetPdfs(self):
        return self.obj
    def GetPdfName(self):
        return self.name
    def SetName(self,name):
        self.name = name
    def copy(self):
        spdf = StreamPdf(self.sid, self.obj, self.num_mix, self.shared)
        spdf.SetName(self.name)
        return spdf
    def display(self, **kwargs):
        """ Return the StatePdf in text format
            E.g:
            >>> StatePdf.display(out_info=["name", "content"])
        """
        out_info = []
        if not kwargs:
            out_info = ["name", "content"]
        else:
            out_info = kwargs["stream_info"]

        string = []
        if "name_cmp" in out_info:
            string.append("<STREAM> %d" % self.sid)
            if self.name:
                string.append("~" + self.type + ' "' + self.name + '"')

        if "name" in out_info:
            if self.name:
                string.append("~" + self.type + ' "' + self.name + '"')
            string.append("<STREAM> %d" % self.sid)

        for info in out_info:
            if info == "content":
                if isinstance(self.obj, list):
                    string.append("<NUMMIXES> %s" % (str(len(self.obj))))
                    for mix in self.obj:
                        string.append(mix.display())
                else:
                    string.append(self.obj.display())

        return "\n".join(string)


class Mixture:
    def __init__(self,mix_id,weight,pdf):
        self.mix_id = mix_id
        self.pdf = pdf
        self.weight = weight
    def _verify(self):
        if self.mix_id is None:
            print "Mixture has no mix_id"
            exit(1)
        if self.pdf is None:
            print "Mixture id",self.mix_id,"has None type pdf"
            exit(1)
        if self.weight is None:
            print "Mixture id",self.mix_id,"has None weight"
            exit(1)

    def GetId(self):
        return self.mix_id
    def GetWeight(self):
        return self.weight
    def GetPdf(self):
        return self.pdf
    def display(self,unt=None):
        string = "%s %d %s\n"%("<MIXTURE>",self.mix_id,'{:.6e}'.format(self.weight))
        string+= self.pdf.display()
        return string


class Pdf:
    # @param mean An instance of Mean.
    # @param var An instance of Var.
    # gconst can be None
    def __init__(self, mean, var,gconst):
        if mean == None:
            raise HtkModelError('Parameter mean is None.')
        if var == None:
            raise HtkModelError('Parameter var is None.')
        self.mean = mean
        self.var = var
        self.gconst = gconst

    def GetMean(self):
        return self.mean

    def GetVar(self):
        return self.var

    def GetGConst(self):
        return self.gconst

    def display(self,unt=None):
        string = self.mean.display() + "\n"
        if self.gconst:
            string += self.var.display(display_name=False) + "\n"
            string += '<GCONST> %s'%('{:.6e}'.format(self.gconst))
        else:
            string += self.var.display(display_name=False)
        return string


class State:
    # obj can be a list of Stream containing  stream_pdf <StreamPdf> in case of cmp_hmm
    # or Shared State Pdf in case of dur_hmm, weight can be None in case of dur_hmm
    def __init__(self,weight=None, state_pdf=None,id=None):

        self.weight = weight
        # Sort the mixture list by mixture index.
        #streams.sort(key=operator.itemgetter(0))
        self.state_pdf = state_pdf
        self.sid = id
    def SetId(self,id):
        self.sid = id
    def SetPdf(self,pdf):
        if not isinstance(pdf,StatePdf):
            raise Exception("input param is not StatePdf, got "+pdf.GetName())
        self.state_pdf = pdf
    def SetPdfToStatePdf(self,pdf):
        """
        input is StreamPdf
        """
        self.state_pdf.SetPdf(pdf)
    def _verify(self):
        if self.weight is None:
            print "state_id",self.sid,"has None type weight"
            exit(1)
        if self.state_pdf is None:
            print "state_id",self.sid,"has None type pdf"
            exit(1)
        self.state_pdf._verify()
    def GetStream(self,stream_id):
        return self.state_pdf.GetStream(stream_id)
    def GetStreamSize(self):
        return self.state_pdf.GetStreamSize()
    def GetId(self):
        return self.sid
    def GetStatePdf(self):
        return self.state_pdf
    def GetPdfs(self):  # Only being call if this state has StatePdf, if this state has list of StreamPdf, the function GetStream will be called
        return self.state_pdf.GetPdfs()
    def SetStreamWeights(self,sweight):
        self.weight = sweight
    def GetSWeight(self):
        return self.weight
    def GetStreams(self):
        return self.streams

    def display(self, **kwargs):
        weight = ""
        if self.weight:
            weight = self.weight.display(True, display_name_only=True) + "\n"
        string = weight
        string += self.state_pdf.display(**kwargs)
        return string


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
