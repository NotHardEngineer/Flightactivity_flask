import os

from flask import Flask

from src import db, main, parsing


class Config:
    TESTING = False
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:pass@localhost:5432/flightactivity_db"
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

    @app.route("/hello")
    def hello():
        return "Hello, World!"


    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
