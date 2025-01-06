import networkx as nx

class TrustGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_trust(self, entity1, entity2):
        self.graph.add_edge(entity1, entity2)

    def is_trusted(self, entity1, entity2):
        return nx.has_path(self.graph, entity1, entity2)