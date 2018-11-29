from .graph_edge import Edge

# factory method to ensure sorted node order in edges
def make_edge(a, b, label):
    if b < a: (b, a) = (a, b)
    return Edge(*a, *b, label)
