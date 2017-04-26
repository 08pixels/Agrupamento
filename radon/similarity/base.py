""" Util functions to be used. """


def pair_similarity(docs, strategy):
    """ Calculate similarity among pairs of docs. """
    sorted_docs = sorted(docs)
    conn = []
    conn_docs = {}
    for doc1_index in range(len(docs) - 1):
        doc1 = sorted_docs[doc1_index]
        doc1_hash = doc1.nodes.hash()
        if doc1_hash in conn_docs:  # It is a clone from another doc. Repeat conn list.
            for result in conn_docs[doc1_hash][-(len(docs) - doc1_index - 1):]:
                conn.append((doc1, result[1], result[2]))
        else:
            conn_docs[doc1_hash] = []
            for doc2_index in range(doc1_index + 1, len(docs)):
                doc2 = sorted_docs[doc2_index]
                result = (doc1, doc2, strategy(doc1.nodes, doc2.nodes))
                conn.append(result)
                conn_docs[doc1_hash].append(result)

    return conn


def t_clone(docs):
    """ Search for cloned docs. Their nodes order are equal. """
    return pair_similarity(docs, lambda nodes1, nodes2: 1 if nodes1.hash() == nodes2.hash() else 0)
