cimport cython
cimport numpy as np
import numpy as np
from libc.math cimport sqrt, round, pow
from libc.stdlib cimport malloc, calloc, free
ctypedef long num
ctypedef float numf
cdef type d_type = np.long
cdef type d_typef = np.float32
from libc.stdio cimport printf


cdef void m_matrix(numf** M, numf* norms, num[:,::1] B, num[:,::1] B_red, int n):
    cdef:
        int i, x, y, j
        int m_len = <int> (n**2 - n)/2
        num[::1] a
        numf the_norm
    for i in range(m_len):
        x = <int> (1 + sqrt(<long> (8*i+1)))/2
        y = i%x
        a = np.multiply(B_red[x], B[y], dtype = d_type)
        the_norm = norms[x]**2 if norms[x] > norms[y] else norms[y]**2
        for j in range(n):
            M[x][y] += (a[j]/the_norm)**2
        M[x][y] = <numf> sqrt(M[x][y])

cdef inline numf c_calc(numf** M, num* x,  int i, int n):
    cdef:
        int j
        numf sum=0
    for j in range(i+1, n):
        sum += x[j]*M[j][i]
    return -sum


cdef inline void mem_free(int n, num* x, num* dx, num* d2x,
                             numf* norms, numf* l, numf** M, numf* c):
    free(norms)
    free(x)
    free(dx)
    free(d2x)
    free(c)
    free(l)
    free(M)

cpdef list schnorr_euchner(num[:,::1] B, num[:,::1] B_red, int R):
    cdef:
        int i=0, j, n = B.shape[0], dim = B.shape[1]
        numf sum_li
        num *x, *dx, *d2x
        numf *norms,*c,*l
        numf **M
        num[::1] sum, temp
        list S = []

    norms = <numf *> calloc(n,sizeof(numf))
    x = <num *> calloc(n, sizeof(num))
    dx = <num *> calloc(n, sizeof(num))
    d2x = <num *> malloc(n*sizeof(num))
    c = <numf *> calloc(n, sizeof(numf))
    l = <numf *> calloc(n, sizeof(numf))
    M = <numf **> calloc(n, sizeof(numf*))
    sum = np.zeros(n, dtype=d_type)

    try:
        for i in range(n):
            d2x[i] = -1
            M[i] = <numf*> calloc(dim,sizeof(numf*))
            for j in range(dim):
                norms[i] += B_red[i,j]**2
            norms[i] = sqrt(norms[i])
        m_matrix(M, norms, B, B_red, n)

        while i<n:
            c[i] = c_calc(M,x,i,n)
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
                c[i] = c_calc(M,x,i,n)
                x[i] = <num> round(c[i])
                dx[i] = 0
                d2x[i] = 1 if c[i] < x[i] else -1
            elif i == n:
                break
            else:
                i += 1
                if i<n:
                    d2x[i] = -d2x[i]
                    dx[i] = dx[i] + d2x[i]
                    x[i] += dx[i]
    finally:
        mem_free(n,x,dx,d2x,norms,l,M,c)
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
