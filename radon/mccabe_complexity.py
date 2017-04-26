#-*- coding: latin1 -*-
import subprocess

def ciclomatic_complexity(code):
    p = subprocess.Popen('python -m mccabe --min 0 ' + code, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    complexity = 0
    ret = p.stdout.readline()
    print 'asdasds' + str(ret)
    if (ret) :
        complexity = int(ret.split()[-1].strip("()"))
    else :
        complexity = 1

    #for line in p.stdout.readlines():
    #    print(line)
    #print(complexity)
    retval = p.wait()
    return complexity

#print(ciclomatic_complexity('/home/rodrigo/Codigos/radon/code1.py'))
# print(ciclomatic_complexity('/home/alexandre/workspace/avaliar/media/codigos/21/98/sol981.py'))
# print(ciclomatic_complexity('/home/alexandre/workspace/avaliar/media/codigos/21/98/sol982.py'))
# print(ciclomatic_complexity('/home/alexandre/workspace/avaliar/media/codigos/21/98/sol983.py'))
# print(ciclomatic_complexity('/home/alexandre/workspace/avaliar/media/codigos/21/98/sol9841.py'))

