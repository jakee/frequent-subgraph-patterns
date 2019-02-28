import numpy as np

from collections import defaultdict

class SubgraphReservoir:
    subgraphs = None
    vertex_subgraphs = None

    def __init__(self, size):
        """
        Initialize a new subgraph reservoir.

        :param size: The maximum size of the reservoir.
        :type size: int
        """
        self.max_size = size
        self.subgraphs = []
        self.subgraph_indices = {}
        self.vertex_subgraphs = defaultdict(set)


    def __contains__(self, subgraph):
        return subgraph in self.subgraph_indices


    def __len__(self):
        return len(self.subgraphs)


    def is_full(self):
        """Checks if the reservoir has reached max_size."""
        return len(self) >= self.max_size


    def add(self, subgraph, N=float('-inf')):
        """Tries to add a subgraph to the resevoir."""

        success = False
        old_subgraph = None

        if subgraph not in self:

            if self.is_full():
                # the reservoir is full, so we replace an existing subgraph
                old_subgraph = self.random(N=N)

                if old_subgraph:
                    self.replace(old_subgraph, subgraph)
                    success = True

            else:
                # the reservoir is not full, so we add the new subgraph
                idx = len(self)
                self.subgraphs.append(subgraph)

                self.subgraph_indices[subgraph] = idx

                for u in subgraph.nodes:
                    self.vertex_subgraphs[u].add(idx)

                success = True

        return success, old_subgraph


    def replace(self, old_subgraph, new_subgraph):
        """Replaces old_subgraph with new_subgraph in the reservoir."""

        # keep track of the index where this operation is happening
        idx = self.subgraph_indices[old_subgraph]

        # replace the old subgraph with new_subgraph in the data structures
        del self.subgraph_indices[old_subgraph]
        self.subgraphs[idx] = new_subgraph
        self.subgraph_indices[new_subgraph] = idx

        # change the subgraphs by vertex mapping
        # only change mapping for vertices if necessary
        old_nodes = set(old_subgraph.nodes)
        new_nodes = set(new_subgraph.nodes)

        for u in new_nodes - old_nodes:
            self.vertex_subgraphs[u].add(idx)

        for v in old_nodes - new_nodes:
            self.vertex_subgraphs[v].remove(idx)


    def get_common_subgraphs(self, u, v):
        """Get all subgraphs from the reservoir that contain the edge (u, v)."""
        common_indices = self.vertex_subgraphs[u] & self.vertex_subgraphs[v]
        return [self.subgraphs[idx] for idx in common_indices]


    def random(self, N=float('-inf')):
        """
        Get a subgraph (or None) from the reservoir uniformly at random.

        Returns a subgraph from the reservoir uniformly at random. If value of
        parameter N exceeds the size of the reservoir M, we return a subgraph
        with probability M/N and otherwise return None. If N < M, the method
        always returns a random subgraph from the reservoir. 

        :param N: population size N used to pick a subgraph at propability M/N
        :type N: int, float
        """

        size = len(self)
        idx = np.random.randint(size if size > N else N)

        if idx < size:
            return self.subgraphs[idx]
        else:
            return None
