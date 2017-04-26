import sys
from math import log, sqrt

def _create_docs_data(docs):
    docs_terms = {}
    docs_len = {}
    global_terms = {}
    max_freq = {}
    avg_freq = {}
    for doc in docs:
        terms = docs_terms.get(doc, {})
        docs_terms[doc] = terms
        docs_len[doc] = len(doc.nodes)
        for line in doc.nodes:
            terms[line] = terms.get(line, 0) + 1
            if max_freq.get(line, 0) < terms[line]:
                max_freq[line] = terms[line]
            docs_set = global_terms.get(line, set())
            docs_set.add(doc)
            global_terms[line] = docs_set
    for term, docs_set in global_terms.items():
        avg_freq[term] = sum([ docs_terms[doc][term] for doc in docs_set])/float(len(docs_set))
    return docs_terms, docs_len, global_terms, max_freq, avg_freq

def _create_docs_tfidf(tf_, idf_, docs_terms, docs_len, global_terms, max_freq, avg_freq):
    docs_tfidf = {}
    docs = docs_terms.keys()
    for doc in docs:
        tf_idf = {}
        docs_tfidf[doc] = tf_idf
        for term, freq in docs_terms[doc].items():
            docs_with_term = len(global_terms[term])
            idf = idf_(len(docs), docs_with_term)
            tf = tf_(float(freq), docs_len[doc], max_freq[term], avg_freq[term])
            tf_idf[term] = tf * idf
    return docs_tfidf

def _sim(tfidf1, tfidf2):
    terms1 = set(tfidf1.keys())
    terms2 = set(tfidf2.keys())
    terms = terms1.union(terms2)

    sum_wi_wj = 0
    sum_wi_2 = 0
    sum_wj_2 = 0
    
    for term in terms:
        sum_wi_wj += tfidf1.get(term, 0) * tfidf2.get(term, 0)
        sum_wi_2 += tfidf1.get(term, 0) ** 2
        sum_wj_2 += tfidf2.get(term, 0) ** 2

    return sum_wi_wj / ( sqrt(sum_wi_2) * sqrt(sum_wj_2))

def base_main(tf, idf, docs):
    docs_terms, docs_len, global_terms, max_freq, avg_freq = _create_docs_data(docs)
    docs_tfidf = _create_docs_tfidf(tf, idf, docs_terms, docs_len, global_terms, max_freq, avg_freq)
    conn = []
    sorted_docs = sorted(docs)
    for d1 in range(len(docs)):
        for d2 in range(d1 + 1, len(docs)):
            doc1 = sorted_docs[d1]
            doc2 = sorted_docs[d2]
            sim = _sim(docs_tfidf[doc1], docs_tfidf[doc2])
            conn.append((doc1, doc2, sim))
    return conn

# SMART NOTATION.. see: http://nlp.stanford.edu/IR-book/html/htmledition/document-and-query-weighting-schemes-1.html

N_TF = lambda freq, doc_len, max_freq, avg_freq : float(freq) / doc_len
L_TF = lambda freq, doc_len, max_freq, avg_freq : 1 + log(float(freq) / doc_len)
B_TF = lambda freq, doc_len, max_freq, avg_freq : 1 if float(freq) / doc_len > 0 else 0
A_TF = lambda freq, doc_len, max_freq, avg_freq : 0.5 + 0.5 * (float(freq)/max_freq)
LOGAVG_TF = lambda freq, doc_len, max_freq, avg_freq : (1 + log(float(freq) / doc_len)) / (1 + log(avg_freq))

N_IDF = lambda len_docs, docs_with_term : 1
T_IDF = lambda len_docs, docs_with_term : log(float(len_docs) / docs_with_term)
P_IDF = lambda len_docs, docs_with_term : 0.00001 if len_docs == docs_with_term else log((float(len_docs) - docs_with_term) / docs_with_term)

THISMODULE = sys.modules[__name__]

STRATEGIES = {}

from functools import partial

for name_tf, func_tf in zip(['n', 'l', 'b', 'a', 'lavg'], [N_TF, L_TF, B_TF, A_TF, LOGAVG_TF]):
    for name_idf, func_idf in zip(['n', 't', 'p'], [N_IDF, T_IDF, P_IDF]):
        name = 'tfidf-' + name_tf + name_idf + 'c'
        func = partial(base_main, func_tf, func_idf)
        setattr(THISMODULE, name, func)
        STRATEGIES[name] = func
