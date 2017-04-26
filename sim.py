import os, sys

from radon.similarity import edit
from radon.similarity import tag
from radon.similarity import tree

codigo_referencia = os.path.join('/home/rodrigo/Codigos/21', 'sol981.py')
codigo_solucao = os.path.join('/home/rodrigo/Codigos/21', 'sol981.py')

source1 = ''
source2 = ''

with open(codigo_referencia) as fobj:
    source1 = fobj.read()

with open(codigo_solucao) as fobj:
    source2 = fobj.read()

algoritmo = "Jaccard"

print("Jaccard\n%s\n%s" %(codigo_referencia, codigo_solucao))

coeficiente_similaridade = tag._token(source1, source2)
print(coeficiente_similaridade)

#algoritmo = "TextEdit"
#print("TextEdit %s(%d) %s(%d)" %(codigo_referencia.arquivo, i, codigo_solucao.arquivo, j))
#coeficiente_similaridade = edit._text(source1, source2)

#algoritmo = "Tree"
#print("Tree %s(%d) %s(%d)" %(codigo_referencia.arquivo, i, codigo_solucao.arquivo, j))
#coeficiente_similaridade = tree._main(source1, source2)