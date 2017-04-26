# -*- coding: utf-8 -*-
#https://pypi.python.org/pypi/editdistance
import editdistance
#import Levenshtein

def f_editdistance(sourceA, sourceB) :
    return editdistance.eval(sourceA, sourceB)


#def f_levenshtein(sourceA, sourceB) :
#    return Levenshtein.distance(sourceA, sourceB)


'''
http://scikit-learn.org/0.17/modules/classes.html
import numpy as np
from sklearn.metrics import jaccard_similarity_score
y_pred = [0, 2, 1, 3]
y_true = [0, 1, 2, 3]
jaccard_similarity_score(y_true, y_pred)
jaccard_similarity_score(y_true, y_pred, normalize=False)
'''
