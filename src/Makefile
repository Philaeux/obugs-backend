# Generate database migrations
win-gen-migrations:
	.\.env\Scripts\alembic.exe revision --autogenerate

# Import docker database to work locally
import-database-snapshot:
	sudo rsync -avz --stats --delete philaeux@luna.the-cluster.org:~/obugs_postgres_save/ ../../obugs_postgres_data

create-database-snapshot:
	sudo rsync -av --no-perms --delete --chown=$(whoami) ../../obugs_postgres_data/ ../../obugs_postgres_save
	sudo chown -R $(whoami):$(whoami) ../../obugs_postgres_save

