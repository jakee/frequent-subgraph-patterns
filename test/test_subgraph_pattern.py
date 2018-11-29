import unittest

from subgraph.subgraph import Subgraph
from subgraph.pattern import canonical_label

class SubgraphPatternTestCase(unittest.TestCase):

    def test_isomorphic_wedges(self):
        wedge = Subgraph(
            nodes=[(1,1), (2,1), (3,2)],
            edges=[(1,2,1),(1,3,2)]
        )

        isomorphic_wedge = Subgraph(
            nodes=[(5,2), (8,1), (15,1)],
            edges=[(5,15,2),(8,15,1)]
        )

        cl1 = canonical_label(wedge)
        cl2 = canonical_label(isomorphic_wedge)

        self.assertEqual(cl1, cl2, "non-matching canonical labels of isomorphic wedges")

    def test_non_isomorphic_wedges(self):
        wedge = Subgraph(
            nodes=[(1,1), (2,1), (3,2)],
            edges=[(1,2,1), (1,3,2)]
        )

        non_isomorphic_wedge = Subgraph(
            nodes=[(5,2), (8,1), (15,1)],
            edges=[(5,8,1), (5,15,2)]
        )

        cl1 = canonical_label(wedge)
        cl2 = canonical_label(non_isomorphic_wedge)

        self.assertNotEqual(cl1, cl2, "matching canonical labels of non-isomorphic wedges")

    def test_isomorphic_triangles(self):
        triangle = Subgraph(
            nodes=[(1,1), (2,1), (3,2)],
            edges=[(1,2,1), (1,3,2), (2,3,1)]
        )

        isomorphic_triangle = Subgraph(
            nodes=[(5,2), (8,1), (15,1)],
            edges=[(5,8,1), (5,15,2), (8,15,1)]
        )

        cl1 = canonical_label(triangle)
        cl2 = canonical_label(isomorphic_triangle)

        self.assertEqual(cl1, cl2, "non-matching canonical labels of isomorphic triangles")

    def test_non_isomorphic_triangles(self):
        triangle = Subgraph(
            nodes=[(1,1), (2,1), (3,2)],
            edges=[(1,2,1), (1,3,2), (2,3,1)]
        )

        non_isomorphic_triangle = Subgraph(
            nodes=[(1,1), (2,2), (3,2)],
            edges=[(1,2,1), (1,3,2), (2,3,1)]
        )

        cl1 = canonical_label(triangle)
        cl2 = canonical_label(non_isomorphic_triangle)

        self.assertNotEqual(cl1, cl2, "matching canonical labels of non-isomorphic triangles")

