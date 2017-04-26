#-*- coding: latin1 -*-
import sys
import os

from edit import _text
from tree import _main
from tag import _token

files = ['codes/sol1321.py','codes/sol1322.py', 'codes/sol1323.py', 'codes/sol1324.py']

source1 = ''
source2 = ''
try:
    for i in range(0, len(files)):
        with open(files[i]) as fobj:
            source1 = fobj.read()

        for j in range(i+1, len(files)):
            with open(files[j]) as fobj:
                source2 = fobj.read()

            print("edit %f" % _text(source1, source2))
            print("token %f" % _token(source1, source2))
            print("tree %f" % _main(source1, source2))
except Exception as e :
    print("Erro>> " + str(e))
