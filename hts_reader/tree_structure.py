import re
from collections import OrderedDict
from hts_reader import h_label


class Question:
    def __init__(self, name, patterns):
        self.name = name
        self.patterns = patterns

    def display(self):
        print "QS %s { %s }"%(self.name,','.join(self.patterns))

    def GetPatterns(self):
        return self.patterns

    def GetName(self):
        return self.name

    def Match(self, string):
        for pattern in self.patterns:
            regex_pattern = pattern.replace("*", ".*").replace("\\", "\\\\").replace("+", "\+").replace("^", "\^").replace('$', '\$').replace("|", "\|").replace("?", ".")

            # Solve the problem of "y^*" should not match "my^*"
            if regex_pattern[0] not in ["*", "."]:
                if re.match(regex_pattern, string):
                    return True
            else:
                if re.search(regex_pattern, string):
                    return True
            #if len(pattern) != len(string):
                #continue
            #flag = 1
            #for c1, c2 in zip(string, pattern):
                #if c2 == '?':
                    #continue
                #if not c1 == c2:
                    #flag = 0
                    #break
            #if flag == 1:
                #return True
        return False


class Node:
    def __init__(self,id,pattern,no_node,yes_node):
        '''
        id: id of the node from a tree
        pattern: pattern to decide the next node
        no_node: if a string does not match the pattern of a node, the no_node will be selected.
        '''
        self.id = id
        self.pattern = pattern
        if isinstance(no_node, basestring):
            self.no_node = no_node.replace('"','')
        else:
            self.no_node = no_node
        if isinstance(yes_node,basestring):
            self.yes_node = yes_node.replace('"','')
        else:
            self.yes_node = yes_node

    def GetPattern(self):
        return self.pattern

    def GetYesNode(self):
        return self.yes_node

    def GetNoNode(self):
        return self.no_node

    def GetId(self):
        return self.id

    def display(self):
        print " %d %s %s %s"%(self.id,self.pattern,str(self.no_node),str(self.yes_node))

    def GetId(self):
        return self.id


def get_question_raw_name(prev_qs):
    if "<=" in prev_qs:
        prev_qs = prev_qs.split("<=")[0]
    else:
        prev_qs = prev_qs.split("=")[0]
    return prev_qs


regex_head = re.compile("^\.\*")
regex_tail = re.compile("\.\*$")


def get_answer2(ctx, qs_list):
    answer = OrderedDict()
    qs_keys = qs_list.keys()
    print qs_list
    #qs_keys.reverse()

    for qs_name in qs_keys:
        answer[qs_name] = False

    exit(1)
    prev_gs = get_question_raw_name(qs_keys[0])
    found = None

    for qs_name in qs_keys:
        raw_name = get_question_raw_name(qs_name)
        print raw_name
        print prev_gs
        if raw_name != prev_gs:
            if not found:
                idx = -1
                x = ctx[idx]
                if x in list('^-+=:+_!#@%&'):
                    idx = -2
                    x = ctx[idx]

                while x not in list('^-+=:+_!#@%&'):
                    idx -= 1
                    x = ctx[idx]
                    print x
                ctx = ctx[:idx + 1]

        pat_list = qs_list[qs_name].patterns
        to_replace = ""
        print qs_name, pat_list
        for pat in pat_list:
            regex_pattern = pat.replace("*", ".*").replace("\\", "\\\\").replace("+", "\+").replace("^", "\^").replace('$', '\$').replace("|", "\|").replace("?", ".")
            if regex_head.match(regex_pattern):
                regex_pattern = regex_head.sub("(", regex_pattern)
            else:
                regex_pattern = "(" + regex_pattern

            if regex_tail.match(regex_pattern):
                regex_pattern = regex_tail.sub("\\1).*", regex_pattern)
            else:
                regex_pattern = regex_pattern + ")"
            match = re.match(regex_pattern, ctx)
            if match:
                answer[qs_name] = True
                found = True
                to_replace = match.group(1)

        if raw_name != prev_gs:

            if found:
                print "Replacing", to_replace
                ctx = ctx.replace(to_replace, "")
            prev_gs = raw_name

        print "context", ctx
        if not ctx:
            break

    return answer


def get_answer(ctx, qslist):
    """Get all answer for each question"""

    answer = OrderedDict()
    qs_keys = qslist.keys()

    for qs_name in qs_keys:
        answer[qs_name] = False

    for qs_name, question in qslist.items():

        pat_list = question.patterns
        for pat in pat_list:
            regex_pattern = pat.replace("*", ".*").replace("\\", "\\\\").replace("+", "\+").replace("^", "\^").replace('$', '\$').replace("|", "\|").replace("?", ".")

            if not regex_tail.search(regex_pattern):
                regex_pattern += "$"

            if not regex_head.search(regex_pattern):
                regex_pattern = "^" + regex_pattern

            match = re.search(regex_pattern, ctx)
            if match:
                answer[qs_name] = True

    return answer


def get_single_answer(ctx, question):
    pat_list = question.patterns
    for pat in pat_list:
        regex_pattern = pat.replace("*", ".*").replace("\\", "\\\\").replace("+", "\+").replace("^", "\^").replace('$', '\$').replace("|", "\|").replace("?", ".")

        if not regex_tail.search(regex_pattern):
            regex_pattern += "$"

        if not regex_head.search(regex_pattern):
            regex_pattern = "^" + regex_pattern

        match = re.search(regex_pattern, ctx)
        if match:
            return True
    return False


class Tree:
    def __init__(self, nodes):    # Define a tree by its name and its nodes
        self.name = ""
        self.nodes = nodes
        self.root = ""
        self.id2node = {}

    def SetName(self,name):
        self.name = name

    def GetId(self):
        state_id = ""
        stream_id = ""

        re_m = re.match(r'\{\*\}\[(\d+)\]\.stream\[([(\d),]+)\]',self.name)
        if re_m:
            state_id,stream_id = re_m.groups()
        else:
            state_id = re.match(r'\{\*\}\[(\d+)\]',self.name).group(1)
        if int(state_id):
            return int(state_id), stream_id
        else:
            print "Failed to get Tree ID from its name",self.name

    def GetNodeById(self,id):
        if self.id2node.has_key(id):
            return self.id2node[id]
        else:
            print "No node with id",id
            exit(1)

    def display(self):
        print self.name+"\n{"
        for node in self.nodes:
            node.display()
        print "}"

    def IsLeaf(self,node):
        if not type(node) is int:
            return True
        else:
            return False

    def parse(self, ctx, qs_list, node=None):
        if node is None:    # Start from root
            node = self.root

        #print "==============-----"
        qs_name = node.GetPattern()

        answer = get_single_answer(ctx, qs_list[qs_name])
        #print "ask", qs_name, qs_list[qs_name].patterns
        #print ctx
        #print "answer:", answer

        if answer:  # if yes
            yes_node = node.GetYesNode()
            if self.IsLeaf(yes_node):
                return yes_node
            return self.parse(ctx, qs_list, self.id2node[yes_node])
        else:
            no_node = node.GetNoNode()
            if self.IsLeaf(no_node):
                return no_node
            return self.parse(ctx, qs_list, self.id2node[no_node])

    def BuildTree(self):
        if self.nodes[0].GetId() != 0:
            print "Tree error, does not have root node with id = 0"
            exit(1)
        self.root = self.nodes[0]
        for node in self.nodes:
            self.id2node[node.GetId()] = node
