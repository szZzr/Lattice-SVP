# distutils: extra_compile_args = -fopenmp
# distutils: extra_link_args = -fopenmp
import numpy as np
cimport numpy as np
cimport openmp as omp

from libc.math cimport sqrt, round, ceil
from libc.stdio cimport printf
from libc.stdlib cimport calloc, free, malloc
from cython.parallel cimport prange, parallel, threadid
from cython cimport boundscheck, wraparound, view
import cython
ctypedef long num
ctypedef double numf
cdef type d_type = np.int_
cdef type d_typef = np.float64
import pickle as pkl

from cppModules cimport abs, roundf, memcpy, Jobs, Pair


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


cdef void to_c_array(L, num** p, int n):
    '''
    Copy a python list to c-array
    
    This method pass as a reference a pointer to
    c-array in which will copy the pythonic list.
    And just modify the pointer, initialize the me-
    mory allocation and copies list's content.
    :param L: python list
    :param p: pointer of c-array
    :param n: length of python list
    :return: void
    '''
    cdef int i,j, temp
    for i,l in enumerate(L):
        p[i] = <num*>malloc(n*cython.sizeof(num))
        for j in range(n):
            p[i][j] = l[j]
    # print("\nPrint The Array\n")
    # for i in range(len(L)):
    #     printf("S[%d] = [", i)
    #     for j in range(n):
    #         printf(" %d,", p[i][j])
    #     print("\b]\n")


cdef list to_list(num*** p, int* p_points, int size_s, int n):
    '''
    Copy a c-array to python's list
    
    This method pass by reference the arguments. The first 
    argument p is a pointer to a 3dim c-array which includes the
    results of enumeration process. Each array record concerns the
    result of each iteration, each iteration result could be just an 
    empty record or a record with a plenty of numpy arrays. The argument
    p_points is a c-array of indices which defines the size of each 
    record (with results of each iteration).
    :param p: 3d c-array with vectors
    :param p_points: c-array with p's records length
    :param size_s: number or records
    :param n: size of each result (of numpy arrays)
    :return: 
    '''
    cdef:
        int i, j, s
        num **tmp_p
        list _list = []
        num[::1] tmp

    for s in range(size_s):
        for i in range(p_points[s]):
            tmp = np.empty(n, dtype=d_type)
            for j in range(n):
                tmp[j] = <num> p[s][i][j]
            _list.append(np.asarray(tmp))
    return _list


cdef inline void parallel_args(int range, int* size, int* step, int* threads):
    '''
    Set the necessary arguments for parallel execution
    
    All the arguments except the range, pass as reference cause them values
    will change according its range. First of all checks if the range is
    bigger than the threads, which is the desired, if it is, defines the number
    of subtasks as the quotient of range by threads, and adapts the division 
    remainder in the number of subtasks. And finally, defines the step of 
    parallel iteration.
    :param range: the range in which the enumeration algorithm will execute
    :param size: the size of results-array (suggests the number of iteration)
    :param step: iteration step 
    :param threads: number of parallel threads
    :return: void
    '''
    # if range > threads[0]:
    #     size[0] = <int> (range / threads[0] )
    #     if size[0] > threads[0]:
    #         size[0] -= size[0] % threads[0]
    #     else:
    #         size[0] += size[0] % threads[0]
    # else:
    #     threads[0] = size[0] = range
    # step[0] = <int> ceil(range / size[0])

    if range >= threads[0]:
        step[0] = <int> (range / threads[0] )
        size[0] = threads[0] + (range % threads[0])
    else:
        threads[0] =  size[0] = range


cdef void basic_algorithm(num[:,::1] B, numf[:,::1] M, numf[::1] norms, numf R, int n,
                          num*** _S, int* s_points, num* x,
                          size_t i_border, int lower_bound, int upper_bound) nogil:
    '''
    The backbone method of Enumeration Algorithm
    
    This method is the core of the Enumeration Algorithm, actually is an implementation
    of Schnorr and Euchner Algorithm. Using the numpy algorithms and the cython's efficient
    method to access the memory buffers typed memoryviews implements the enumeration. Each
    execution concerns a specific branch of the Enumeration Tree which has reported as subtask.
    Each one has a limit, when exceeds the limits it stops to prevent the duplication work.
    :param _S: c-array with records of results
    :param s_points: number of result of each record
    :param B: Lattice's Basis Matrix
    :param M: GSO Coefficient Matrix
    :param norms: array with norms of Basis matrix
    :param x: denotes the branch
    :param R: norm's radius (declares the upper bound of norms)
    :param n: Lattice's dimension
    :param limit: defines the value of branch's root
    :return: void
    '''
    cdef:
        int i=0, test = 0
        numf sum_li, best_norm
        num[::1] sum, dx, d2x
        numf[::1] c, l
    with gil, wraparound(False), boundscheck(False):
        c,l = np.zeros(n, dtype=d_typef), np.zeros(n, dtype=d_typef)
        sum = np.zeros(n, dtype=d_type)
        dx, d2x = np.zeros(n, dtype=d_type), (-1)* np.ones(n, dtype=d_type)
        dx[0] = 1
        d2x[0] = 1

        S=[]
        while i < i_border:
            test += 1
            c[i] = - c_(i, x, M, n)
            l[i] = norms[i]* ((x[i] - c[i]) ** 2)

            sum_li = 0
            for j in range(i, n):
                sum_li += l[j]

            # show_all(i,x, sum_li, R,n, t_id)

            if sum_li <= R**2 and i == 0:  # #NOTE: R => R**2
                sum = np.multiply(sum, 0)
                for j in range(n):
                    sum += np.multiply(x[j], np.asarray(B[j]))
                best_norm  = np.linalg.norm(sum)#**2
                if best_norm< R and best_norm>0:
                    S.append(sum)
                    show_array(sum, n, "\tvector")
                    R = best_norm
                    #break

            if sum_li <= R**2 and i>0:  # #NOTE: R => R**2
                i -= 1
                c[i] = - c_(i, x, M, n)
                x[i] = <num> roundf(c[i])
                dx[i] = 0
                d2x[i] = 1 if c[i] < x[i] else -1
            else:
                if i==i_border or (i==i_border-1 and (x[i]<lower_bound or x[i]>upper_bound)):
                    printf("\nHere has broke with i: %d\n",i)
                    break
                else:  #sum_li>R or i==0:
                    i += 1
                    d2x[i] = - d2x[i]
                    dx[i] = - dx[i] + d2x[i]
                    x[i] += dx[i]
                    if i==i_border-1 and (x[i]<lower_bound or x[i]>upper_bound):
                        printf("\nBRoooke AFTER ++ --> x[%d] = %d __ iborder-1=%d\n", i,x[i],i_border-1)
                        break

        s_points[0] = len(S) # In case where not break with the first
        printf("***Number of iteration: %d\n**Number of resutlts: %d", test, s_points[0])
        if s_points[0] >0:
            _S[0] = <num**> malloc(s_points[0]*sizeof(num*))
            to_c_array(S, _S[0], n)
            # printf("HAVE RESULTS\n")


cpdef bytes intro(int _threads, num[:,::1] B, numf[:,::1] M, numf[::1] norms,
                numf R, int n, bytes boost2): #BOOST boost1, BOOST boost2
    '''
    The main method of Enumeration Algorithm

    This method is responsible for the Schnorr and Euchner Enumeration Algorithm
    execution. Initialize the necessary parameters, deserialize the task's information,
    set the basic parameters for parallel execution. The main purpose of this method is
    the parallel execution of Enumeration Algorithm. In each parallel iteration collects the
    results of enumeration and store them in _S (c-array). Finally returns the results as a 
    pythonic list to the Worker's instance.

        #B,M,norms, R, n = unboost(boost1)
        #x, limit = unboost(boost2)
    :param _threads: 
    :param B: Lattice's Basis Matrix
    :param M: GSO Coefficient Matrix
    :param norms: array with norms of Basis matrix
    :param R: norm's radius (declares the upper bound of norms)
    :param n: Lattice's dimension
    :param boost2: Serialized version of task
    :return: serialized results list of vectors
    '''
    cdef:
        int i=0, processes, balance, width, upper_bound, lower_bound
        size_t limit, i_border, threads, t
        num*** _S
        num* x,** x_prl
        int* s_points
        list S = []
        Pair[long] task

    task.deserialize(boost2)
    i_border = task.pos # x[i_border]: VALUE NEVER CHANGE
    width = task.limit + 1 # x[index_border-1] -> [0, task.upper_bound]
    x = task.get_job()
    task.show()

    if i_border == 0:  #Server has already enumerate the branch
        printf("***i_border==0***")
        _S = <num***> malloc(sizeof(num**))
        _S[0] = <num**> malloc(n*sizeof(num*))
        s_points = <int*> calloc(1, sizeof(int))
        s_points[0] = 1
        memcpy(_S[0], x, n*sizeof(num))
        return pkl.dumps(to_list(_S, s_points, 1, n))

    if _threads>0:
        processes = width//_threads
        balance = width%_threads
        threads = balance if processes==0 else _threads
    else:
        return pkl.dumps("")

    s_points = <int*> calloc(threads, sizeof(int))
    _S = <num ***> malloc(threads * sizeof(num**))
    x_prl = <num**> malloc(threads * sizeof(num*))

    #NOTE: Create an array of x-copies "x_prl", to avoid parallel overwriting
    # because there is no way yet to define an omp private variable without #pragma
    for i in range(threads):
        x_prl[i] = <num*> malloc(n*sizeof(num))
        memcpy(x_prl[i], x, n*sizeof(num))


    omp.omp_set_num_threads(threads)
    with nogil, wraparound(False), boundscheck(False), parallel():
        for i in prange(0, threads, schedule = 'static'):
            t = i + 1
            upper_bound = processes*t - 1 + (t+balance-threads)*((t+balance)>=threads)
            lower_bound = upper_bound + 1 - processes - ((t+balance)>=threads)

            x_prl[i][i_border-1] = lower_bound

            printf("\n-%d) ThreaID: %d\tx[%d]: [%d, %d]\n",
                   t, threadid(), i_border-1, lower_bound, upper_bound)

            basic_algorithm(B, M, norms, R, n, &_S[i], &s_points[i], x_prl[i],
                            i_border, lower_bound, upper_bound)
            memcpy(x_prl[i], x, n * sizeof(num))
            printf("\nFinished the ThreadID: %d\n", threadid())

    S = to_list(_S, s_points, threads, n)

    free(_S) #It isn't the right way...
    free(s_points)
    free(x_prl)
    return pkl.dumps(S)


cdef void show_all(int i,num* x,numf sum_li,numf R, int n, int t_id):
    printf("\n\t*ThreadID: %d\n\ti: %d\n\tR: %f,\n\tsum_li: %f\n\t",t_id, i,R,sum_li)
    show_carray(x, n, "x")


cdef void show_carray(num* x,int n, char * ch):
    printf("%s = [", ch)
    for i in range(n):
        printf(" %d,", x[i])
    printf("\b ]\n")


cdef void show_array(num[::1] x,int n, char * ch):
    printf("%s = [", ch)
    for i in range(n):
        printf(" %d,", x[i])
    printf("\b ]\n")
