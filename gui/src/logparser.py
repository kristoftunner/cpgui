import time

class LogParser():
    """
        class implementing the parsing of the input catchpenny logs for real-time debugging
    """
    logMessages = {}
    def __init__(self):
        self.messages = []
        self.message_types = []
        self.modules = []
        self.functions = []

    def update(self, input_message):
        """Read the input message and parse it into the message list.

        Args:
            input_message (string): input message recieved from the logging device
        """
        #parse input message
        input_message_split = input_message.split(" ")
        type = input_message_split[0][1:-1]
        function = input_message_split[1]
        module = input_message_split[2]
        timestamp = input_message_split[3]
        message = input_message[input_message.find(":")+4:]

        #update the parsed message arguments
        self.messages.append([type,function,module,timestamp,message])

        if function not in self.functions:
            self.functions.append(function)
        if module not in self.modules:
            self.modules.append(module)

    def get_message_by_type(self, type):
        """sorts the message list by message type and return the selected ones.    

        Args:
            type (string): message type - INF,WARN,ERR,DBG

        Returns:
            list: array of the parsed messages which are the type selected in the input
        """
        selected_messages = []
        for msg in self.messages:
            if msg[0] == type:
                selected_messages.append(msg)
        return selected_messages

    def get_message_by_function(self, function):
        """sorts the message list by the message "function" and return the selected ones

        Args:
            function (string): function name from which we want to get the logs

        Returns:
            list: array of the parsed messages which are from the selected function
        """
        selected_messages = []
        for msg in self.messages:
            if msg[1] == function:
                selected_messages.append(msg)
        return selected_messages
    
    def get_message_by_module(self, module):
        """sorts the message list by module and return the selected ones.

        Args:
            module (string): module name from which we want to get the logs of

        Returns:
            list: array of the parsed messages
        """
        selected_messages = []
        for msg in self.messages:
            if msg[2] == module:
                selected_messages.append(msg)
        return selected_messages
    
    def get_message_by_time(self, begin_timestamp, end_timestamp):
        """sorts the message list by timestamp and returns the selected ones.

        Args:
            begin_timestamp (time.struct_time): lower bound of the time interval represented in the time module struct_time
            end_timestamp (time.struct_time): upper bound of the time interval represented in time.struct_time

        Returns:
            list: array of the parsed messages
        """
        selected_messages = []
        for msg in self.messages:
            #first extracting the time variables
            year    = int(msg[3].split("_")[0].split("-")[0])
            month   = int(msg[3].split("_")[0].split("-")[1])
            day     = int(msg[3].split("_")[0].split("-")[2])
            hour    = int(msg[3].split("_")[1].split(":")[0])
            minute  = int(msg[3].split("_")[1].split(":")[1])
            
            if year > begin_timestamp.tm_year and year < end_timestamp.tm_year:
                selected_messages.append(msg)
            elif year == begin_timestamp.tm_year:
                if month > begin_timestamp.tm_mon:
                    selected_messages.append(msg)
                elif month == begin_timestamp.tm_mon:
                    if day > begin_timestamp.tm_day:
                        selected_messages.append(msg)
                    elif day == begin_timestamp.tm_day:
                        if hour > begin_timestamp.tm_hour:
                            selected_messages.append(msg)
                        elif hour == begin_timestamp.tm_hour:
                            if minute >= begin_timestamp.tm_min:
                                selected_messages.append(msg)
            elif year == end_timestamp.tm_year:
                if month < end_timestamp.tm_mon:
                    selected_messages.append(msg)
                elif month == end_timestamp.tm_mon:
                    if day < end_timestamp.tm_day:
                        selected_messages.append(msg)
                    elif day == end_timestamp.tm_day:
                        if hour < end_timestamp.tm_hour:
                            selected_messages.append(msg)
                        elif hour == end_timestamp.tm_hour:
                            if minute <= end_timestamp.tm_min:
                                selected_messages.append(msg)
        return selected_messages

if __name__ == '__main__':
    log_message1 = "[INF] main teslactrl 2021-05-02_05:23 Logging started"
    log_message2 = "[WRN] main gsm 2021-05-06_07:23 Logging started"
    log_message3 = "[ERR] gsm_controlProcess gsm 2022-06-04_05:23 Logging started"
    log_message4 = "[INF] main gsm 2023-10-04_09:13 Logging started"
    log_message5 = "[ERR] main teslactrl 2021-05-04_05:23 Logging started"
    lp = LogParser()
    lp.update(log_message1)
    lp.update(log_message2)
    lp.update(log_message3)
    lp.update(log_message4)
    lp.update(log_message5)
    
    messages = lp.get_message_by_type("INF")
    print("INF messages:")
    for msg in messages:
        print(msg)

    begin_timestamp = time.gmtime(1619820000)
    end_timestamp = time.gmtime(1622498400)
    messages_by_time = lp.get_message_by_time(begin_timestamp,end_timestamp)
    print("Messages by time:")
    for msg in messages_by_time:
        print(msg)
    print(begin_timestamp)
    print(end_timestamp)

    print("Messages for the teslactrl module:")
    messages_by_module = lp.get_message_by_module("teslactrl")
    for msg in messages_by_module:
        print(msg)

    print("Messages from the \"main\" function")
    messages_by_function = lp.get_message_by_function("main")
    for msg in messages_by_function:
        print(msg)

    