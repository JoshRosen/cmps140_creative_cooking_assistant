test:
	rm -f combined_taggers.pkl
	py.test --doctest-modules

refresh:
	### Download DB ###
	sh update_database.sh
	
	### Regenerate wordlists ###
	python2.6 generate_cuisines.py
	python2.6 generate_ingredients.py

	### Remove cached tagger ###
	rm -f combined_taggers.pkl
	
	### Done. ###
