from collections import namedtuple

SubgraphEdge = namedtuple('SubgraphEdge', ['u', 'v', 'label'])
Subgraph = namedtuple('Subgraph', ['nodes', 'edges'])
