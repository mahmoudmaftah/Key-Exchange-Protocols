from flask import Flask, render_template, request, jsonify
import networkx as nx
from enum import Enum
from typing import List, Set

class TrustLevel(Enum):
    IMPLICIT = "Implicit"
    COMPLETE = "Complete"
    PARTIAL = "Partial Trust"
    MARGINAL = "Marginally Valid"
    INVALID = "Invalid"

class TrustNetwork:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.trust_levels = {}

    def add_entity(self, name: str, trust_level: str):
        self.graph.add_node(name)
        self.trust_levels[name] = trust_level

    def add_trust(self, from_entity: str, to_entity: str):
        if from_entity != to_entity:
            self.graph.add_edge(from_entity, to_entity)

    def get_trust_predecessors(self, node: str, trust_level: str) -> Set[str]:
        return {pred for pred in self.graph.predecessors(node) 
               if self.trust_levels[pred] == trust_level}

    def validate_node_trust(self, node: str, visited: Set[str]) -> bool:
        if node in visited:
            return True
            
        level = self.trust_levels[node]
        visited.add(node)

        # Invalid entities break the trust chain
        if level == TrustLevel.INVALID.value:
            return False

        # Implicit trust is always valid
        if level == TrustLevel.IMPLICIT.value:
            return True

        # Get predecessors
        predecessors = list(self.graph.predecessors(node))
        if not predecessors:
            return level == TrustLevel.IMPLICIT.value

        # Complete trust needs at least one Implicit/Complete predecessor
        if level == TrustLevel.COMPLETE.value:
            valid_types = {TrustLevel.IMPLICIT.value, TrustLevel.COMPLETE.value}
            return any(self.trust_levels[pred] in valid_types and 
                      self.validate_node_trust(pred, visited.copy())
                      for pred in predecessors)

        # Marginal trust needs at least 2 valid Partial trust predecessors
        if level == TrustLevel.MARGINAL.value:
            partial_trusted = self.get_trust_predecessors(node, TrustLevel.PARTIAL.value)
            valid_partials = sum(1 for pred in partial_trusted 
                               if self.validate_node_trust(pred, visited.copy()))
            return valid_partials >= 2

        # Partial trust needs at least one valid Complete/Implicit predecessor
        if level == TrustLevel.PARTIAL.value:
            valid_types = {TrustLevel.IMPLICIT.value, TrustLevel.COMPLETE.value}
            return any(self.trust_levels[pred] in valid_types and 
                      self.validate_node_trust(pred, visited.copy())
                      for pred in predecessors)

        return False

    def find_all_paths(self, start: str, end: str, visited: Set[str], path: List[str]) -> List[List[str]]:
        if start in visited:
            return []
            
        path = path + [start]
        if start == end:
            return [path]
            
        paths = []
        visited = visited | {start}
        
        for neighbor in self.graph.neighbors(start):
            new_paths = self.find_all_paths(neighbor, end, visited, path)
            paths.extend(new_paths)
            
        return paths

    def check_trust(self, from_entity: str, to_entity: str) -> bool:
        # Handle self-trust
        if from_entity == to_entity:
            level = self.trust_levels[from_entity]
            return level in [TrustLevel.IMPLICIT.value, TrustLevel.COMPLETE.value]

        # Find all possible paths
        paths = self.find_all_paths(from_entity, to_entity, set(), [])
        if not paths:
            return False

        # Validate each path
        for path in paths:
            valid = True
            visited = set()
            
            # Validate each node in the path
            for node in path:
                if not self.validate_node_trust(node, visited.copy()):
                    valid = False
                    break
                    
            if valid:
                return True

        return False

app = Flask(__name__)
trust_network = TrustNetwork()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_entity', methods=['POST'])
def add_entity():
    data = request.get_json()
    trust_network.add_entity(data['name'], data['trust_level'])
    return jsonify({"success": True})

@app.route('/add_trust', methods=['POST'])
def add_trust():
    data = request.get_json()
    trust_network.add_trust(data['from'], data['to'])
    return jsonify({"success": True})

@app.route('/check_trust', methods=['POST'])
def check_trust():
    data = request.get_json()
    has_trust = trust_network.check_trust(data['from'], data['to'])
    return jsonify({"has_trust": has_trust})

@app.route('/get_graph', methods=['GET'])
def get_graph():
    return jsonify({
        "nodes": list(trust_network.graph.nodes()),
        "edges": list(trust_network.graph.edges()),
        "trust_levels": trust_network.trust_levels
    })

if __name__ == '__main__':
    app.run(debug=True)