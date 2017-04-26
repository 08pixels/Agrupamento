#-*- coding: latin1 -*-
from radon.raw import analyze
from radon.metrics import mi_visit
from radon.metrics import mi_compute
from radon.metrics import h_visit
from radon.complexity import cc_visit
from radon.cli.tools import iter_filenames
from mccabe_complexity import ciclomatic_complexity

# iter through filenames starting from the current directory
# you can pass ignore or exclude patterns here (as strings)
# for example: ignore='tests,docs'
files = ['code1.py']#['code.py', 'T3E0.py', 'T4E0.py']
for filename in iter_filenames(files):
    with open(filename) as fobj:
        source = fobj.read()

    # get cc blocks
    #complexity = cc_visit(source)
    complexity = ciclomatic_complexity(filename)
    # get raw metrics
    raw = analyze(source)
    # Halstead metrics
    halstead = h_visit(source)

    # Now do what you want with the data
    print("================ \n ciclomatic complexity \n================ ")
    print("Ciclomatic Complexity: " + str(complexity))

    # print("================ \n raw metrics \n================ ")
    # print("LOC: " + str(raw[0]))
    # print("LLOC: " + str(raw[1]))
    # print("SLOC: " + str(raw[2]))
    # print("comments: " + str(raw[3]))
    # print("multi: " + str(raw[4]))
    # print("blank: " + str(raw[5]))
    # print("single_comments: " + str(raw[6]))

    print"================ \n halstead metrics \n================ "
    print("h1 is the number of distinct operators: " + str(halstead[0]))
    print("h2 is the number of distinct operands: " + str(halstead[1]))
    # print("N1 is the total number of operators: " + str(halstead[2]))
    # print("N2 is the total number of operands: " + str(halstead[3]))
    # print("h is the vocabulary, i.e. h1 + h2: " + str(halstead[4]))
    # print("N the length, i.e. N1 + N2: " + str(halstead[5]))
    # print("calculated_length = h1 * log2(h1) + h2 * log2(h2): " + str(halstead[6]))
    # print("volume = V = N * log2(h): " + str(halstead[7]))
    # print("difficulty: D = h1 / 2 * N2 / h2: " + str(halstead[8]))
    # print("effort: E = D * V: " + str(halstead[9]))
    # print("time: T = E / 18 seconds: " + str(halstead[10]))
    # print("bugs: B = V / 3000 - an estimate of the errors in the implementation: " + str(halstead[11]))

    # print("================ \n mi \n================ ")
    # # get MI score
    # mi = mi_visit(source, True) # using complexity = None
    # mi2 = mi_compute(halstead[7], complexity, raw[2], raw[3])

    # print("" + str(mi))
    # print("" + str(mi2))

    











