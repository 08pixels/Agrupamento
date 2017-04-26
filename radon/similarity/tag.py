from base import pair_similarity

def _token_diff_base(union_op, code1, code2):
    hash_set1 = {}
    hash_set2 = {}

    for line in code1:
        hash_set1[line] = hash_set1.get(line, 0) + 1

    for line in code2:
        hash_set2[line] = hash_set2.get(line, 0) + 1

    tokens = set()
    tokens = tokens.union(hash_set1.keys())
    tokens = tokens.union(hash_set2.keys())
   
    inter = 0
    union = 0

    for one_token in tokens:
        token1 = 0 if one_token not in hash_set1 else hash_set1[one_token]
        token2 = 0 if one_token not in hash_set2 else hash_set2[one_token]
        inter += min(token1, token2)
        union += union_op(token1, token2)

    return inter, union

# Jaccard Index. Equivalent to Dice and Sorensen.
def _token(code1, code2):
    inter, union = _token_diff_base(max, code1, code2)
    return inter/float(union)

def token(docs):
    return pair_similarity(docs, _token)

# Jaccard Index with weigheted values (Buttler 2004)
def _tokenw(code1, code2):
    inter, union = _token_diff_base(lambda x, y: x + y, code1, code2)
    return 2 * (inter/float(union))

def tokenw(docs):
    return pair_similarity(docs, _tokenw)
