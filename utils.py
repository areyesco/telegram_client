from datetime import datetime
from enum import Enum

class MessageType(Enum):
    HTML = "html"
    MD = "markdown"
    TXT = "default"

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