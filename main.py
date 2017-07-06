#!/usr/bin/python
#coding: utf-8

import MySQLdb
import numpy as np

from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn import metrics
from codigo import Codigo

import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from mpl_toolkits.mplot3d import Axes3D

conexao	= MySQLdb.connect('localhost', 'root', 'root', 'Codigos-Estrutura_e_Dados')
cursor	= conexao.cursor()


chaveDePropriedades = {	0: 'CORRETUDE',
						1: 'COMPLEXIDADE',
						2: 'OPERADORES',
						3: 'OPERANDOS'}

n_propriedades	= len(chaveDePropriedades)  # quantidade de propriedades


def identificarChaves():  # Identifica por extenso as propriedades
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

		# 'i' eh a chave (bitmask) referente a cadeia de propriedades
		for i in range(0, n_propriedades):
			if( (x >> i) &1):
				propriedade.append(tupla[i])

		lista_propriedades.append(propriedade)

	return lista_propriedades


codes 				 = []
DESCRICAO_DAS_CHAVES = identificarChaves()

cursor.execute('''SELECT medidas_ok,
						problema_id,
						arquivo,
						medida_corretude_funcional,
						medida_complexity,
						medida_distinct_operands,
						medida_distinct_operators
						FROM programacao_codigo
						WHERE programacao_codigo.problema_id = 49''')


for row in cursor.fetchall():

	if row[0]: # medidas ok
		code = Codigo(row[1], row[2], row[3], row[4], row[5], row[6])  # segue a ordem de busca
		code.propriedades = criarCombinacoes(row[3:])  # apartir do index 3 comeca a ser os dados das propriedades

		codes.append(code)


################################## BDSCAN ##################################

chaveDePropriedades = 15 # propriedade escolhida sem criterios

# parametros usados no algoritmo

''' eps:
		A distancia maxima entre duas amostras para que
		sejam consideradas como pertencentes a mesma vizinhanca
'''

''' min_samples:
		O numero de amostras (ou pelo total) em uma vizinhaca
		para um ponto ser considerado como ponto central.
		Isso inclui o proprio ponto.
'''

db = DBSCAN(eps=0.01, min_samples=1).fit([code.propriedades[chaveDePropriedades] for code in codes])

# print db.core_sample_indices_ # indices dos elementos que pertencem a um grupo
# print db.components_ # elementos e devidas propriedades (formatado)

# print db.labels_ # Especifica o grupo pertente do respectivo elemento (-1 representa o 'ruído')

for index in xrange(len(codes)):
	print codes[index].propriedades[chaveDePropriedades], ' Pertence ao grupo: ',  db.labels_[index]
