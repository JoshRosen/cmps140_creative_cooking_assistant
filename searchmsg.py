from data_structures import ParsedInputMessage
import random

class SearchMessage(ParsedInputMessage):

    def __init__(self, raw_input_string):
        """
        Create a new SearchMessage
        """
        self.frame = {"ingredients":None,
                      "cost":None,
                      "calories":None,
                      "time_total":None,
                      "time_prep":None,
                      "time_cook":None,
                      "culture":None,
                      "actions":None,
                      "instruments":None,
                      "food_type":None,
                      "author":None,
                      "meal_time":None,
                      "course":None,
                      "taste":None,
                      "food_group":None}
        self.keywords = ["search", "find", "bring", "want", "need"]
    
    def parse(self):
        """
        Fills out message meta and frame attributes
        """
        choice = random.randrange(0, 3)
        print choice
        if choice is 0:
            self.frame["ingredient"] = ["butter", "bread", "jelly"]
            self.frame["cost"] = 45.02
            self.frame["calories"] = 200
            self.frame["time_total"] = 600
            self.frame["time_prep"] = 120
            self.frame["time_cook"] = 480
            self.frame["culture"] = "Mexican"
            self.frame["actions"] = ["slice", "spread"]
            self.frame["instruments"] = ["knife", "fork", "spoon"]
            self.frame["food_type"] = "snack"
            self.frame["author"] = ["Sunset Magazine"]
            self.frame["food_group"] = ["grains", "sweets"]
        elif choice is 1:
            self.frame["ingredient"] = ["soda", "chips", "margarine"]
            self.frame["cost"] = 10.11
            self.frame["calories"] = 1000
            self.frame["time_total"] = 600
            self.frame["time_prep"] = 240
            self.frame["time_cook"] = 360
            self.frame["culture"] = "Russian"
            self.frame["food_type"] = "snack"
            self.frame["author"] = ["Sunset Magazine"]
            self.frame["food_group"] = ["dairy", "sweets"]
        else:
            self.frame["ingredient"] = ["pasta", "sauce"]
            self.frame["cost"] = 20.75
            self.frame["calories"] = 500
            self.frame["time_total"] = 1200
            self.frame["time_prep"] = 120
            self.frame["time_cook"] = 1080
            self.frame["culture"] = "Italian"
            self.frame["food_type"] = "dinner"
            self.frame["author"] = ["Culinary Periodical"]
            self.frame["food_group"] = ["grains"]

    def confidence(self):
        for keyword in self.keywords:
            if keyword in raw_input_string:
                return 1.0
        return 0.0

