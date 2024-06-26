oBugs Backend
==============

GraphQL backend using the following technologies:

* Python 3.11+
* `Poetry <https://python-poetry.org/>`_ to manage Python Virtual Environnement and dependencies.
* `Docker <https://www.docker.com/>`_ to manage deployment in production and database in development.
* `Postgresql <https://www.postgresql.org/>`_ as database choice.
* `SQLAlchemy <https://www.sqlalchemy.org/>`_ as ORM (Object Relational Mapper) library.
* `Alembic <https://alembic.sqlalchemy.org/en/latest/>`_ to manage database migrations.
* `Strawberry <https://strawberry.rocks/>`_ as GraphQL API Framework.
* `FastAPI <https://fastapi.tiangolo.com/>`_ as Asynchronous Web Framework.
* `Uvicorn <https://www.uvicorn.org/>`_ as Asynchronous Web Server.
* `Pytest <https://docs.pytest.org/en/8.0.x/>`_ as Test Framework.
* `Sphinx <https://www.sphinx-doc.org/en/master/>`_ to generate documentation from codebase.


Setup
-------

You first need to create 2 configuration files:

- Create `./docker/docker.env` file with as structure similar to `./docker/docker.example.env`
- Create `./src/settings.ini` file with a structure similar to `./src/settings.example.ini`

If you wish to use docker-postgresql in dev, start it using the .dev compose file::

    cd docker
    docker compose -f docker-compose.dev.yaml --env-file docker.env up 
    # Optional, make a backup of production database
    sudo rsync -av --no-perms --delete --chown=$(whoami) ../obugs_postgres_data/ ~/obugs_postgres_save
    sudo chown -R $(whoami):$(whoami) ../obugs_postgres_save
    # And download it to use for your development tests
    sudo rsync -avz --stats --delete $(whoami)@<server>:~/obugs_postgres_save/ ../obugs_postgres_data
    sudo rm -rf ~/obugs_postgres_save

To run the code, using poetry::

    # Make sure you have poetry
    python -m pip install pipx
    python -m pipx install poetry
    # Install dependencies
    poetry install --with docs,tests
    # Generate documentation
    cd docs
    poetry run sphinx-build . _build
    # Run tests
    cd src
    poetry run pytest
    # Get information about the virtual environment (to setup in your ide)
    poetry env info
    # Run
    cd src
    poetry run python main.py
    # If you want to remove your venv associated
    poetry env remove python

To generate a new database migration, use alembic::

    poetry run alembic revision --autogenerate

Production
------------

If everything is properly setup (configuration files), its only a git pull and restart::

    cd docker
    docker compose down
    git pull
    docker compose --env-file docker.env up --build -d
