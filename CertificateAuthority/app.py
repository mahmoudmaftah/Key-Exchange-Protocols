from flask import Flask, redirect, url_for
from strict_hierarchy.routes import strict_hierarchy_bp
from web.routes import web_bp

app = Flask(__name__)

# Register Blueprints for both strict and web systems
app.register_blueprint(strict_hierarchy_bp, url_prefix='/strict')
app.register_blueprint(web_bp, url_prefix='/web')

@app.route('/')
def home():
    return redirect(url_for('strict_hierarchy.index'))
if __name__ == '__main__':
    app.run(debug=True)
