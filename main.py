#!/usr/bin/python
#coding: utf-8

import MySQLdb
from codigo import Codigo

conexao = MySQLdb.connect('localhost', 'root', 'root', 'Codigos-Estrutura_e_Dados')
cursor = conexao.cursor()

n_propriedades = 4	# quantidade de propriedades

propertyKeys = { 0: 'CORRETUDE',
				 1: 'COMPLEXIDADE',
				 2: 'OPERADORES',
				 3: 'OPERANDOS'		}

def identificarChaves():
	propriedades = [[]]

	for x in range(1, 2**n_propriedades):
		p = []

		for i in range(0, n_propriedades):
			if( (x >> i) &1):
				p.append(propertyKeys[i])

		propriedades.append(p)

	return propriedades


def criarCombinacoes(tupla):
	lista_propriedades = [[n_propriedades]]

	for x in range(1, 2**n_propriedades):
		propriedade = []

		for i in range(0, n_propriedades): # notar que o 'i' eh a chave (bitmask) referente a cadeia de propriedades
			if( (x >> i) &1):
				propriedade.append(tupla[i])

		lista_propriedades.append(propriedade)

	return lista_propriedades
	
# cursor.execute('SELECT * FROM `Codigos-Estrutura_e_Dados`.programacao_codigo as codigo WHERE codigo.problema_id = 49')

cursor.execute('SELECT medidas_ok, problema_id, arquivo, medida_corretude_funcional, medida_complexity, medida_distinct_operands, medida_distinct_operators FROM programacao_codigo WHERE programacao_codigo.problema_id = 49')

DESCRICAO_DAS_CHAVES = identificarChaves()
codes = []

for row in cursor.fetchall():

	if row[0]: # medidas ok
		code = Codigo(row[1], row[2], row[3], row[4], row[5], row[6]) # segue a ordem de busca
		code.propriedades = criarCombinacoes(row[3:]) # apartir da terceira posicao comeca a ser os dados das propriedades
		codes.append(code)