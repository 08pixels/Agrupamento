from base import pair_similarity

def _text(code1, code2): # Levenshtein distance.

    m = len(code1) + 1
    n = len(code2) + 1

    i_cost = 1 # Insertion cost
    d_cost = 1 # Delete cost
    s_cost = 1 # Substitution cost

    distances = [n * [0] for y in range(m)]

    for i in range(m):
        distances[i][0] = i_cost * i

    for j in range(n):
        distances[0][j] = i_cost * j

    for j in range(1, n):
        for i in range(1, m):
            if code1[i - 1] == code2[j - 1]:
                distances[i][j] = distances[i-1][j-1]
            else:
                distances[i][j] = min(distances[i-1][j] + d_cost,
                              distances[i][j-1] + i_cost,
                              distances[i-1][j-1] + s_cost)

    max_code = float(max(m - 1, n - 1))


    return 1 - (distances[m-1][n-1] / max_code)


def text(docs):
    # Traditional similarity
    return pair_similarity(docs, _text)
