# Flightactivity_flask

- docker_compose.yaml have shared volume with local code directory and intended for development process, container need to be restarted when template changes bc of how gunicorn works or idk.
- docker_compose_prod.yaml is intended for creation images for production server.
<p> Both of them require db initialization, in web/app_prod terminal execute this: </p>

```
flask db init
flask db migrate
flask db upgrade
```
