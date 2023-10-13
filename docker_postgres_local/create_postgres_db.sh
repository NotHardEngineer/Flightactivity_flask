docker build -t my-postgres-flask .
docker run -d --name my-postgres-flask -p 5434:5434 my-postgres-flask
