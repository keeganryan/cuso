import logging

from sage.all import Matrix

from .utils import lm_no_N, lc_no_N, monom_no_N, coeff_no_N

logger = logging.getLogger("cuso.symbolic.Optimal")

def get_S_from_S_bar(R, M_bar, S_bar, M):
    assert set(M).issubset(set(M_bar))
    if len(M) == len(M_bar):
        return S_bar
    
    # Get basis of linear span
    B = Matrix(R, len(S_bar), len(M_bar))

    assert M_bar[:len(M)] == M
    for i, f_i in enumerate(S_bar):
        for j, m_j in enumerate(M_bar):
            c_ij = coeff_no_N(f_i, m_j)
            B[i,j] = c_ij

    B = B[::-1,::-1].echelon_form()[::-1,::-1]

    # Convert back to S
    S = []
    for i in range(len(S_bar)):
        if B[i][-len(M_bar)+len(M):] != 0:
            continue
        f_i = 0
        for j, (c_j, m_j) in enumerate(zip(B[i], M)):
            f_i += c_j * m_j
        S += [f_i]
    return S

def get_optimal_shift_polys(M, J, skip_reduce=False):
    # X bounds are implicit in the TermOrder contained in J
    logger.debug("Getting optimal shift polys in ideal")

    logger.debug("Computing Groebner basis")
    G = J.groebner_basis()
    R = J.ring()

    lc_no_N(G[-1])

    logger.debug("Initializing queue")
    M = sorted(M)
    M_queue = M[:]
    M_bar = M[:]
    S_bar = []

    logger.debug("Getting S_bar")
    S_bar = []
    G_lms = [(g, lm_no_N(g)) for g in G]
    while len(M_queue) > 0:
        m = M_queue.pop(0)

        T = [g for g, g_lm in G_lms if m % g_lm == 0]
        if len(T) != 0:
            # Smallest leading coefficient
            g = min(T, key=lc_no_N)
            h = (m / lm_no_N(g)) * g
            h = R(h)
            if skip_reduce:
                h_prime = h
            else:
                h_prime = h.lt() + J.reduce(h - h.lt())
            S_bar += [h_prime]

            # If there are any new monomials, add them to the queue
            for monom in h_prime.monomials():
                monom = monom_no_N(monom)
                if monom not in M_bar:
                    M_bar += [monom]
                    M_queue += [monom]

    logger.debug("Getting S")
    S = get_S_from_S_bar(R, M_bar, S_bar, M)
    
    return S
