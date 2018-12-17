from util.set import flatten

def addition_explore(graph, u, v, k):
    if k > 4:
        raise ValueError("this exploration algorithm only works for k <= 4")

    # each subgraph is either a new addition or replaces an existing subgraph
    additions = set()
    replacements = set()

    for h in range(k - 2 + 1):
        j = k - 2 - h

        u_neighborhoods = graph.n_hop_neighborhood(u, h)
        v_neighborhoods = graph.n_hop_neighborhood(v, j)

        # the common nodes in the neighborhoods
        if h < j:
            u_neighborhoods_ext = graph.n_hop_neighborhood(u, h + 1)
            common = flatten(u_neighborhoods_ext) & flatten(v_neighborhoods)
        else:
            common = flatten(u_neighborhoods) & flatten(v_neighborhoods)

        common -= set([u, v])

        for u_neighborhood in u_neighborhoods:
            for v_neighborhood in v_neighborhoods:
                # only consider disjoint neighborhoods
                # as their union will have size k
                if u_neighborhood.isdisjoint(v_neighborhood):
                    neighborhood = frozenset(u_neighborhood | v_neighborhood)

                    if (neighborhood not in additions) and \
                       (neighborhood not in replacements):
                        # only consider neighborhoods once

                        if common.isdisjoint(neighborhood):
                            # combined neighborhoods contain no common nodes
                            # add the newly created subgraph
                            additions.add(neighborhood)
                        else:
                            # combined neighborhoods contain common nodes
                            # replace the existing subgraph
                            replacements.add(neighborhood)

    return additions, replacements
