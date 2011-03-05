from data_structures import ParsedInputMessage

class SystemMessage(ParsedInputMessage):
    frame_keys = ['action']
    keywords = ['exit', '/debug']
                
    def _parse(self, raw_input_string):
        """
        Fills out message meta and frame attributes
        """
        
        if 'exit' == raw_input_string:
            frame['action'] = 'exit'
        elif '/debug' == raw_input_string:
            frame['action'] = 'debug'
         
    @staticmethod
    def confidence(raw_input_string):
        """
        Returns a confidence score if keyword is sentence
        """
        for keyword in self.keywords:
            if keyword == raw_input_string:
                return 1.0
        return 0.0
            
    def __repr__(self):
        return '<%s: frame:%s>' % (self.__class__.__name__, self.frame)

