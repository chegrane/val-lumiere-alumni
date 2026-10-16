#!/usr/bin/env bash
# Rebuild the database from zero: schema, views, test data.
#
# Usage:   scripts/reset_db.sh                    (rebuilds val_lumiere_alumni)
#          scripts/reset_db.sh other_database     (rebuilds another database)
#
# Everything in the database is deleted first. That is fine: there is no real data,
# only what the SQL files create.

set -euo pipefail   # stop at the first error; an unset variable is an error

DB="${1:-val_lumiere_alumni}"           # first argument, or the default name
cd "$(dirname "$0")/.."                 # run from the project root, wherever it is called from

dropdb --if-exists "$DB"                # delete the database, if it exists
createdb "$DB"                          # create it empty

for file in sql/01_schema.sql sql/02_views.sql sql/03_test_data.sql; do
    echo "== $file"
    psql --quiet --set ON_ERROR_STOP=1 --dbname "$DB" --file "$file"
done

echo "Database $DB rebuilt."
