from itertools import combinations, product

def addition_explore(graph, u, v, k=4):
    if k != 4:
        raise ValueError("this exploration algorithm only works for k = 4")

    adds = set()
    reps = set()

    u_neighbors = graph.neighbors(u)
    v_neighbors = graph.neighbors(v)

    one_hop_common = u_neighbors & v_neighbors

    u_own = u_neighbors - one_hop_common

    # Cases 1 & 2: One endpoint is center of wedge or triangle, no overlap

    if len(u_own) > 1:
        adds.update([frozenset([u,v,n1,n2]) for n1,n2 in combinations(u_own, 2)])

    v_own = v_neighbors - one_hop_common

    if len(v_own) > 1:
        adds.update([frozenset([u,v,n1,n2]) for n1,n2 in combinations(v_own, 2)])

    # Case 3: One endpoint is the corner of a wedge, no overlap
    # Case 5: Edge completes a square

    u_own_two_hop_dict = graph.two_hop_neighborhood(u, u_own)
    u_own_two_hop = set(u_own_two_hop_dict.keys())

    if len(u_own_two_hop) > 0:
        adds.update([frozenset([u,v,n1,n2]) for n1 in u_own_two_hop - v_own for n2 in u_own_two_hop_dict[n1]])
        reps.update([frozenset([u,v,n1,n2]) for n1 in u_own_two_hop & v_own for n2 in u_own_two_hop_dict[n1]])

    v_own_two_hop_dict = graph.two_hop_neighborhood(v, v_own)
    v_own_two_hop = set(v_own_two_hop_dict.keys())

    if len(v_own_two_hop) > 0:
        adds.update([frozenset([u,v,n1,n2]) for n1 in v_own_two_hop - u_own for n2 in v_own_two_hop_dict[n1]])
        reps.update([frozenset([u,v,n1,n2]) for n1 in v_own_two_hop & u_own for n2 in v_own_two_hop_dict[n1]])

    # Case 4: Both endpoints have a pair, no overlap

    if len(u_own) > 0 and len(v_own) > 0:
        adds.update(frozenset([u,v,n_u,n_v]) for n_u,n_v in product(u_own, v_own) if n_v not in u_own_two_hop)

    if len(one_hop_common) > 0:

        if len(u_own) > 0:
            reps.update([frozenset([u,v,n1,n2]) for n1,n2 in product(u_own, one_hop_common)])

        if len(v_own) > 0:
            reps.update([frozenset([u,v,n1,n2]) for n1,n2 in product(v_own, one_hop_common)])

    # 4-cliques

    if len(one_hop_common) > 1:
        reps.update([frozenset([u,v,n1,n2]) for n1,n2 in combinations(one_hop_common, 2)])

    two_hop_common_dict = graph.two_hop_neighborhood(u, one_hop_common, set([v]))

    if len(two_hop_common_dict) > 0:
        reps.update([frozenset([u,v,n1,n2]) for n1 in two_hop_common_dict for n2 in two_hop_common_dict[n1]])

    return adds, reps
