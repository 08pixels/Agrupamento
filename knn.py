# coding: utf-8

GROUP = (CORRETUDE, COMPLEXIDADE, OPERADORES, OPERANDOS, JACCARD, TEXT, TREE) = (1, 2, 3, 4, 5, 6, 7)

dataTrainning, dataTotal = 105, 150			# dataTotal is equals to number of lines in the file

database 	= []					# Will contains the data training
tests		= []					# Will contains the tests
correct 	= 0						# Number of correct answers	
idx 		= 0						# Index of tests
k			= 3						# K is the number of classes

file = open("database", 'r')		# Database file

def euclideanDistance(x, y):
	global k
	sum_distance = 0.0

	for i in xrange(k):
		sum_distance = sum_distance + (x[i]-y[i])**2

	return sum_distance ** 0.5

def sortSample(candidate):
	global database, dataTrainning, k

	classes 	= []
	distances	= []

	for element in GROUP:
		classes.append([0, element])

	for individual in database:
		dataCandidate = euclideanDistance(candidate, individual)
		distances.append((dataCandidate, individual[-1]))

	distances.sort()

	for i in xrange(k):
		classes[ int(distances[i][1])-1 ][0] += 1

	classes.sort()
	return classes[-1][1]						# Returns the element of greater frequency

for i in xrange(dataTrainning):					# Training the algorithm
	line = map(float, file.readline().split())
	database.append(line)

for i in xrange(dataTrainning, dataTotal):		# Add the test cases
	line = map(float, file.readline().split())
	tests.append(line)

for current in tests:							# Trying the algorithm
	if sortSample(current) == tests[idx][-1]:
		correct += 1

	idx += 1

print 'Number of correct answers: %d/%d' %(correct, dataTotal-dataTrainning)