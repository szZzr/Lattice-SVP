cimport cython
cimport numpy as np
import numpy as np
from libc.stdlib cimport free
#include "numpy/arrayobject.h"
from libc.math cimport sqrt, round
from libc.stdlib cimport malloc, calloc
ctypedef long num
ctypedef float numf
cdef type d_type = np.long
cdef type d_typef = np.float32
from libc.stdio cimport printf

cdef num[::1] norms_calc(num[:,::1] B, int n):
    cdef:
        int i
        num[::1] norms = np.zeros(n, dtype= d_type)
    for i in range(n):
        norms[i] = np.linalg.norm(B[i])
    return norms


cdef numf[:,::1] m_matrix(num[:,::1] B, num[:,::1] B_red, int n, numf[::1] norms):
    cdef:
        numf[:,::1] m = np.tril(np.ones(n, dtype= d_typef), -1)
        int m_len = <int>(n**2 - n)/2
        int i,x,y,index
        num[::1] a
    for i in range(m_len):
        x = <int> (1 + sqrt(<long> (8*i+1)))/2
        y = i%x
        a = np.multiply(B_red[x],B[y], dtype = d_type)
        # a = np.dot(B_red[x],B[y])
        index = x if norms[x] > norms[y] else y
        m[x,y] = np.linalg.norm(np.divide(a, norms[index]**2))
    return m


cdef inline numf c_calc(int i, num[::1] x, numf[:,::1] M, int n):
    cdef:
        int j
        numf sum=0
    for j in range(i+1, n):
        sum += x[j]*M[j, i]
    return -sum


cpdef list schnorr_euchner(num[:,::1] B, num[:,::1] B_red, int R):      #ta inputs tha einai numpy arrays
    cdef:
        int i=0, j, n = B.shape[0], dim = B.shape[1]
        numf sum_li
        num[::1] sum, temp, x,dx,d2x
        numf[::1] norms, c,l
        numf[:,::1] M
        list S = []

    norms= np.linalg.norm(B_red,axis=1).astype(d_typef) #to allaksa
    M = m_matrix(B, B_red, n, norms)
    sum = np.zeros(n, dtype=d_type)
    x = np.zeros(n, dtype=d_type)
    c = np.zeros(n, dtype=d_typef)
    l = np.zeros(n, dtype=d_typef)
    dx = np.zeros(n, dtype=d_type)
    d2x =  (-1) * np.ones(n, dtype=d_type)
    dx[0] = 1
    d2x[0] = 1

    while i<n:
        c[i] = c_calc(i,x,M,n)
        l[i] = norms[i] * ((x[i] - c[i]) ** 2)

        sum_li = 0
        for j in range(i,n):
            sum_li += l[j]

        if sum_li<= R**2 and i==0:
            sum = np.dot(sum,0)     # .astype(d_type)
            for j in range(n):
                temp = np.asarray(B[j:j+1]).reshape(dim)
                sum += np.dot(temp, x[j])   # .astype(d_type)
            S.append(sum)
        if sum_li <= R**2 and i > 0:
            i -= 1
            c[i] = c_calc(i,x,M,n)
            x[i] = <num>round(c[i])
            dx[i] = 0
            d2x[i] = 1 if c[i] < x[i] else -1
        elif i == n:
            break
        else:
            i += 1
            if i<n:
                d2x[i] = -1*d2x[i]
                dx[i] = dx[i] + d2x[i]
                x[i] += dx[i]

    return S


def show(*args):
    print("---norms---\n",np.array(args[0]))
    print("\n---sum---\n", np.array(args[1]))
    print("\n---M---\n", np.array(args[2]))
    print("\n---x---\n", np.array(args[3]))
    print("\n---c---\n", np.array(args[4]))
    print("\n---l---\n", np.array(args[5]))
    print("\n---dx---\n", np.array(args[6]))
    print("\n---d2x---\n", np.array(args[7]))
