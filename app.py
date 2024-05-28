from flask import Flask
from scripts.login.login import login_blueprint
from scripts.annotation.annotation import annotation_blueprint
from scripts.extensions import cache

app = Flask(__name__, 
            static_url_path='/scripts/static', 
            static_folder='scripts/static',
            template_folder='scripts/templates')
cache.init_app(app)

app.secret_key = 'your_secret_key'

# Register blueprints
app.register_blueprint(login_blueprint)
app.register_blueprint(annotation_blueprint)


if __name__ == "__main__":
    app.run(debug=False)
