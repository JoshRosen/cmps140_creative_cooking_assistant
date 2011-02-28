test:
	py.test --doctest-modules

refresh:
	### Download DB ###
	sh update_database.sh
	
	### Regenerate wordlists ###
	python2.6 generate_cuisines.py
	python2.6 generate_ingredients.py

	python generate_cuisines.py
	python generate_ingredients.py
	
	### Done. ###
