def get_new_subgraphs(graph, k, u, v):
    if k != 3:
        raise ValueError("this exploration algorithm only works for k = 3")

    N_u = graph.neighbors(u)
    N_v = graph.neighbors(v)

    return set(frozenset([u, v, w]) for w in (N_u ^ N_v))


def get_all_subgraphs(graph, k, u, v):
    if k != 3:
        raise ValueError("this exploration algorithm only works for k = 3")

    N_u = graph.neighbors(u)
    N_v = graph.neighbors(v)

    additions = set(frozenset([u, v, w]) for w in (N_u ^ N_v))
    replacements = set(frozenset([u, v, w]) for w in (N_u & N_v))

    return additions, replacements
