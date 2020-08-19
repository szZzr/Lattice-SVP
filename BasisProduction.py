from fpylll import IntegerMatrix
import random


def basis_gen(option, dim):
    basis = IntegerMatrix(dim, dim)
    bits = 10
    categories = {"u": uniform,
                  "n": ntru,
                  "n2": ntru2,
                  "q": qary,
                  "s": simdioph}
    return categories[option](basis, bits)


def uniform(basis, bits):
    '''
    "uniform" - generate a d x d matrix whose entries are
    independent integers of bit-lengths <=bits.
    :param basis:
    :return:
    '''
    basis.randomize("uniform", bits=bits)
    return basis


def ntru(basis, bits):
    '''
    "ntrulike" - generate an NTRU-like matrix. If bits is given,
    then it first samples an integer q of bit-length <=bits,
    whereas if q, then it sets q to the provided value. Then
    it samples a uniform h in the ring Z_q[x]/(x^n-1). It finally
    returns the 2 x 2 block matrix [[I, Rot(h)], [0, q*I]], where
    each block is d x d, the first row of Rot(h) is the coefficient
    vector of h, and the i-th row of Rot(h) is the shift of
    the (i-1)-th (with last entry put back in first position), for
    all i>1. Warning: this does not produce a genuine ntru lattice
    with h a genuine public key.
    :param basis:
    :return:
    '''
    limit = int(''.join(['1' for i in range(bits)]), 2)
    q = random.randrange(limit)
    basis.randomize("ntrulike", bits=bits, q=q)
    return basis


def ntru2(basis, bits):
    '''
    ntrulike2" : as the previous option, except that the constructed matrix
    is [[q*I, 0], [Rot(h), I]].
    :param basis:
    :return:
    '''
    limit = int(''.join(['1' for i in range(bits)]), 2)
    q = random.randrange(limit)
    basis.randomize("ntrulike2", bits=bits, q=q)
    return basis


def qary(basis, bits):
    '''
    "qary" : generate a q-ary matrix. If bits is given, then it first samples
    an integer q of bit-length <=bits; if q is provided, then set q to the provided
    value. It returns a 2 x 2 block matrix [[q*I, 0], [H, I]], where H is k x (d-k)
    and uniformly random modulo q. These bases correspond to the SIS/LWE q-ary
    lattices. Goldstein-Mayer lattices correspond to k=1 and q prime.
    :param basis:
    :return:
    '''
    limit = int(''.join(['1' for i in range(bits)]), 2)
    q = random.randrange(limit)
    basis.randomize("qary", bits=bits, q=q, k=1)
    return basis


def simdioph(basis, bits):
    bits2 = bits-1
    '''
    "simdioph" - generate a d x d matrix of a form similar to that is involved when trying to
    find rational approximations to reals with the same small denominator. The first vector starts
    with a random integer of bit-length <=bits2 and continues with d-1 independent integers of
    bit-lengths <=bits; the i-th vector for i>1 is the i-th canonical unit vector scaled by a
    factor 2^b.
    :param basis:
    :return:
    '''
    basis.randomize("simdioph", bits=bits, bits2=bits2)
    return basis

