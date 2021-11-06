# distutils: extra_compile_args = -fopenmp
# distutils: extra_link_args = -fopenmp
# distutils: language=c++
# cython: language_level=3

import numpy as np
cimport numpy as np
import pickle as pkl

from numpy import linalg as la
from cython.parallel cimport prange, parallel, threadid
from cython cimport boundscheck, wraparound, view
from libc.stdio cimport printf
from libc.stdlib cimport calloc, free, malloc

from cppModules cimport sqrt, ceil
from cppModules cimport JobsPair
from cppModules cimport VIA_NODES as c_NODES
from cppModules cimport VIA_DEPTH as c_DEPTH

ctypedef long num
ctypedef double numf
cdef type d_type = np.int_
cdef type d_typef = np.float64


cdef inline numf c_(int i, num* x, numf[:,::1] M, int n):
    '''
    Sum of products of the GSO and Basis coefficients

    This is an inline function which has a lot of calls. The
    first idea was to make a parallel implementation but the 
    parallel setting overhead increase the execution time, so
    preferred the linear one.
    :param i: the index of matrix-M
    :param x: basis coefficients
    :param M: the matrix of GSO coefficients
    :param n: lattice's rank
    :return: sum of product
   '''
    cdef:
        int j
        numf sum=0
    for j in range(i+1, n):
        sum += x[j]*M[j, i]
    return sum


cdef numf quot(int i,numf[::1] norms, num* x,numf[:,::1] M, int n,numf R):
    cdef:
        numf[::1] c
        numf suml = 0
        int j
    c = np.zeros(n, dtype=d_typef)
    c[i] = c_(i, x, M, n)
    for j in range(i+1,n):
        suml += norms[j] * ((x[j] - c[j]) ** 2)
        printf("\n\tTo j:%d --> li:%f", j, suml)
    printf("\n\t quotient: %f - %f/%f", R**2, suml, norms[i])
    return sqrt(R**2 - suml)/norms[i]
#fad

cdef num[::1] norms_calc(num[:,::1] B, int n):
    '''
    Calculates the norms of array with ndarrays
    
    This simple function takes as arguments a typed
    memoriview (efficient cython's method to access the
    memory buffer) which refers to some numpy arrays (ndarrays), 
    and estimates the norm of each numpy array.
    :param B: Typed memoryview of ndarrays
    :param n: size of memory buffer with ndarrays
    :return: Typed memoryview of norms
    '''
    cdef:
        int i
        num[::1] norms = np.zeros(n, dtype= d_type)
    for i in range(n):
        norms[i] = np.linalg.norm(B[i])**2
    return norms

@wraparound(False)
@boundscheck(False)
cdef num[:,::1] gso(numf[:,::1] M, num[:,::1] B):
    '''
    Estimation of GSO Coefficients
    
    This method implements the Gram Schmidt Algorithm which
    estimates the coefficients of GSO matrix and the orthogonal
    lattice's basis.
    :param M: GSO Coefficients
    :type M: Typed Memoryview (access to ndarray)
    :param R: Lattice's Basis 
    :type R: Typed Memoryview (access to ndarray)
    :param n: Lattice's dimension
    :return: void
    '''
    cdef:
        # int m_len = <int> ( (n**2 - n)/2 )
        int i,j,n
        num norm
        numf dot
        numf[::1] proj, t1,t2,t3
        num[::1] temp
        num[:,::1] R
    # B = np.copy(R)
    # for x in range(m_len):
    #     i = <int> ((1 + sqrt(<long> (8 * x + 1))) / 2)
    #     j = x % i
    #     M[i, j] = (np.dot(B[i], R[j])) / (la.norm(R[j]) ** 2)
    #     b = B[i] - np.multiply(B[i], M[i, j], casting='unsafe', dtype=d_type)
    #     R[i,:] = b
    n = B.shape[0]
    R = np.copy(B)
    for i in range(n):
        t1 = np.copy(B[i]).astype(dtype=d_typef, casting='unsafe')
        t2 = np.copy(t1)
        t3 = np.copy(t1)
        for j in range(i-1,-1,-1):
            # dot = <numf>(np.dot(t1,R[j]))
            # norm = <num>(la.norm(R[j])**2)
            # M[i,j] = dot/norm
            # proj = np.multiply(M[i,j],R[j])
            # t2 = np.subtract(t3, proj)
            M[i, j] = np.dot(t1,R[j])/ (la.norm(R[j])**2)
            t2 = np.subtract(t3, np.multiply(M[i,j],R[j]), dtype=d_typef)
            t3 = np.copy(t2)
        temp =  np.copy(t2).astype(dtype=d_type, casting = 'unsafe')
        R[i] = temp
    return R


@wraparound(False)
@boundscheck(False)
cdef void gso_parallel(numf[:,::1] M, np.ndarray[num, ndim=2] R, int n):
    '''
    Parallel Estimation of GSO Coefficients
    
    This method includes the parallel implementation of the Gram Schmidt 
    Algorithm whichb estimates the coefficients of GSO matrix and the 
    orthogonal lattice's basis.
    :param M: GSO Coefficients
    :type M: Typed Memoryview (access to ndarray)
    :param R: Lattice's Basis 
    :type R: Typed Memoryview (access to ndarray)
    :return: void
    '''
    cdef:
        int m_len = <int> ( (n**2 - n)/2 )
        int i,j,x, chunk, threads
        np.ndarray[num, ndim=2] B
    threads = <int> _threads
    B = np.copy(R)
    chunk = <int> ((n*0.8)/threads)
    with nogil, parallel(num_threads=threads):
        for x in prange(m_len,schedule='static'): #schedule='dynamic',chunksize=chunk
            i = <int> ((1 + sqrt(<long> (8 * x + 1))) / 2)
            j = x % i
            with gil:
                M[i, j] = (np.dot(B[i], R[j])) / (la.norm(R[j]) ** 2)
                R[i] = B[i] - np.multiply(B[i],M[i, j], casting='unsafe',dtype=d_type)


cdef inline void distr_args(int range, size_t* size, int* tasks):
    if range > tasks[0]:
        size[0] = <int> (range / tasks[0] )
        if size[0] > tasks[0]:
            size[0] -= size[0] % tasks[0]
        else:
            size[0] += size[0] % tasks[0]
    else:
        tasks[0] = size[0] = range
    printf("\nIn function tasks: %d\n",tasks[0])


cdef void show_2d_matrixf(numf[:,::1] x, char* str):
    cdef int i, n= x.shape[0]
    printf("\n\n%s\n", str)
    for i in range(n):
        printf("[ ")
        for j in range(n):
            printf(" %f,",x[i,j])
        printf("\b]\n")


cdef void show_2d_matrix(num[:,::1] x, char* str):
    cdef int i, n= x.shape[0]
    printf("\n\n%s\n", str)
    for i in range(n):
        printf("[ ")
        for j in range(n):
            printf(" %d,",x[i,j])
        printf("\b]\n")


cdef void show_1d_matrix(num[::1] x, char* str):
    cdef int i, n= x.shape[0]
    printf("\n\n%s\n[ ", str)
    for i in range(n):
        printf(" %d,",x[i])
    printf("\b]\n")


cdef void show_1d_matrixf(numf[::1] x, char* str):
    cdef int i, n= x.shape[0]
    printf("\n\n%s\n[ ", str)
    for i in range(n):
        printf(" %f,",x[i])
    printf("\b]\n")


# cpdef dict algorithm(num[:,::1] B, numf R, int tasks):
#     cdef:
#         int i=0, n = B.shape[0], r, limit, index=0, width=0
#         numf[::1] norms
#         numf[:,::1] M
#         num[:,::1] _B
#         Jobs[long] * jobs
#         bytes b_infos
#         list b_jobs
#         numf _ssum, _quot
#         num* x
#     global _threads
#     _threads = 4
#
#     jobs = new Jobs(size_job=n)
#     M = np.tril(np.ones([n,n], dtype=d_typef))
#     _B = gso(M,B)
#     norms= la.norm(_B,axis=1).astype(d_typef)
#     show_2d_matrixf(M,"GSO COEFF")
#     show_2d_matrix(_B, "NEW BASIS")
#     # if _threads==1:
#     #     gso(M, B, n)
#     # else:
#     #     gso_parallel(M, np.asarray(B), n)
#
#     x = <num*> calloc(n, sizeof(num))
#     x[n-1] = 0
#     i = 1
#     _ssum = - c_(i, x, M, n)
#     _quot = quot(i, norms, x, M, n, R)
#
#     printf("\n\nSUM: %f\n\n", _ssum)
#     printf("\nByTheBook\t Interval-X%d: [ %f, %f ]",i, _ssum -_quot, _ssum + _quot )
#
#
#     r = <int> (R**2/norms[0])
#     #TODO: SHOULD FIX THE SIZE!!!
#     width = r + 1 # +1 --> corresponds to 0
#     step = tasks/width
#     if tasks>width:
#         tasks= width
#     elif step > ceil(step):
#         tasks = tasks + 1
#
#     # distr_args(2*r+1, &size_s, &tasks)
#     printf("\nRange: %d\n",width)
#     printf("\nNumber of tasks: %d\n", tasks)
#
#     # BOOST 2 ---->  ( x,limit )
#     # test_serialized = jobs.serialize(jobs[0])
#     #TODO: Resize the number of tasks base the cpp
#     jobs.set_parameters(range = r, size_jobs=tasks)
#     jobs.set_jobs()
#     jobs.show()
#     b_jobs = []
#     for i in range(tasks):
#         b_jobs.append(jobs.next_pair())
#
#
#     #BOOST 1 --->  ( B,M, norms, R, n )
#     b_infos = pkl.dumps({'B':np.asarray(B),
#                          'M':np.asarray(M),
#                          'norms':np.asarray(norms),
#                          'R':R, 'n':n})
#
#     return {'boost1':b_infos, 'boost2':b_jobs}

ctypedef enum CONDITION:
    VIA_DEPTH = 0
    VIA_NODES = 1


cpdef dict algorithm(num[:,::1] B, numf R, size_t condition, size_t tasks):
    cdef:
        size_t n = B.shape[0], i=0
        numf[::1] norms
        numf[:,::1] M
        num[:,::1] _B
        JobsPair[long, double] *jobs
        bytes b_infos
        list b_jobs
        char* task

    global _threads
    _threads = 4

    if condition == VIA_DEPTH:
        print('CONDITION VIA_DEPTH')
        jobs = new JobsPair(request=tasks, dims=n, R=R, condition=c_DEPTH)
        #tasks = n if tasks>n else tasks
    elif condition == VIA_NODES:
        print('CONDITION VIA_NODES')
        jobs = new JobsPair(request=tasks, dims=n, R=R, condition=c_NODES)
        #tasks = jobs.get_size_jobs()
    else:
        print('NO CONDITION')
        return

    M = np.tril(np.ones([n,n], dtype=d_typef))
    _B = gso(M,B)
    norms= la.norm(_B,axis=1).astype(d_typef)
    # norms= np.power(norms,2).astype(d_typef)
    # show_2d_matrixf(M,"GSO COEFF")
    # show_2d_matrix(_B, "NEW BASIS")

    # NOTE: BOOST 2 ---->  ( x,limit )
    show_1d_matrixf(norms, "NORMS")
    # show_2d_matrixf(M, "GSO")
    jobs.set_parameters(&norms[0], &M[0,0])
    jobs.set_jobs()
    jobs.show()
    tasks = jobs.get_size_jobs()
    b_jobs = [jobs.next_pair() for _ in range(tasks)]
    del jobs

    # NOTE: BOOST 1 --->  ( B,M, norms, R, n )
    b_infos = pkl.dumps({'B':np.asarray(B),
                         'M':np.asarray(M),
                         'norms':np.asarray(norms),
                         'R':R, 'n':n})

    return {'boost1':b_infos,'boost2':b_jobs}




# cdef extern from "cpp_extras/jobs/Jobs.hpp":
#     cdef cppclass Condition:
#         pass
#
#
# cdef extern from "cpp_extras/jobs/Jobs.hpp" namespace "Condition":
#     cdef Condition VIA_NODES
#     cdef Condition VIA_DEPTH
#
#
# cdef extern from "cpp_extras/jobs/Jobs.hpp":
#     cdef enum  _Condition 'Condition':
#         _VIA_NODES 'Condition::VIA_NODES'
#         _VIA_DEPTH 'Condition::VIA_DEPTH'

# cdef extern from "cpp_extras/jobs/JobsEstimator.h":
#     cdef enum CONDITION "Condition":
#         VIA_NODES, VIA_DEPTH
