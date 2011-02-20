rm 'ingredients.txt'
python scrapy-ctl.py runspider 'scraper/spiders/edible_seeds.py' &> 'log/edible_seeds.log'
mv 'ingredients.txt' '../wordtree/'
