def addition_explore(graph, u, v, k=3):
    if k != 3:
        raise ValueError("this exploration algorithm only works for k = 3")

    u_neighbors = set([u_nbr.to_node() for u_nbr in graph.neighbors(u)])
    v_neighbors = set([v_nbr.to_node() for v_nbr in graph.neighbors(v)])

    common = u_neighbors & v_neighbors

    additions = set()
    additions.update([frozenset([u, v, n_u]) for n_u in u_neighbors - common])
    additions.update([frozenset([u, v, n_v]) for n_v in v_neighbors - common])

    replacements = set([frozenset([u, v, n_b]) for n_b in common])

    return additions, replacements
