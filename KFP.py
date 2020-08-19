import numpy as np
from numpy import linalg as la
import time
from math import sqrt
from math import ceil


def norms_calc(B):
    n = B.nrows
    norms = [B[i].norm() for i in range(n)]
    # print("\nNorms_Duration: ", time.time() - s1)

    # Numpy-norms-calculation is slower
    # basis = np.array(list(B))
    # s1 = time.time()
    # np_norms = [la.norm(basis[i]) for i in range(len(basis))]
    # print("\nNP: ", np_norms, "\nTime: ", time.time() - s1)
    return norms


def m_matrix(B, B_red, norms, n):
    # m = np.tril(np.ones((n, n)), -1)
    m1 = np.tril(np.ones((n, n)), -1)
    m_len = int((n ** 2 - n) / 2)  # number of down-tri

    # Double-Loop two times slower
    # for i in range(n):
    #     for j in range(i):
    #         if norms[i] > norms[j]:
    #             a = (B_red[i] * B[j]).astype(float)
    #             m[i, j] = la.norm(a / (norms[i] ** 2))
    #         else:
    #             a = (B[i] * B_red[j]).astype(float)
    #             m[i, j] = la.norm(a / (norms[j] ** 2))

    # Single-Loop
    for i in range(m_len):
        x = int((1 + sqrt(8*i+1))/2)
        y = i%x
        if norms[x] > norms[y]:
            a = (B_red[x] * B[y]).astype(float)
            m1[x, y] = la.norm(a / (norms[x] ** 2))
        else:
            a = (B[x] * B_red[y]).astype(float)
            m1[x, y] = la.norm(a / (norms[y] ** 2))
    return m1


def left_bound(M, x, R, norms,i,n):
    sum1 = 0
    sum2 = 0
    for j in range(i+1,n):
        sum1 += M[j,i]*x[j]
        sum2 += l_calc(j, n, M, x, norms)
    return ceil(-sum1 - sqrt((R**2 - sum2)/norms[i]))


def l_calc(j, n, M, x, norms):
    sum = 0
    for i in range(j+1,n):
        sum += M[i,j]*x[i]

    return (x[j] + sum)**2 * norms[j]


def kfp(B, B_red, R):
    norms = norms_calc(B_red)

    B = np.array(list(B))
    B_red = np.array(list(B_red))
    n = len(B)
    M = m_matrix(B, B_red, norms, n)


    # norms2 = [norms[i]**2 for i in range(n)]
    # print('\nNorms: ', norms, '\nM_matrix:\n', M)

    x = np.zeros(n)
    c = np.zeros(n)
    l = np.zeros(n)

    S = []
    i = 0
    while i < n:
        sum = 0
        for j in range(i+1, n):
            sum += x[j] * M[j, i]
        c[i] = - sum
        l[i] = norms[i] * ((x[i] - c[i]) ** 2)

        sumli = 0
        for j in range(i, n):
           sumli += l[j]

        if sumli <= R**2:
            if i == 0:
                sum=0
                for j in range(n):
                   sum += x[j] * B[j]
                   #  sum += np.dot(x[j],B[j])
                # print("APPEND:", sum)
                S.append(sum)
                x[0] += 1
            else:
                i -= 1
                x[i] = left_bound(M, x, R, norms, i, n)
        else:
            i += 1
            # if i < n:   # in other case -> out of bounds
            #     x[i] += 1
            x[i % n] += 1   # in other case -> out of bounds
    return S
