import numpy as np

from collections import defaultdict

class SubgraphReservoir:
    subgraphs = None
    vertex_subgraphs = None

    def __init__(self, size):
        self.max_size = size
        self.subgraphs = []
        self.subgraph_indices = {}
        self.vertex_subgraphs = defaultdict(set)


    def __contains__(self, subgraph):
        return subgraph in self.subgraphs


    def __len__(self):
        return len(self.subgraphs)


    def is_full(self):
        return len(self.subgraphs) >= self.max_size


    def add(self, subgraph, N=float('-inf')):
        success = False
        old_subgraph = None

        if subgraph not in self.subgraph_indices:

            if self.is_full():
                # the reservoir is full, so we replace an existing subgraph
                old_subgraph = self.random(N=N)

                if old_subgraph:
                    self.replace(old_subgraph, subgraph)
                    success = True

            else:
                # the reservoir is not full, so we add the new subgraph
                idx = len(self.subgraphs)
                self.subgraphs.append(subgraph)

                self.subgraph_indices[subgraph] = idx

                for u in subgraph.nodes:
                    self.vertex_subgraphs[u].add(idx)

                success = True

        return success, old_subgraph


    def replace(self, old_subgraph, new_subgraph):
        idx = self.subgraph_indices[old_subgraph]
        del self.subgraph_indices[old_subgraph]

        self.subgraphs[idx] = new_subgraph
        self.subgraph_indices[new_subgraph] = idx

        # change the subgraphs by vertex mapping only if necessary
        old_nodes = set(old_subgraph.nodes)
        new_nodes = set(new_subgraph.nodes)

        for u in new_nodes - old_nodes:
            self.vertex_subgraphs[u].add(idx)

        for v in old_nodes - new_nodes:
            self.vertex_subgraphs[v].remove(idx)


    def get_common_subgraphs(self, u, v):
        common_indices = self.vertex_subgraphs[u] & self.vertex_subgraphs[v]
        return [self.subgraphs[idx] for idx in common_indices]


    def random(self, N=float('-inf')):
        size = len(self.subgraphs)
        idx = np.random.randint(size if size > N else N)

        if idx < size:
            return self.subgraphs[idx]
        else:
            return None
