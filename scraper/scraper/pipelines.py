# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from scrapy.exceptions import DropItem
from scraper import items
import re
        
class DropPipeline(object):
    """
    Drops invalid items.
    """
    def process_item(self, item, spider):
        print "PARENT: ", item['parent']
        print "NAME: ", item['name']
        if item['parent'] == None or item['name'] == None or item['parent'] == '' or item['name'] == '':
            raise DropItem("Item has no parent or name.")
        else:
            return item
            
class SanitizePipeline(object):
    """
    Cleans up the text in the item fields.
    """
    def clean(self, string):
        re.escape(string.lower())
    
    def process_item(self, item, spider):
        print "CLEAN: ", item
            
        if item['parent']:
            item['parent'] = self.clean(item['parent'])
            item['name'] = self.clean(item['name'])
            return item
        else:
            raise DropItem("Item has no parent or name.")
            return
        
class ExportPipeline(object):
    """
    Writes items out to file.
    """
    def __init__(self):
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        
    def spider_opened(self, spider):
        self.files={items.IngredientItem: open('ingredients.txt','wa')}
        
    def process_item(self, item, spider):
        line = "(%s,%s)\n" % (item['parent'], item['name'])
        self.files[type(item)].writelines([line])
        return item
            
    def spider_closed(self, spider):
        for afile in self.files.values():
            afile.close()
