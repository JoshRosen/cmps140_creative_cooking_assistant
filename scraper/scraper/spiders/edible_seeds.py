from scrapy.spider import BaseSpider
from scraper import items
from scrapy.selector import HtmlXPathSelector


class EdibleSeedsSpider(BaseSpider):
    name = 'edible_seeds'
    domain_name = 'wikipedia.org'
    start_urls = ['http://en.wikipedia.org/wiki/List_of_edible_seeds']
                
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        item = items.IngredientItem()
        
        categoryItem = items.IngredientItem()
        categoryItem['parent'] = 'ingredient'
        categoryItem['name'] = 'seed'
        yield categoryItem
        
        categories = hxs.select('//h2/span[not(contains(text(),"See also") or contains(text(),"References"))]')
        for category in categories:
            categoryItem = items.IngredientItem()
            categoryItem['parent'] = 'seed'
            categoryItem['name'] = category.select('./text()').extract()[0]
            yield categoryItem
            
            tags = category.select('./../following-sibling::*')
            for tag in tags:
                if tag.select('self::h2'): break
                seeds = tag.select('.//ul//li/a/text()').extract()
                for seed in seeds:
                    seedItem = items.IngredientItem()
                    seedItem['parent'] = categoryItem['name']
                    seedItem['name'] = seed
                    yield seedItem
            
        
SPIDER=EdibleSeedsSpider()
