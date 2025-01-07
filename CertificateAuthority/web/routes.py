from flask import render_template, request, jsonify
from . import web_bp
from .web import WebTrustHierarchy

web_trust_system = WebTrustHierarchy()

@web_bp.route('/')
def index():
    return render_template('web_index.html')

@web_bp.route('/api/add_node', methods=['POST'])
def add_node():
    data = request.json
    success = web_trust_system.add_node(data['name'], data['node_type'])
    return jsonify({"success": success})

@web_bp.route('/api/add_edge', methods=['POST'])
def add_edge():
    data = request.json
    success = web_trust_system.add_edge(data['source'], data['target'])
    return jsonify({"success": success})

@web_bp.route('/api/check_trust', methods=['POST'])
def check_trust():
    data = request.json
    result = web_trust_system.check_trust(data['source'], data['target'])
    return jsonify(result)

@web_bp.route('/api/restart', methods=['POST'])
def restart():
    global web_trust_system
    web_trust_system = WebTrustHierarchy()  # Create a new instance
    return jsonify({"success": True})