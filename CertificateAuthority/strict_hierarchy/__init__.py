# Initializes the blueprint for the strict CA system
from flask import Blueprint

strict_hierarchy_bp = Blueprint('strict_hierarchy', __name__, template_folder='templates')
