#!/bin/sh
set -eu

echo "Seeding database..."
python -m app.db.seed
