from flask import render_template, request, jsonify
from . import strict_hierarchy_bp
from .hierarchy import TrustHierarchy

trust_system = TrustHierarchy()

@strict_hierarchy_bp.route('/')
def index():
    return render_template('index.html')

@strict_hierarchy_bp.route('/api/add_node', methods=['POST'])
def add_node():
    data = request.json
    success = trust_system.add_node(data['name'], data['node_type'])
    return jsonify({"success": success})

@strict_hierarchy_bp.route('/api/add_edge', methods=['POST'])
def add_edge():
    data = request.json
    success = trust_system.add_edge(data['source'], data['target'])
    return jsonify({"success": success})

@strict_hierarchy_bp.route('/api/check_trust', methods=['POST'])
def check_trust():
    data = request.json
    result = trust_system.check_trust(data['source'], data['target'])
    return jsonify(result)

@strict_hierarchy_bp.route('/api/restart', methods=['POST'])
def restart():
    global trust_system
    trust_system = TrustHierarchy()  # Create a new instance
    return jsonify({"success": True})