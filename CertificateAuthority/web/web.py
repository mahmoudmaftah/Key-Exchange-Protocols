import networkx as nx

class WebTrustHierarchy:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes = {'root': [], 'ca': [], 'user': []}

    def add_node(self, name, node_type):
        if name in self.graph:
            return False
        
        self.graph.add_node(name, type=node_type)
        self.nodes[node_type].append(name)
        return True

    def add_edge(self, source, target):
        if source not in self.graph or target not in self.graph:
            return False
        
        self.graph.add_edge(source, target)
        return True

    def get_ancestors(self, node):
        ancestors = set()
        for n in self.graph.nodes():
            if nx.has_path(self.graph, n, node):
                node_type = nx.get_node_attributes(self.graph, 'type')[n]
                if node_type == 'root':
                    ancestors.add(n)
        return ancestors

    def check_trust(self, source, target):
        if source == target:
            return {"trusted": True, "path": [source], "chain_length": 0}
        
        source_ancestors = self.get_ancestors(source)
        target_ancestors = self.get_ancestors(target)
        
        # Trust if they share at least one root, even if different
        if source_ancestors and target_ancestors:
            return {
                "trusted": True,
                "reason": "Both nodes can be traced back to trusted roots"
            }
        
        return {
            "trusted": False,
            "reason": "No trusted root CA ancestor found for both users"
        }
