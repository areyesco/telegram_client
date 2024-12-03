from datetime import datetime
from enum import Enum
import config

class MessageType(Enum):
    HTML = "html"
    MD = "markdown"
    TXT = "default"

class Log_Level(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"

async def log_message(log_level=Log_Level.DEBUG, *args):
    """
    Logs a message to the console by concatenating all arguments into a single string.

    :param args: Multiple string arguments to be logged.
    """
    bprint = False
    if log_level == Log_Level.INFO:
        bprint = True
    if log_level == Log_Level.DEBUG and config.DEBUG:
        bprint = True
    
    if bprint:
        message = " ".join(map(str, args))
        print(message)


"""
Convert a timestamp to String
    timestamp = 1628344800000/1000
    print(timeStampToString(timestamp))
"""
def timeStampToString(timestamp, dtFormat="%Y/%m/%d, %H:%M:%S.%f"):
    return datetime.fromtimestamp(timestamp).strftime(dtFormat)

def timeStampBinanceToString(timestamp, dtFormat="%Y/%m/%d %H:%M:%S.%f"):
    return timeStampToString(timestamp/1000, dtFormat)

def timeStampBinanceToTimeString(timestamp, dtFormat="%d %H hrs"):
    return timeStampToString(timestamp/1000, dtFormat)

def normilize_message(event):
    msg1 = event.message.text
    msg2 = repr(msg1)                                                                             
    msg3 = msg2.replace("'","")
    return msg3