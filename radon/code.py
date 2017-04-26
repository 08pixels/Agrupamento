[(x, y) for x in [1,2,3] for y in [3,1,4] if x != y]

while True:
	frase = raw_input()
	nova = ''
	letra_anterior_0 = '.'
	letra_anterior_1 = ' '
	if frase == '&':
		break

	for letra in frase:
		if letra == '0':
			if (letra_anterior_0 == '.' and letra_anterior_1 == ' ') or letra_anterior_1 == '.':
				nova += 'O'
			else:
				nova += 'o'
		elif letra == '1':
			if (letra_anterior_0 == '.' and letra_anterior_1 == ' ') or letra_anterior_1 == '.':
				nova += 'I'
			else:
				nova += 'i'
		elif letra == '2':
			if (letra_anterior_0 == '.' and letra_anterior_1 == ' ') or letra_anterior_1 == '.':
				nova += 'U'
			else:
				nova += 'u'
		elif letra == '4':
			if (letra_anterior_0 == '.' and letra_anterior_1 == ' ') or letra_anterior_1 == '.':
				nova += 'A'
			else:
				nova += 'a'
		elif letra == '5':
			if (letra_anterior_0 == '.' and letra_anterior_1 == ' ') or letra_anterior_1 == '.':
				nova += 'E'
			else:
				nova += 'e'
		else:
			nova += letra
		letra_anterior_0 = letra_anterior_1
		letra_anterior_1 = letra
	print nova
