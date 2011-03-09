# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class IngredientItem(Item):
    # define the fields for your item here like:
    parent = Field()
    name = Field()
    def __repr__(self):
        return '<IngredientItem: name:\'%s\' parent:\'%s\'>' % (self['name'], self['parent'])
