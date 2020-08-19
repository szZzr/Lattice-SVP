from fpylll import LLL, BKZ


def lll(basis):
    basis_lll = LLL.reduction(basis)
    if LLL.is_reduced(basis_lll):
        return basis_lll
    else:
        return bkz(basis, 3)


def bkz(basis, block_size):
    param = BKZ.Param(block_size=block_size, strategies=BKZ.DEFAULT_STRATEGY)
    basis_bkz = BKZ.reduction(basis, param)
    return basis_bkz

