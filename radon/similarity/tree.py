#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.
#Authors: Tim Henderson and Steve Johnson
#Email: tim.tadh@hackthology.com, steve.johnson.public@gmail.com

import sys, collections, itertools

class Node(object):

    def __init__(self, label):
        self.label = label
        self.children = list()

    def addkid(self, node, before=False):
        if before:  self.children.insert(0, node)
        else:   self.children.append(node)
        return self

    def get(self, label):
        if self.label == label: return self
        for c in self.children:
            if label in c: return c.get(label)

    def iter(self):
        queue = collections.deque()
        queue.append(self)
        while len(queue) > 0:
            n = queue.popleft()
            for c in n.children: queue.append(c)
            yield n

    def __contains__(self, b):
        if isinstance(b, str) and self.label == b: return 1
        elif not isinstance(b, str) and self.label == b.label: return 1
        elif (isinstance(b, str) and self.label != b) or self.label != b.label:
            return sum(b in c for c in self.children)
        raise TypeError, "Object %s is not of type str or Node" % repr(b)

    def __eq__(self, b):
        if b is None: return False
        if not isinstance(b, Node):
            raise TypeError, "Must compare against type Node"
        return self.label == b.label

    def __ne__(self, b):
        return not self.__eq__(b)

    def __repr__(self):
        return super(Node, self).__repr__()[:-1] + " %s>" % self.label

    def __str__(self):
        s = "%d:%s" % (len(self.children), self.label)
        s = '\n'.join([s]+[str(c) for c in self.children])
        return s
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#For licensing see the LICENSE file in the top level directory.


try:
    from editdist import distance as strdist
except ImportError:
    def strdist(a, b):
        if a == b:
            return 0
        else:
            return 1


def post_traverse(root):
    stack = list()
    pstack = list()
    stack.append(root)
    while len(stack) > 0:
        n = stack.pop()
        for c in n.children: stack.append(c)
        pstack.append(n)
    while len(pstack) > 0:
        n = pstack.pop()
        yield n

class AnnotatedTree(object):

    def __init__(self, root):
        def setid(n, _id):
            setattr(n, "_id", _id)
            return n

        self.root = root
        self.nodes = list() # a pre-order enumeration of the nodes in the tree
        self.lmds = list()  # left most descendents
        self.keyroots = None
            # k and k' are nodes specified in the pre-order enumeration.
            # keyroots = {k | there exists no k'>k such that lmd(k) == lmd(k')}
            # see paper for more on keyroots

        stack = list()
        pstack = list()
        stack.append((root, collections.deque()))
        j = 0
        while len(stack) > 0:
            n, anc = stack.pop()
            setid(n, j)
            for c in n.children:
                a = collections.deque(anc)
                a.appendleft(n._id)
                stack.append((c, a))
            pstack.append((n, anc))
            j += 1
        lmds = dict()
        keyroots = dict()
        i = 0
        while len(pstack) > 0:
            n, anc = pstack.pop()
            #print list(anc)
            self.nodes.append(n)
            #print n.label, [a.label for a in anc]
            if not n.children:
                lmd = i
                for a in anc:
                    if a not in lmds: lmds[a] = i
                    else: break
            else:
                try: lmd = lmds[n._id]
                except:
                    import pdb
                    pdb.set_trace()
            self.lmds.append(lmd)
            keyroots[lmd] = i
            i += 1
        self.keyroots = sorted(keyroots.values())

def distance(A, B):
    A, B = AnnotatedTree(A), AnnotatedTree(B)
    treedists = dict()

    def treedist(i, j):
        if i in treedists and j in treedists[i]: return treedists[i][j]
        def s(i, j, v):
            if i not in treedists: treedists[i] = dict()
            treedists[i][j] = v

        fd = forestdists = dict()
        def gfd(a, b): # get an item from the forest dists array
            if (a,b) in forestdists:
                return forestdists[(a,b)]
            if a[0] >= a[1] and b[0] >= b[1]: # δ(θ, θ) = 0
                return 0
            if b[0] >= b[1]:
                return forestdists[(a,(0,0))]
            if a[0] >= a[1]:
                return forestdists[((0,0),b)]
            raise KeyError, (a,b)

        Al = A.lmds
        Bl = B.lmds
        An = A.nodes
        Bn = B.nodes

        for x in xrange(Al[i], i+1): # δ(l(i1)..i, θ) = δ(l(1i)..1-1, θ) + γ(v → λ)
            fd[(Al[i], x), (0, 0)] = (
                gfd((Al[i],x-1), (0, 0)) + strdist(An[x].label, '')
            )
        for y in xrange(Bl[j], j+1): # δ(θ, l(j1)..j) = δ(θ, l(j1)..j-1) + γ(λ → w)
            fd[(0, 0), (Bl[j], y)] = (
                gfd((0,0), (Bl[j],y-1)) + strdist('', Bn[y].label)
            )

        for x in xrange(Al[i], i+1): ## the plus one is for the xrange impl
            for y in xrange(Bl[j], j+1):
                # only need to check if x is an ancestor of i
                # and y is an ancestor of j
                if A.lmds[i] == A.lmds[x] and B.lmds[j] == B.lmds[y]:
                    #                   +-
                    #                   | δ(l(i1)..i-1, l(j1)..j) + γ(v → λ)
                    # δ(F1 , F2 ) = min-+ δ(l(i1)..i , l(j1)..j-1) + γ(λ → w)
                    #                   | δ(l(i1)..i-1, l(j1)..j-1) + γ(v → w)
                    #                   +-
                    fd[((Al[i], x), (Bl[j], y))] = min(
                        (
                            gfd((Al[i],x-1), (Bl[j], y))
                            + strdist(An[x].label, '')
                        ),
                        (
                            gfd((Al[i], x), (Bl[j],y-1))
                            + strdist('', Bn[y].label)
                        ),
                        (
                            gfd((Al[i],x-1), (Bl[j],y-1))
                            +strdist(An[x].label, Bn[y].label)
                        )
                    )
                    s(x, y, fd[((Al[i], x), (Bl[j], y))])
                else:
                    #                   +-
                    #                   | δ(l(i1)..i-1, l(j1)..j) + γ(v → λ)
                    # δ(F1 , F2 ) = min-+ δ(l(i1)..i , l(j1)..j-1) + γ(λ → w)
                    #                   | δ(l(i1)..l(i)-1, l(j1)..l(j)-1) + treedist(i,j)
                    #                   +-
                    fd[((Al[i], x), (Bl[j], y))] = min(
                        (
                            gfd((Al[i],x-1), (Bl[j], y))
                            + strdist(An[x].label, '')
                        ),
                        (
                            gfd((Al[i], x), (Bl[j],y-1))
                            + strdist('', Bn[y].label)
                        ),
                        (
                            gfd((Al[i],Al[x]-1), (Bl[j],Bl[y]-1))
                            + treedist(x, y)
                        )
                    )
        if i in treedists and j in treedists[i]:
            return treedists[i][j]
        else:
            print('WTF')
            print(A.lmds[i], i), (B.lmds[j], j), tuple(xrange(A.lmds[i], i+1)), tuple(xrange(B.lmds[j], j+1))
            print(x, y)
            print(treedists)
            sys.exit(1)

    for i in A.keyroots:
        for j in B.keyroots:
            x = treedist(i,j)
    return x


def _create_tree(code):
    root = Node("_ROOT_")
    stack = [root]
    level = 0
    for line in code:
        cur_level = len(line) - len(line.strip())
        node = Node(line.strip())
        if cur_level == level:
            stack[-1].addkid(node)
        elif cur_level > level:
            stack[-1].addkid(node)
            stack.append(node)
        else:
            del stack[-1]
            stack[-1].addkid(node)
    return (root)


def _main(code1, code2):
    tree1 = _create_tree(code1)
    tree2 = _create_tree(code2)
    return 1 - distance(tree1, tree2) / float(max(len(code1), len(code2)))

from base import pair_similarity


def main(docs):
    return pair_similarity(docs, _main)
