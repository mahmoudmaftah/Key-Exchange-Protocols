from flask import Flask, render_template, request, jsonify, send_from_directory
import networkx as nx
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional
import os

class TrustModel(Enum):
    STRICT_HIERARCHY = "strict"
    NETWORKED = "networked" 
    WEB_BROWSER = "browser"
    PGP = "pgp"

class NodeType(Enum):
    ROOT_CA = "Root CA"
    SUPER_ROOT_CA = "Super Root CA" 
    INTERMEDIATE_CA = "Intermediate CA"
    END_ENTITY = "End Entity"
    PGP_USER = "PGP User"

class TrustLevel(Enum):
    COMPLETE = "Complete"
    IMPLICIT = "Implicit"
    PARTIAL = "Partial"
    MARGINAL = "Marginal"
    INVALID = "Invalid"

@dataclass
class Node:
    name: str
    node_type: NodeType
    trust_level: Optional[TrustLevel] = None

class CATrustSystem:
    def __init__(self, model_type: TrustModel):
        self.model_type = model_type
        self.graph = nx.DiGraph()
        self.nodes: Dict[str, Node] = {}

    def add_node(self, name: str, node_type: str, trust_level: Optional[str] = None) -> bool:
        if name in self.nodes:
            return False
        
        try:
            node_type_enum = NodeType(node_type)
            trust_level_enum = TrustLevel(trust_level) if trust_level else None
            node = Node(name=name, node_type=node_type_enum, trust_level=trust_level_enum)
            self.nodes[name] = node
            self.graph.add_node(name)
            return True
        except ValueError:
            return False

    def add_edge(self, source: str, target: str) -> bool:
        if source not in self.nodes or target not in self.nodes:
            return False

        # Validate edge based on model type
        if self.model_type == TrustModel.STRICT_HIERARCHY:
            if not self._validate_hierarchy_edge(source, target):
                return False
        elif self.model_type == TrustModel.NETWORKED:
            if not self._validate_networked_edge(source, target):
                return False
        elif self.model_type == TrustModel.WEB_BROWSER:
            if not self._validate_browser_edge(source, target):
                return False
        elif self.model_type == TrustModel.PGP:
            if not self._validate_pgp_edge(source, target):
                return False

        self.graph.add_edge(source, target)
        return True

    def _validate_hierarchy_edge(self, source: str, target: str) -> bool:
        source_node = self.nodes[source]
        target_node = self.nodes[target]
        
        # Root CA can sign intermediate CAs
        if source_node.node_type == NodeType.ROOT_CA:
            return target_node.node_type in [NodeType.INTERMEDIATE_CA, NodeType.END_ENTITY]
        
        # Intermediate CA can sign other intermediates or end entities
        if source_node.node_type == NodeType.INTERMEDIATE_CA:
            return target_node.node_type in [NodeType.INTERMEDIATE_CA, NodeType.END_ENTITY]
            
        return False

    def _validate_networked_edge(self, source: str, target: str) -> bool:
        source_node = self.nodes[source]
        target_node = self.nodes[target]

        # Super Root CA model
        if source_node.node_type == NodeType.SUPER_ROOT_CA:
            return target_node.node_type == NodeType.ROOT_CA
        if target_node.node_type == NodeType.SUPER_ROOT_CA:
            return source_node.node_type == NodeType.ROOT_CA
            
        # Mesh model - Root CAs can cross-sign
        return source_node.node_type == NodeType.ROOT_CA and target_node.node_type == NodeType.ROOT_CA

    def _validate_browser_edge(self, source: str, target: str) -> bool:
        source_node = self.nodes[source]
        target_node = self.nodes[target]
        
        # Root CAs can sign any certificate
        if source_node.node_type == NodeType.ROOT_CA:
            return True
            
        # Intermediate CAs can sign end entities
        if source_node.node_type == NodeType.INTERMEDIATE_CA:
            return target_node.node_type == NodeType.END_ENTITY
            
        return False

    def _validate_pgp_edge(self, source: str, target: str) -> bool:
        source_node = self.nodes[source]
        target_node = self.nodes[target]
        return source_node.node_type == NodeType.PGP_USER and target_node.node_type == NodeType.PGP_USER

    def check_trust(self, source: str, target: str) -> Dict:
        if source not in self.nodes or target not in self.nodes:
            return {"trusted": False, "reason": "Node not found"}

        if self.model_type == TrustModel.PGP:
            return self._check_pgp_trust(source, target)
        
        try:
            path = nx.shortest_path(self.graph, source, target)
            return {
                "trusted": True,
                "path": path,
                "chain_length": len(path) - 1
            }
        except nx.NetworkXNoPath:
            return {
                "trusted": False,
                "reason": "No trust path exists"
            }

    def _check_pgp_trust(self, source: str, target: str) -> Dict:
        source_node = self.nodes[source]
        target_node = self.nodes[target]
        
        if target_node.trust_level in [TrustLevel.COMPLETE, TrustLevel.IMPLICIT]:
            return {"trusted": True, "level": "Complete"}
            
        # Check for marginal trust (requires multiple partial trust signatures)
        partial_signers = [n for n in self.graph.predecessors(target)
                         if self.nodes[n].trust_level == TrustLevel.PARTIAL]
        
        if len(partial_signers) >= 2:
            return {"trusted": True, "level": "Marginal"}
            
        return {"trusted": False, "reason": "Insufficient trust signatures"}

app = Flask(__name__, template_folder='templates')
trust_systems: Dict[str, CATrustSystem] = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/templates/<path:path>')
def serve_template(path):
    return send_from_directory('templates', path)

@app.route('/api/create_model', methods=['POST'])
def create_model():
    try:
        data = request.json
        model_type = TrustModel(data['type'])
        trust_systems[model_type.value] = CATrustSystem(model_type)
        return jsonify({"success": True})
    except (KeyError, ValueError):
        return jsonify({"error": "Invalid model type"}), 400

@app.route('/api/add_node', methods=['POST'])
def add_node():
    data = request.json
    model_type = data.get('model_type')
    
    if not model_type or model_type not in trust_systems:
        return jsonify({"success": False, "error": "Invalid model type"}), 400

    success = trust_systems[model_type].add_node(
        name=data.get('name'),
        node_type=data.get('node_type'),
        trust_level=data.get('trust_level')
    )
    
    return jsonify({"success": success})

if __name__ == '__main__':
    app.run(debug=True, port=5000)