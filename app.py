import os

from flask import Flask
# from flask_admin import Admin
# from flask_admin.contrib.sqla import ModelView

from src import db, main, parsing
from src.models import Flights, Companies


class Config:
    TESTING = False
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:pass@db/flightactivity_db"
    SQLALCHEMY_SESSION_OPTIONS = {"expire_on_commit": False}


def create_app(config_class=Config):
    # create and configure the app
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder="src/templates",
        static_folder="src/static",
    )
    app.config.from_object(config_class)
    app.config["SECRET_KEY"] = "your_secret_key_here"
    db.init_app(app)

    app.config["IPYTHON_CONFIG"] = {
        "InteractiveShell": {
            "colors": "Linux",
            "confirm_exit": False,
        },
    }

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.register_blueprint(main.bp_main)
    app.register_blueprint(parsing.bp_parsing)
    # admin = Admin(app, name='delete on prod', template_mode='bootstrap3')
    # admin.add_view(ModelView(Flights, db.session))
    # admin.add_view(ModelView(Companies, db.session))

    @app.route("/hello")
    def hello():
        return "Hello, World!"

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
