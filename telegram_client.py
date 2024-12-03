from asyncio.windows_events import NULL
from telethon import TelegramClient, events
import re
import pprint
import utils
import config

client = TelegramClient(config.TELEGRAM_USER, config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)

chatIds_to_read = config.TELEGRAM_CHATIDS_TO_READ
@client.on(events.NewMessage)
async def handler(event):
    chat_id = None
    if event.is_channel:
        chat_id = event.chat.id
        print("is_channel:" + str(event.is_channel))
        print("event.chat.id:" + str(event.chat.id))
    else:
        print("chat_id:" + str(event.chat_id))
        chat_id = event.chat_id
    
    if chat_id in chatIds_to_read:
        print("chat_id:" + str(chat_id))
        print("str(event):" + str(event))
        msg1 = event.message.text
        msg2 = repr(msg1)                                                                             
        msg3 = msg2.replace("'","")
        print("event.message.message:" + msg3)
        namedGroups = evaluateMessage(msg3)
        if namedGroups != None:
            #print("msgType:" + namedGroups["msgType"])
            #print("namedGroups:", namedGroups)
            if namedGroups["msgType"] == "TPReached":
                await client.send_message('me', 'Reached')
            elif namedGroups["msgType"] == "Signal":
                (jsonSignalEvaluation, msgSignalToSend) = signalEvaluation.signalEvaluation(namedGroups, utils.MessageType.HTML)
                await sendMessageDataSignalToMe(msgSignalToSend, utils.MessageType.HTML)
                (buyOrderPlaced, buyOrder, sellOrders) = signalEvaluation.buyEvaluation(jsonSignalEvaluation)
                if buyOrderPlaced:
                    await sendMessageDataSignalToMe(pprint.pformat(buyOrder), utils.MessageType.TXT)
                atLeastSellOrderPlaced = False
                for sellOrder in sellOrders:
                    if sellOrder["sellOrderPlaced"]:
                        atLeastSellOrderPlaced = True
                        await sendMessageDataSignalToMe(pprint.pformat(sellOrder["sellOrder"]), utils.MessageType.TXT)
                    
                if buyOrderPlaced and not atLeastSellOrderPlaced:
                    await sendMessageDataSignalToMe("*********************************** ERR1: Se compro pero no se vendio *******************************************", utils.MessageType.TXT)

                #if sellOrderPlaced:
                #    await sendMessageDataSignalToMe(pprint.pformat(sellOrder), utils.MessageType.TXT)
            #print("message sent to yourself")

    #print(event)

async def sendMessageDataSignalToMe(msgSignal, messageType=None):
    """
    msgSignal = 'Signal: \n' + msg
    jsonDataSymbol = binanceProcessor.getDataAnalysisForSymbol(namedGroups["symbol"],"1h",6)
    msgSignal = msgSignal + "\n\nData:" + pprint.pformat(jsonDataSymbol)
    """
    if messageType == utils.MessageType.HTML:
        await client.send_message('me', msgSignal, parse_mode=messageType.value)
    elif messageType == utils.MessageType.TXT:
        await client.send_message('me', msgSignal)
    #await forwardMessage(509261802, msg)

async def forwardMessage(chatID, msg):
    await client.send_message(chatID, msg)

def evaluateMessage(msg):
    """The function will return a namedGroups = None, if the the message is not a 'Signal Bot' message """
    namedGroups = evaluateSignalMessage(msg)
    if namedGroups == None:
        namedGroups = evaluateTPReachedMessage(msg)
    return namedGroups

new_signal_pattern = r"^Symbol\:..(?P<symbol>\w*)\\nMarket\:..(?P<market>\w*)[\s|\S]*Buy in range\:\s*(?P<buyMin>[\d|.]*).-.(?P<buyMax>[\d|.]*)[\s|\S]*Short Term\:\s*(?P<shortTP>[\d|.]*)[\s|\S]*Mid.Term\:\s*(?P<midTP>[\d|.]*)[\s|\S]*Long.Term\:\s*(?P<longTP>[\d|.]*)[\s|\S]*Stop.Loss\:\s*(?P<sl>[\d|.]*)[\s|\S]*$"
def evaluateSignalMessage(msg):
    """The function will return a namedGroups = None, if the the message is not a 'Signal Bot' message """
    global new_signal_pattern
    m = re.match(new_signal_pattern, msg)
    namedGroups = None
    if m != None:
        namedGroups = m.groupdict()
        if namedGroups != None:
            namedGroups['msgType'] = "Signal"
    return namedGroups

new_tpreached_pattern = r"[\w\W]*(?P<reached>Reached)"
def evaluateTPReachedMessage(msg):
    global new_tpreached_pattern
    m = re.match(new_tpreached_pattern, msg, re.MULTILINE)
    namedGroups = None
    if m != None:
        namedGroups = m.groupdict()
        if namedGroups != None:
            namedGroups["msgType"] = "TPReached"
    return namedGroups

client.start()
client.run_until_disconnected()