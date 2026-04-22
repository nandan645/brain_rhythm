from flask import Flask
from config import Config
from extensions import db
import os
from routes.api_routes import register_api_routes
from routes.combined_routes import register_combined_routes
from routes.analytics_routes import analytics_bp


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    instance_path=os.path.join(BASE_DIR, "instance"),
    instance_relative_config=True
)
app.config.from_object(Config)
app.register_blueprint(analytics_bp)

os.makedirs(app.instance_path, exist_ok=True)

db.init_app(app)

# Register all routes
register_api_routes(app)
register_combined_routes(app)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
