#-*- coding: latin1 -*-
import subprocess

def ciclomatic_complexity(code):
    p = subprocess.Popen('python -m mccabe --min 1 ' + code, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    complexity = int(p.stdout.readline().split()[-1].strip("()"))

    #for line in p.stdout.readlines():
    #    print(line)

    retval = p.wait()
    return complexity

#print(ciclomatic_complexity('code.py'))