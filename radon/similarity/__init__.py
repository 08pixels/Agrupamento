""" Main module to calculate similarity.

Used to invoke desired similarity strategy.
All similarities are values between 0 to 1.

* 0 represents no similarity at all.
* 1 represents max similarity.
"""

import tag
import tree
import edit
import tfidf
import base

STRATEGIES = {'token': tag.token,
              'tokenw': tag.tokenw,
              'text': edit.text,
              'tree': tree.main,
              'clone': base.t_clone}

for name, func in tfidf.STRATEGIES.items():
    STRATEGIES[name] = func


def main(strategy, docs):
    """ Main function. Returns a list of (doc1, doc2, similarity) tuples. """
    conn = STRATEGIES[strategy](docs)
    return conn
