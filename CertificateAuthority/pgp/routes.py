from flask import Blueprint, render_template, request, jsonify
from .pgp import PGPTrustWeb
from . import pgp_bp  # Import pgp_bp from the same package/module

pgp_trust_system = PGPTrustWeb()

@pgp_bp.route('/')
def index():
    return render_template('pgp_index.html')

@pgp_bp.route('/api/add_node', methods=['POST'])
def add_node():
    data = request.json
    success = pgp_trust_system.add_node(data['name'])
    return jsonify({"success": success})

@pgp_bp.route('/api/add_signature', methods=['POST'])
def add_signature():
    data = request.json
    result = pgp_trust_system.add_signature(
        data['signer'],
        data['target'],
        data['trust_level']
    )
    return jsonify(result)

@pgp_bp.route('/api/check_trust', methods=['POST'])
def check_trust():
    data = request.json
    result = pgp_trust_system.check_trust(
        data['viewer'],
        data['target']
    )
    return jsonify(result)