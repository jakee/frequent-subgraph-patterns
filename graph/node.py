from collections import namedtuple

Node = namedtuple('Node', ['node_id', 'label'])

class Neighbor(namedtuple('Neighbor', Node._fields + ('e_label',))):
    __slots__ = ()

    def to_node(self):
        return Node(self.node_id, self.label)