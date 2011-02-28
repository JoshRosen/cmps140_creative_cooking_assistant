test:
	py.test --doctest-modules
refresh:
	### Download DB ###
	sh update_database.sh
	
	### Regenerate wordlists ###

	python generate_cuisines.py
	python generate_ingredients.py
	
	### Done. ###
