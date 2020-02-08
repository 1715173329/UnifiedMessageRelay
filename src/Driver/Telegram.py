import threading
import asyncio
from typing import Dict
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ContentType
from Core.UMRType import UnifiedMessage, MessageEntity, ChatAttribute
from Core import UMRDriver
from Core import UMRLogging
from Core import UMRConfig
from Core.UMRMessageRelation import set_ingress_message_id, set_egress_message_id
from Util.Helper import check_attribute
import datetime

launch_time = datetime.datetime.now()

NAME = 'Telegram'

# Initialize bot and dispatcher

logger = UMRLogging.getLogger('UMRDriver.Telegram')
logger.debug('Started initialization for Telegram')

attributes = [
    'BotToken'
]
config = UMRConfig.config['Driver']['Telegram']
check_attribute(config, attributes, logger)
bot: Bot
bot_user_id = int(config['BotToken'].split(':')[0])
loop: asyncio.AbstractEventLoop
image_file_id: Dict[str, str] = dict()  # mapping from filename to existing file id


@UMRDriver.api_register('Telegram', 'send')
async def send(to_chat: int, message: UnifiedMessage):
    """
    decorator for send new message
    :return:
    """
    logger.debug('calling real send')
    return asyncio.run_coroutine_threadsafe(_send(to_chat, message), loop)


async def _send(to_chat: int, message: UnifiedMessage):
    """
    decorator for send new message
    :return:
    """
    logger.debug('begin processing message')
    await bot.send_chat_action(to_chat, types.chat.ChatActions.TYPING)
    if message.chat_attrs.name:
        text = '<b>' + message.chat_attrs.name + '</b>: '
    else:
        text = ''

    for m in message.message:
        text += htmlify(m)

    if message.send_action.message_id:
        reply_to_message_id = message.send_action.message_id
    else:
        reply_to_message_id = None  # TODO support cross platform reply in the future

    if message.image:
        if message.image in image_file_id:
            logger.debug(f'file id for {message.image} found, sending file id')
            if message.image.endswith('gif'):
                tg_message = await bot.send_animation(to_chat, image_file_id[message.image], caption=text,
                                                      parse_mode=types.message.ParseMode.HTML,
                                                      reply_to_message_id=reply_to_message_id)
            else:
                tg_message = await bot.send_photo(to_chat, image_file_id[message.image], caption=text,
                                                  parse_mode=types.message.ParseMode.HTML,
                                                  reply_to_message_id=reply_to_message_id)
        else:
            logger.debug(f'file id for {message.image} not found, sending image file')
            if message.image.endswith('gif'):
                tg_message = await bot.send_animation(to_chat, types.input_file.InputFile(message.image), caption=text,
                                                      parse_mode=types.message.ParseMode.HTML,
                                                      reply_to_message_id=reply_to_message_id)
                image_file_id[message.image] = tg_message.document.file_id
            else:
                tg_message = await bot.send_photo(to_chat, types.input_file.InputFile(message.image), caption=text,
                                                  parse_mode=types.message.ParseMode.HTML,
                                                  reply_to_message_id=reply_to_message_id)
                image_file_id[message.image] = tg_message.photo[-1].file_id
    else:
        logger.debug('finished processing message, ready to send')
        tg_message = await bot.send_message(to_chat, text, parse_mode=types.message.ParseMode.HTML,
                                            reply_to_message_id=reply_to_message_id)

    if message.chat_attrs:
        set_egress_message_id(src_platform=message.chat_attrs.platform,
                              src_chat_id=message.chat_attrs.chat_id,
                              src_message_id=message.chat_attrs.message_id,
                              dst_platform='Telegram',
                              dst_chat_id=to_chat,
                              dst_message_id=tg_message.message_id,
                              user_id=bot_user_id)
    logger.debug('finished sending')
    return tg_message.message_id


def encode_html(encode_string: str) -> str:
    """
    used for telegram parse_mode=HTML
    :param encode_string: string to encode
    :return: encoded string, is encoded
    """
    return encode_string.replace('<', '&lt;').replace('>', '&gt;')


def htmlify(segment: MessageEntity):
    entity_type = segment.entity_type
    encoded_text = encode_html(segment.text)
    if entity_type == 'bold':
        return '<b>' + encoded_text + '</b>'
    elif entity_type == 'italic':
        return '<i>' + encoded_text + '</i>'
    elif entity_type == 'underline':
        return '<u>' + encoded_text + '</u>'
    elif entity_type == 'strikethrough':
        return '<s>' + encoded_text + '</s>'
    elif entity_type == 'monospace':
        if '\n' in encoded_text:
            return '<pre>' + encoded_text + '</pre>'
        else:
            return '<code>' + encoded_text + '</code>'
    elif entity_type == 'link':
        return '<a href=' + segment.link + '>' + encoded_text + '</a>'
    else:
        return encoded_text


def parse_entity(message: types.Message):
    message_list = list()
    if message.text:
        text = message.text
    elif message.caption:
        text = message.caption
    else:
        return message_list  # return an empty list
    if message.entities:
        entities = message.entities
    elif message.caption_entities:
        entities = message.caption_entities
    else:
        message_list.append(MessageEntity(text=text))
        return message_list

    offset = 0
    length = len(text)
    for index, entity in enumerate(entities):
        if entity.offset > offset:
            message_list.append(MessageEntity(text=text[offset: entity.offset]))
        start = entity.offset
        offset = entity.offset + entity.length
        # entity overlapping not supported
        if entity.type == 'text_link':
            message_list.append(MessageEntity(text=text[start:offset], entity_type='url', link=entity.url))
        else:
            entity_map = {
                'mention':       'bold',
                'hashtag':       '',
                'cashtag':       '',
                'bot_command':   '',
                'url':           'url',
                'email':         '',
                'phone_number':  '',
                'bold':          'bold',
                'italic':        'italic',
                'underline':     'underline',
                'strikethrough': 'strikethrough',
                'code':          'monospace',
                'pre':           'monospace',
                'text_mention':  ''
            }
            message_list.append(MessageEntity(text=text[start:offset], entity_type=entity_map[entity.type]))
    if offset < length:
        message_list.append(MessageEntity(text=text[offset: length]))
    return message_list


async def tg_get_image(file_id) -> (str, str):
    """

    :param file_id:
    :param changes: if the file id for the same file changes across time
    :param format:
    :return:
    """
    file = await bot.get_file(file_id)
    url = f'https://api.telegram.org/file/bot{config["BotToken"]}/{file.file_path}'
    perm_id = file_id[-52:]
    return url, perm_id


def get_chat_attributes(message: types.Message, chat_attrs: ChatAttribute):
    if message.forward_from_chat:  # forward from channel or user's private chat
        if message.forward_from_chat.title:
            name = message.forward_from_chat.title
            chat_id = message.forward_from_chat.id
            user_id = 0
            message_id = message.forward_from_message_id
        else:
            name = message.forward_from_chat.full_name
            chat_id = message.forward_from_chat.id
            user_id = message.forward_from_chat.id
            message_id = 0
        # private message does not have message_id, and channel message does not have user_id
        chat_attrs.forward_from = ChatAttribute(platform='Telegram',
                                                chat_id=chat_id,
                                                user_id=user_id,
                                                name=name,
                                                message_id=message_id)

    if message.forward_sender_name:
        chat_attrs.forward_from = ChatAttribute(platform='Telegram',
                                                name=message.forward_sender_name)

    if message.forward_from:  # forward from user (group message)
        name = message.forward_from.full_name
        user_id = message.forward_from.id
        # forward message does not have message_id and chat_id
        chat_attrs.forward_from = ChatAttribute(platform='Telegram',
                                                chat_id=0,
                                                user_id=user_id,
                                                name=name)

    if message.reply_to_message:
        chat_attrs.reply_to = ChatAttribute(platform='Telegram',
                                            chat_id=message.reply_to_message.chat.id,
                                            name=message.reply_to_message.from_user.full_name,
                                            user_id=message.reply_to_message.from_user.id,
                                            message_id=message.reply_to_message.message_id)
        get_chat_attributes(message.reply_to_message, chat_attrs.reply_to)


@UMRDriver.api_register('Telegram', 'is_group_admin')
async def is_group_admin(chat_id: int, user_id: int):
    member = await bot.get_chat_member(chat_id, user_id)
    if member:
        if member.status in ('creator', 'administrator'):
            return True
    return False


@UMRDriver.api_register('Telegram', 'is_group_owner')
async def is_group_owner(chat_id: int, user_id: int):
    member = await bot.get_chat_member(chat_id, user_id)
    if member:
        if member.status == 'creator':
            return True
    return False


def handle_exception(loop, context):
    # context["message"] will always be there; but context["exception"] may not
    msg = context.get("exception", context["message"])
    logger.exception('Unhandled exception: ', exc_info=msg)


def run():
    global bot, dp, loop
    loop = asyncio.new_event_loop()
    loop.set_exception_handler(handle_exception)
    asyncio.set_event_loop(loop)
    bot = Bot(token=config['BotToken'])
    dp = Dispatcher(bot)

    @dp.message_handler(content_types=ContentType.ANY)
    @dp.edited_message_handler(content_types=ContentType.ANY)
    async def handle_msg(message: types.Message):
        from_user = message.from_user

        unified_message = UnifiedMessage(platform='Telegram',
                                         chat_id=message.chat.id,
                                         name=from_user.full_name,
                                         user_id=from_user.id,
                                         message_id=message.message_id)

        get_chat_attributes(message, unified_message.chat_attrs)
        set_ingress_message_id(src_platform='Telegram', src_chat_id=message.chat.id,
                               src_message_id=message.message_id, user_id=message.from_user.id)

        if message.content_type == ContentType.TEXT:
            unified_message.message = parse_entity(message)
            await UMRDriver.receive(unified_message)
        elif message.content_type == ContentType.PHOTO:
            url, file_id = await tg_get_image(message.photo[-1].file_id)
            unified_message.image = url
            unified_message.file_id = file_id
            unified_message.message = parse_entity(message)
            await UMRDriver.receive(unified_message)
        elif message.content_type == ContentType.STICKER:
            url, file_id = await tg_get_image(message.sticker.file_id)
            unified_message.image = url
            unified_message.file_id = file_id
            await UMRDriver.receive(unified_message)
        elif message.content_type == ContentType.ANIMATION:
            url, file_id = await tg_get_image(message.animation.file_id)
            unified_message.image = url
            unified_message.file_id = file_id
            await UMRDriver.receive(unified_message)
        else:
            unified_message.message = [MessageEntity(text='[Unsupported message]')]
            await UMRDriver.receive(unified_message)

    executor.start_polling(dp, skip_updates=True, loop=loop)


t = threading.Thread(target=run)
t.daemon = True
UMRDriver.threads.append(t)
t.start()

logger.debug('Finished initialization for Telegram')
