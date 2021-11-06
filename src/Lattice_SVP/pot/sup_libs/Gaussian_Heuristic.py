from fpylll import *
import numpy as np
from fpylll.util import set_random_seed,ball_log_vol,gaussian_heuristic

def gh(B,par): #norm of the shortest vector given by GH
    M = GSO.Mat(B)  # this is floating point Gram-Schmidt
    M.update_gso()
    rows = B.nrows
    gram_matrix = [M.get_r(k,k) for k in range(rows)]

    return par * np.sqrt(gaussian_heuristic(gram_matrix))


