from fpylll import LLL, BKZ, GSO, IntegerMatrix
from fpylll import Enumeration

def _gso(basis):
    #basis_gso = GSO.Mat(basis)
    basis_gso = GSO.Mat(basis, flags=GSO.INT_GRAM,float_type='mpfr')
    basis_gso.update_gso()
    return basis_gso

def gso(basis):
    return _gso(basis).G

def lll(basis):
    basis_lll = LLL.reduction(basis)
    if LLL.is_reduced(basis_lll):
        return basis_lll
    else:
        return bkz(basis, 3)


def _bkz(basis, block_size):
    lll = LLL.Reduction(basis)
    param = BKZ.Param(block_size=block_size, strategies=BKZ.DEFAULT_STRATEGY)
    basis_bkz = BKZ.Reduction(basis, lll, param)
    return basis_bkz

def bkz_object(basis, block_size):
    return _bkz(_gso(basis), block_size)

def bkz(basis, block_size):
    param = BKZ.Param(block_size=block_size, strategies=BKZ.DEFAULT_STRATEGY)
    # print("**GSO COEF**\n\n", _gso(basis).B)
    return BKZ.reduction(basis, param)


def enumeration(matrix):
    lll = LLL.reduction(matrix)
    m = GSO.Mat(lll)
    m.update_gso()
    e = Enumeration(m)
    _, v1 = e.enumerate(0, m.d, m.get_r(0,0),0)[0]
    # v1 =
