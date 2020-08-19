import numpy as np
from numpy import linalg as la
from math import sqrt
import time

def norms_calc(B):
    n = B.nrows
    norms = [B[i].norm() for i in range(n)]
    return norms


def m_matrix(B, B_red, norms, n):
    m1 = np.tril(np.ones((n, n)), -1)
    m_len = int((n ** 2 - n) / 2)  # number of down-tri
    for i in range(m_len):
        x = int((1 + sqrt(8*i+1))/2)
        y = i%x
        a = (B_red[x] * B[y]).astype(float)
        if norms[x] > norms[y]:
            m1[x, y] = la.norm(a / (norms[x] ** 2))
        else:
            m1[x, y] = la.norm(a / (norms[y] ** 2))
    return m1


def c_calc(i, x, M, n):
    sum = 0
    for j in range(i + 1, n):
        sum += x[j] * M[j, i]
    return -sum


def schnorr_euchner(B, B_red, R):
    norms = norms_calc(B_red)

    B = np.array(list(B))
    B_red = np.array(list(B_red))
    n = len(B)
    M = m_matrix(B, B_red, norms, n)
    norms2 = [norms[i] ** 2 for i in range(n)]
    # print('\nNorms: ', norms2, '\nM_matrix:\n', M)

    x = np.zeros(n)
    c = np.zeros(n)
    l = np.zeros(n)
    dx = np.zeros(n)
    d2x = (-1) * np.ones(n)
    dx[0] = 1
    d2x[0] = 1

    S = []
    i = 0


    while i < n:
        c[i] = c_calc(i, x, M, n)
        l[i] = norms[i] * ((x[i] - c[i]) ** 2)

        sumli = 0
        for j in range(i, n):
            sumli += l[j]


        if sumli <= R**2 and i == 0:
            sum = 0
            for j in range(n):
                sum += x[j] * B[j]
            S.append(sum)
        if sumli <= R**2 and i > 0:
            i -= 1
            c[i] = c_calc(i, x, M, n)
            x[i] = round(c[i])     # kati paizei edo
            dx[i] = 0
            d2x[i] = 1 if c[i] < x[i] else -1
        elif i == n:
            break
        else:
            i += 1
            if i<n:
                d2x[i] = -d2x[i]
                dx[i] = -dx[i] + d2x[i]
                x[i] += dx[i]
    return S





