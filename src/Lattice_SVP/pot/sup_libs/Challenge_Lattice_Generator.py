import numpy as np
from numpy import matrix
from numpy import random
from fpylll import IntegerMatrix

def fp2mat(A):
    L = np.zeros(shape=(A.nrows,A.ncols))
    for i in range(A.nrows):
        for j in range(A.ncols):
            L[i,j] = A[i,j]
            L = matrix(L)
    return L

def mat2fp(A):
    L = IntegerMatrix(A.shape[0],A.shape[1])
    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            L[i,j] = int(A[i,j])
    return L

def generate_knapsack_matrices(n,b):
    # n : dimension
    # b : bits
    A = IntegerMatrix.random(n-1, "intrel", bits = b)
    B = fp2mat(A)
    List = [random.randint(2**b)] + [0]*(n-1)
    C = np.append(B, np.array([ List ]), axis=0)
    D = np.roll(C,-n+1,axis=0)
    E = mat2fp(D)
    # print(E)
    return E

