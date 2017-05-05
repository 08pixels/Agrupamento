#!/usr/bin/python
#coding: utf-8

import MySQLdb
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from codigo import Codigo

conexao = MySQLdb.connect('localhost', 'root', 'root', 'Codigos-Estrutura_e_Dados')
cursor = conexao.cursor()


chaveDePropriedades = {	0: 'CORRETUDE',
						1: 'COMPLEXIDADE',
						2: 'OPERADORES',
						3: 'OPERANDOS'		}

N				= 10
n_propriedades	= len(chaveDePropriedades)	# quantidade de propriedades
grupo_id		= [x for x in range(1, N+1)]

def target(valor):
	global grupo_id, N

	for i in grupo_id:	
		if valor <= (i * N):
			return i

def identificarChaves(): # Identifica por extenso as propriedades
	global n_propriedades
	global chaveDePropriedades

	propriedades = [[]]

	for x in range(1, 2**n_propriedades):
		p = []

		for i in range(0, n_propriedades):
			if( (x >> i) &1):
				p.append(chaveDePropriedades[i])

		propriedades.append(p)

	return propriedades


def criarCombinacoes(tupla):
	global n_propriedades

	lista_propriedades = [[n_propriedades]]

	for x in range(1, 2**n_propriedades):
		propriedade = []

		for i in range(0, n_propriedades): # notar que o 'i' eh a chave (bitmask) referente a cadeia de propriedades
			if( (x >> i) &1):
				propriedade.append(tupla[i])

		lista_propriedades.append(propriedade)

	return lista_propriedades


codes				 = []
dataTrainning		 = [] # lista de listas
dataTarget			 = [] # lista
DESCRICAO_DAS_CHAVES = identificarChaves()

neigh = KNeighborsClassifier(n_neighbors=N) # com N vizinhos

cursor.execute('SELECT medidas_ok, problema_id, arquivo, medida_corretude_funcional, medida_complexity, medida_distinct_operands, medida_distinct_operators FROM programacao_codigo WHERE programacao_codigo.problema_id = 49')

for row in cursor.fetchall():

	if row[0]: # medidas ok
		code = Codigo(row[1], row[2], row[3], row[4], row[5], row[6]) # segue a ordem de busca
		code.propriedades = criarCombinacoes(row[3:]) # apartir da terceira posicao comeca a ser os dados das propriedades

		codes.append(code)


for code in codes[:len(codes)/2]: # treina com metade dos codigos encontrados.
	
	code.grupo_id.append(target(code.propriedades[1][0])) # target soh aceita um elemento
	
	dataTrainning.append(code.propriedades[1])
	dataTarget.append(code.grupo_id[1])	# o indice significa uma chave (bitmask)

	# print ' [%12s ] %5s %7s' %(code.arquivo, code.grupo_id[1], code.propriedades[1][0]) # imprime formatado

neigh.fit(dataTrainning, dataTarget) # treinando o algoritmo

data  	= [ x.propriedades[1][0]	for x in codes[len(codes)/2:] ]
target 	= [ neigh.predict(x)[0]		for x in data ]

data.append(70)
target.append(8)

data.append(50)
target.append(5)

x_min, x_max = -5, 105
y_min, y_max = -5, 105

plt.figure(2, figsize=(8, 6))
plt.clf()

# Plot the training points
plt.scatter(data, target, c=target, cmap=plt.cm.Paired)
plt.xlabel('CORRETUDE FUNCIONAL')
plt.ylabel('CLASSIFICACAO')

plt.xlim(x_min, x_max)
plt.ylim(y_min, y_max)
plt.xticks(())
plt.yticks(())

plt.show()

# for code in codes[len(codes)/2:]:
# 	print '\n\nO CODIGO [%d] PERTENCE AO GRUPO %d\n\n' %(code.arquivo, neigh.predict(code.propriedades[1])[0])
