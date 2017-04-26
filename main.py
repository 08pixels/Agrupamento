#coding: utf-8

import os, sys
import MySQLdb
# from Codes import Codes

conexao = MySQLdb.connect('localhost', 'root', 'root', 'Codigos-Estrutura_e_Dados')
dataTempFile = 'dataTemp'

# for row in cursor.fetchall():
# 	#	  corretude_func | complexidade | operador | operando
# 	print row[7],			row[8], 		 row[14], row[15]

# 	# for col in xrange(len(row)):
# 	# 	print ' ', row[col],

propertyKeys = {'CORRETUDE'		: 1,
				'COMPLEXIDADE'	: 2,
				'OPERADORES'	: 3,
				'OPERANDOS'		: 4,
				'JACCARD'		: 5,
				'TEXT'			: 6,
				'TREE'			: 7
				}

propertyID = [0, 7, 8, 14, 15, 1, 2, 3]

n_properties = 7	# quantidade de propriedades

# def generateData():
# 	global propertyKeys
# 	cursor = conexao.cursor()
	
# 	file = (dataTempFile, 'w')

# 	cursor.execute('SELECT * from programacao_codigo')

# 	for row in cursor.fetchall():
# 		current_str = ''
# 		current_str.append(	row[],
# 							row[],
# 							row[],
# 							)

# 	cursor.execute('SELECT * from programacao_similaridade')

def createGroups(n_properties):
	groups = []

	for i in xrange(n_properties + 1):
		groups.append([])

	return groups


def generateMasks(n_properties):
	masks = []

	for x in range(1, 2**n_properties):
		masks.append(''.join(str((x>>i)&1) for i in xrange(n_properties-1,-1,-1)))

	return masks


# def extract(bitmask):
# 	global n_properties, cursor
# 	current = []

# 	for i in xrange(n_properties):
		
# 	for row in cursor_1.fetchall():
# 		if bitmask[i]:

# 			if i < 4:
# 			else:
		
# 				current.append(row[ propertyID[ i + 1 ] ])


# 	return current

# masks 	= generateMasks(n_properties)
# groups	= createGroups(n_properties)


# for bitmask in masks:
# 	groups[ bitmask.count('1') ].append(extract(bitmask))

cursor = conexao.cursor()
# cursor.execute('SELECT * FROM `Codigos-Estrutura_e_Dados`.programacao_codigo as codigo WHERE codigo.problema_id = 49')
cursor.execute('SELECT arquivo, problema_id FROM programacao_codigo')

for row in cursor.fetchall():
	print row
