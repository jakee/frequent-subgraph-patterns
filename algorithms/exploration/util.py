from . import optimized_triplet
from . import optimized_quadruplet


def new_subgraphs_func(k):
    if k == 3:
        return optimized_triplet.get_new_subgraphs
    elif k == 4:
        return optimized_quadruplet.get_new_subgraphs
    else:
        raise ValueError("no function available for k = %d" % (k))


def all_subgraphs_func(k):
    if k == 3:
        return optimized_triplet.get_all_subgraphs
    elif k == 4:
        return optimized_quadruplet.get_all_subgraphs
    else:
        raise ValueError("no function available for k = %d" % (k))
