from flask import Flask, render_template, request, jsonify
import networkx as nx

app = Flask(__name__)

class TrustHierarchy:
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
        source_type = next(typ for typ, nodes in self.nodes.items() if source in nodes)
        target_type = next(typ for typ, nodes in self.nodes.items() if target in nodes)
        
        if source_type == 'user' or target_type == 'root':
            return False
            
        self.graph.add_edge(source, target)
        return True

    def get_ancestors(self, node):
        ancestors = set()
        for n in self.graph.nodes():
            if nx.has_path(self.graph, n, node):
                node_type = next(typ for typ, nodes in self.nodes.items() if n in nodes)
                if node_type in ['root', 'ca']:
                    ancestors.add(n)
        return ancestors

    def find_all_trust_paths(self, source, target, ancestor):
        paths = []
        try:
            path_to_source = nx.shortest_path(self.graph, ancestor, source)
            path_to_target = nx.shortest_path(self.graph, ancestor, target)
            paths.append(path_to_source[::-1] + path_to_target[1:])
        except nx.NetworkXNoPath:
            pass
        return paths

    def check_trust(self, source, target):
        if source == target:
            return {"trusted": True, "path": [source], "chain_length": 0}
            
        source_ancestors = self.get_ancestors(source)
        target_ancestors = self.get_ancestors(target)
        common_ancestors = source_ancestors.intersection(target_ancestors)
        
        if common_ancestors:
            all_paths = []
            min_length = float('inf')
            
            for ancestor in common_ancestors:
                paths = self.find_all_trust_paths(source, target, ancestor)
                for path in paths:
                    if len(path) <= min_length:
                        if len(path) < min_length:
                            all_paths = []
                            min_length = len(path)
                        all_paths.append(path)
                    
            if all_paths:
                return {
                    "trusted": True,
                    "paths": all_paths,
                    "chain_length": min_length - 1
                }
        
        return {
            "trusted": False,
            "reason": "No common trusted ancestor found"
        }

trust_system = TrustHierarchy()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/add_node', methods=['POST'])
def add_node():
    data = request.json
    success = trust_system.add_node(data['name'], data['node_type'])
    return jsonify({"success": success})

@app.route('/api/add_edge', methods=['POST'])
def add_edge():
    data = request.json
    success = trust_system.add_edge(data['source'], data['target'])
    return jsonify({"success": success})

@app.route('/api/check_trust', methods=['POST'])
def check_trust():
    data = request.json
    result = trust_system.check_trust(data['source'], data['target'])
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)