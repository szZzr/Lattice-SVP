from Package.BasisProduction import basis_gen
from Package.LatticeReduction import lll, bkz
from Package.KFP import kfp
from Package.SchnorrEuchner import schnorr_euchner as schnorr
from copy import copy
from fpylll import *
import C_SchnorrEuchner
import C2_SchnorrEuchner
import time
import numpy as np
from numpy.linalg import norm


def basis_setter(red_method):
    # basis = basis_gen("u", 30)
    # basis = IntegerMatrix.from_matrix([[3, 11, 12], [6, 3, 12], [13, 15, 0]])
    # basis = IntegerMatrix.from_matrix([[3, 6, 13],[11, 3, 15],[12, 12, 0]])
    basis = IntegerMatrix.from_matrix([[2, 7, 7, 5], [3, -2, 6, -1], [2, -8, -9, -7], [8, -9, 6, -4]])
    # basis = IntegerMatrix.from_matrix([[-2, 7, 7, -5], [3, -2, 6, -1], [2, -8, -9, -7], [8, -9, 6, -4]])
    # print("Basis\n", basis)
    if red_method == "lll":
        red_basis = lll(copy(basis))
    else:
        red_basis = bkz(basis, block_size=3)
    # print("\nReduced-Basis\n", red_basis)
    # print('Lattice:\n', basis, '\n\nLLL-Lattice:\n', red_basis)
    return basis, red_basis


def search_for_variants(S, S2):
    variant = []
    for i in range(len(S2)):
        flag = True
        for j in range(len(S)):
            if S2[i].tolist() == S[j].tolist():
                flag = False
        if flag:
            variant.append(S2[i])
    return variant


def show_results(t1,t2,S, name):
    print(name, "\n\tDuration:", t2 - t1, "\n\tResults","\n\tSize:", len(S))
    for i in range(len(S)):
        print(i, " -> ", np.asarray(S[i]), "\t => norm: ", norm(S[i]))


def results_comparison(s1, s2, s3, s4, s5, S, S2, S3):
    # show_results(s1,s2,S,"KFP")
    show_results(s4, s5, S3, "C1 ---Schnorr und Euchner")
    show_results(s2, s3, S2, "C2 --- Schnorr und Euchner")

    # print("Benchmarks -> SE vs KFP: ", round(100 * (-s3 + s2 + s2 - s1) / (s3 - s2), 2), "%  speed")
    print("Benchmarks -> cSE vs pSE: ", round(100 * (-s5 + s4 + s3 - s2) / (s5 - s4), 2), "%  speed")

    # variant = search_for_variants(S2, S3)
    #
    # print("\n\nComparison: ", variant)


def to_np_array(b, b_red):
    dtype = np.long
    return np.array(list(b), dtype=dtype), np.array(list(b_red), dtype=dtype)


def SVP(basis, red_basis, R):
    # s1 = time.time()
    # S = kfp(basis, red_basis, R)
    S=[]
    b, b_red = to_np_array(basis, red_basis)

    s4 = time.time()
    S3 = C_SchnorrEuchner.schnorr_euchner(b, b_red, R)
    s5 = time.time()

    s2 = time.time()
    S2 = C2_SchnorrEuchner.schnorr_euchner(b, b_red, R)
    s3 = time.time()

    # s2 = time.time()
    # S2 = schnorr(basis, red_basis, R)
    # s3 = time.time()


    results_comparison(0, s2, s3, s4, s5, S, S2, S3)


def main():
    R = 5
    basis, red_basis = basis_setter("lll")
    SVP(basis, red_basis, R)


main()
# if __name__ == '__main__':
#     import cProfile
#     cProfile.run('main()', sort='time')
