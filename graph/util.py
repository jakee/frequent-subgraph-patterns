from .graph_edge import Edge

# factory method to ensure sorted node order in edges
def make_edge(u, l_u, v, l_v, q_uv):
    if v < u: u, l_u, v, l_v = v, l_v, u, l_u
    return Edge(u, l_u, v, l_v, q_uv)
