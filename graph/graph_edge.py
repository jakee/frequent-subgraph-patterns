from collections import namedtuple

from .node import Node, Neighbor

class Edge(namedtuple('Edge', ['u', 'u_label', 'v', 'v_label', 'label'])):
    __slots__ = ()

    def __lt__(self, other):
        if self != other:
            u_self = self.get_u()
            u_other = other.get_u()

            if u_self < u_other:
                return True
            elif u_self == u_other:
                v_self = self.get_v()
                v_other = other.get_v()

                if v_self < v_other:
                    return True
                elif v_self == v_other:
                    return self.label < other.label

        return False

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        return not (self <= other)

    def __ge__(self, other):
        return not (self < other)

    def get_u(self):
        return Node(self.u, self.u_label)

    def get_u_nbr(self):
        return Neighbor(self.u, self.u_label, self.label)

    def get_v(self):
        return Node(self.v, self.v_label)

    def get_v_nbr(self):
        return Neighbor(self.v, self.v_label, self.label)
