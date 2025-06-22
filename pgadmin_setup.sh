#!/bin/bash
# Setup script for pgAdmin to connect to database

# Set environment variables for pgAdmin
export PGADMIN_SETUP_EMAIL="admin@imdb.com"
export PGADMIN_SETUP_PASSWORD="adminpass"

# Create pgpass file if it doesn't exist
mkdir -p /var/lib/pgadmin/storage/admin_imdb.com
echo "db:5432:imdb:imdbuser:imdbpass" > /var/lib/pgadmin/storage/admin_imdb.com/pgpass
chmod 600 /var/lib/pgadmin/storage/admin_imdb.com/pgpass

# Load servers configuration
python3 /pgadmin4/setup.py load-servers /pgadmin4/servers.json --user admin@imdb.com
