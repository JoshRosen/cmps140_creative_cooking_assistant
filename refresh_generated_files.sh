#bin/sh

# Download DB
echo "* Downloading DB."
sh update_database.sh

# Regenerate wordlists
echo "* Generating wordlists."
python generate_cuisines.py
python generate_ingredients.py

echo "* Done."
