

import math 

import numpy as np

x = 4
N = 20
A = 7



# calcul de la probabilité de tirer k attaquants 

def p_X_k(k):
    t = 0
    for i in range(1, N+1):
        if k <= i:
            t += proba_hyper_geo(k, x, N-x, i, N) * 1/(N)
    return t


def proba_hyper_geo(k, pN, qN,n, N):
    """ Calcul de la proba de la loi hypergéométrique avec les paramètres spécifiés"""
    return math.comb(pN,k) * math.comb(qN, n-k)/math.comb(N,n)
# construction de la matrice de transition de la chaîne de Markov 

def build_M():
    M = []
    for h in range(x+1):
        row = []
        for j in range(x+1):
            p = 0
            if j >= h:
                for m in range(j-h, x+1):
                    p += (math.comb(x-h, j-h)*math.comb(h, m-(j-h)) * p_X_k(m))/ math.comb(x,m)
            print(h, j, p)
            row += [round(p,3)]
        
        M += [row]

    print(M)
    return M

"""s = 0
for l in range(7):
    print(l, p_X_k(l))
    s += p_X_k(l)
print(s)
"""
"""
t= 0 
i = 10
for k in range(x+1):
    t+= proba_hyper_geo(k, x, N-x, i, N)
print(t)"""

M = build_M()

M7 = np.linalg.matrix_power(M, A)
print(M7)
print()
for row in M7:
    print([round(p,3) for p in row])


def p_e_x_y(sx, sy, N):
    return 1/((N*N) * math.comb(N, sx) * math.comb(N, sy))

def calc_p_j_1_0():
    s1= 1
    s2 = 2
    s3 = 3
    s4 = 2
    return 1 - (p_e_x_y(s1,s1, 3) + p_e_x_y(s1, s4, 3) + p_e_x_y(s4, s1, 3) + p_e_x_y(s4, s4, 3))

print(calc_p_j_1_0())

l = 0
N = 3
size_dict = {1: 1, 2:2, 3:3, 4:2}
for x in range(1,5):
    for y in range(1,5):
        print(x,y, p_e_x_y( size_dict[x], size_dict[y],N))
        l += p_e_x_y( size_dict[x], size_dict[y],N)
print(l)
