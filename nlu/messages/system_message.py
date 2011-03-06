from nlu.messages.parsed_input_message import ParsedInputMessage

class SystemMessage(ParsedInputMessage):
    frame_keys = ['action']
    exit_keywords = ['adieu.n.01', 'bye.n.01', 'farewell.n.02', 'exit.v.01']
                
    def _parse(self, raw_input_string):
        """
        Fills out message meta and frame attributes
        """
        
        if 'exit' == raw_input_string:
            frame['action'] = 'exit'
         
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

