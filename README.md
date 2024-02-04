# oBugs Backend

Technologies
* Poetry dependencies
* Docker deployment
* Postgresql database
* SQLAlchemy ORM
* Alembic database migrations
* Strawberry GraphQL
* FastAPI Web Framework
* Uvicorn server

## Setup

- Create `./docker.env` file with as structure similar to `./docker.example.env`
- Create `./src/settings.ini` file with a structure similar to `./src/settings.example.ini`

## Dev

If you wish to use docker-postgresql in dev, set it to something similar to the production:

```
cd docker
docker compose -f docker-compose-dev.yaml --env-file docker.env up postgres
```

To run the code, use poetry:

```
# Make sure you have poetry
python -m pip install pipx
python -m pipx install poetry
# Install dependencies
poetry install --with docs --no-root
# Get information about the venv (to setup in your ide)
poetry env info
# Run
cd src
poetry run python main.py
# If you want to remove your venv associated
poetry env remove python
```

To generate a new database migration, use alembic:

```
poetry run alembic revision --autogenerate
```

To build the docs:

```
cd docs
poetry run sphinx-build . _build
```

## Prod

Use the `deploy.sh` script to get the latest version of code and refresh the docker containers:

```
cd docker
./deploy.sh
```
