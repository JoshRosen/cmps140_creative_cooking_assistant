from scrapy.spider import BaseSpider

class CulinaryFruitsSpider(BaseSpider):
    name = 'culinary_fruits'
    domain_name = 'wikipedia.org'
    start_urls = ['http://en.wikipedia.org/wiki/List_of_culinary_fruits',
                  'http://en.wikipedia.org/wiki/List_of_edible_seeds',
                  'http://en.wikipedia.org/wiki/List_of_pasta',
                  'http://en.wikipedia.org/wiki/List_of_breads',
                  'http://en.wikipedia.org/wiki/List_of_breads',
                  'http://en.wikipedia.org/wiki/List_of_breads',
                  'http://en.wikipedia.org/wiki/List_of_meat_animals',
                ]
                
    def parse(self, response):
        print "test1"
        
SPIDER=CulinaryFruitsSpider()
