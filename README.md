# Flightactivity_flask

- services.yml have shared volume with local code storage and intended for development process, container need to be restarted when template changes bc how gunicorn works or idk.
- services_prod.yml is intended for creation images for production server.
<p> Both of them require db initialization, in web/app_prod terminal write this: </p>

```
flask db init
flask db migrate
flask db upgrade
```
