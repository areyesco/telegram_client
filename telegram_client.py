import sys
import asyncio
from telethon import TelegramClient, events
import utils
import config
from get_giftcard import process_message

# Set the event loop policy for Windows if necessary
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

client = TelegramClient(config.TELEGRAM_USER, config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)

chat_ids_to_read = config.TELEGRAM_CHATIDS_TO_READ

@client.on(events.NewMessage)
async def handler(event):
    chat_id = event.chat.id

    if chat_id in chat_ids_to_read:
        await utils.log_message(utils.Log_Level.INFO, "----------------------------------------------------")
        await utils.log_message(utils.Log_Level.INFO, f"telegram_client: chat_id: {chat_id}")
        await utils.log_message(f"debug: telegram_client: event: {event}")
        msg = utils.normilize_message(event)
        await utils.log_message(utils.Log_Level.INFO, f"telegram_client: event.message.message: {msg}")
        await process_message(str(msg))  # Await the asynchronous function
        await send_message_data_signal_to_me(msg, utils.MessageType.TXT)

async def send_message_data_signal_to_me(msg_signal, message_type=None):
    """
    Sends a message to yourself on Telegram.

    Parameters:
    msg_signal (str): The message content to send.
    message_type: The type of message formatting.
    """
    if message_type == utils.MessageType.HTML:
        await client.send_message('me', msg_signal, parse_mode=message_type.value)
    elif message_type == utils.MessageType.TXT:
        await client.send_message('me', msg_signal)
    else:
        await client.send_message('me', msg_signal)

client.start()
client.run_until_disconnected()
