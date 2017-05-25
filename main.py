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

conexao = MySQLdb.connect('localhost', 'root', 'root', 'Codigos-Estrutura_e_Dados')
cursor = conexao.cursor()


chaveDePropriedades = { 0: 'CORRETUDE',
						1: 'COMPLEXIDADE',
						2: 'OPERADORES',
						3: 'OPERANDOS'}

n_propriedades	= len(chaveDePropriedades)	# quantidade de propriedades


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
			if( (x >> i) &1): # 1010
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
						medida_distinct_operators FROM programacao_codigo WHERE programacao_codigo.problema_id = 49''')


for row in cursor.fetchall():

	if row[0]: # medidas ok
		code = Codigo(row[1], row[2], row[3], row[4], row[5], row[6]) # segue a ordem de busca
		code.propriedades = criarCombinacoes(row[3:]) # apartir da terceira posicao comeca a ser os dados das propriedades

		codes.append(code)



############################################################################
################################## BDSCAN ##################################

X = StandardScaler().fit_transform([code.propriedades[1] for code in codes])

db = DBSCAN().fit(X)


core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
core_samples_mask[db.core_sample_indices_] = True
labels = db.labels_

n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)



############################################################################
################################ GRAFICO ###################################

# Black removed and is used for noise instead.
unique_labels = set(labels)
colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))

for k, col in zip(unique_labels, colors):

	if k == -1:
		col = 'k' # Black used for noise.

	class_member_mask = (labels == k)

	xy = X[class_member_mask & core_samples_mask]
	plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col, markeredgecolor='k', markersize=14)

	xy = X[class_member_mask & ~core_samples_mask]
	plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col, markeredgecolor='k', markersize=6)

plt.title('Estimated number of clusters: %d' % n_clusters_)

plt.show()