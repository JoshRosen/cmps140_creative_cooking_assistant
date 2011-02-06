from data_structures import ParsedInputMessage
import random

class SearchMessage(ParsedInputMessage):
    # attributes in the frame
    frame_keys = ['ingredientients', 'cost', 'callories', 'time_total', 'time_prep',
            'time_cook', 'culture', 'actions', 'instruments', 'food_type',
            'author', 'meal_time', 'course', 'taste', 'food_group']
    keywords = ["search", "find", "bring", "want", "need"]
    
    def parse(self, raw_input_string):
        """
        Fills out message meta and frame attributes
        """
        super(SearchMessage, self).parse(raw_input_string)
        
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

    def confidence(raw_input_string):
        for keyword in self.keywords:
            if keyword in raw_input_string:
                return 1.0
        return 0.0
