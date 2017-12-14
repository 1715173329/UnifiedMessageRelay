import global_vars
from telegram.ext.dispatcher import DispatcherHandlerStop
from utils import get_forward_index, get_plugin_priority
from telegram.ext import MessageHandler, Filters

from command import command_listener
from telegram import Update, User
import traceback
import logging

# Commands are only available in group and discuss
# For private chat, another plugin will take over

logger = logging.getLogger("CTBMain.text_forward")

def tg_command(bot, update: Update):
    if update.edited_message:  # handle edit
        message = update.edited_message
    else:
        message = update.message

    tg_group_id = message.chat_id  # telegram group id
    if message.text.startswith('!!'):
        for command in global_vars.command_list:  # process all non-forward commands
            if command.tg_only:
                if message.text[2:] == command.command or message.text[2:] == command.cmd:
                    command.handler(tg_group_id, message.from_user, message.message_id)
                    raise DispatcherHandlerStop()

    forward_index = get_forward_index(tg_group_id=tg_group_id)  # TODO: reconstruct get_forward_index, add new function to return list
    if forward_index == -1:
        raise DispatcherHandlerStop()

    if message.text.startswith('!!'):
        for command in global_vars.command_list:  # process all forward commands
            if not command.tg_only and not command.qq_only:
                if message.text[2:] == command.command or message.text[2:] == command.cmd:
                    command.handler(forward_index, tg_user=message.from_user, tg_group_id=tg_group_id, tg_message_id=message.message_id)
                    raise DispatcherHandlerStop()


global_vars.dp.add_handler(MessageHandler(Filters.text, tg_command), get_plugin_priority(__name__))


# decorator 'message_type', 'message_type', ..., group=number
@global_vars.qq_bot.on_message('group', 'discuss', group=get_plugin_priority(__name__))
def qq_command(context):
    if len(context['message']) > 1:  # rich text can not be commands
        return {'pass': True}

    if context['message'][0]['type'] != 'text':  # commands can only be pure text
        return {'pass': True}

    qq_group_id = context.get('group_id')
    qq_discuss_id = context.get('discuss_id')
    text = context['message'][0]['data']['text']  # get message text

    if text.startswith('!!'):
        logger.debug('command indicator met: ' + text)
        text = text[2:]
        for command in global_vars.command_list:  # process all non-forward commands
            if command.qq_only:
                if text == command.command or text == command.cmd:
                    logger.debug('command: ' + command.command + ' , qq_only')
                    return command.handler(qq_group_id, qq_discuss_id, int(context['user_id']))

    forward_index = get_forward_index(qq_group_id=qq_group_id, qq_discuss_id=qq_discuss_id)
    if forward_index == -1:
        return ''

    if text.startswith('!!'):
        text = text[2:]
        for command in global_vars.command_list:  # process all forward commands
            if not command.tg_only and not command.qq_only:
                if text == command.command or text == command.cmd:
                    logger.debug('command: ' + command.command)
                    return command.handler(forward_index, qq_group_id=qq_group_id, qq_discuss_id=qq_discuss_id, qq_user=int(context['user_id']))

    return {'pass': True}


@command_listener('show commands', 'sc', qq_only=True, description='print all commands')
def command_qq(qq_group_id: int, qq_discuss_id:int, qq_user: int):
    result = ''
    for command in global_vars.command_list:
        if not command.tg_only:
            result += command.command + '(' + command.cmd + '): '
            if command.description:
                result += command.description + '\n'
    return {'reply': result}


@command_listener('show commands', 'sc', tg_only=True, description='print all commands')
def command_tg(tg_group_id: int, tg_user: User, tg_message_id: int):
    result = ''
    for command in global_vars.command_list:
        if not command.qq_only:
            result += '<b>' + command.command + '</b>(<b>' + command.cmd + '</b>): '
            if command.description:
                result += command.description + '\n'
    global_vars.tg_bot.sendMessage(tg_group_id, result, reply_to_message_id=tg_message_id, parse_mode='HTML')


@command_listener('help', 'h', qq_only=True, description='print help')
def command_qq(qq_group_id: int, qq_discuss_id:int, qq_user: int):
    result = '''I'm a relay bot between qq and tg.
Please use "!!show commands" or "!!sc" to show all commands.
'''
    return {'reply': result}


@command_listener('help', 'h', tg_only=True, description='print help')
def command_tg(tg_group_id: int, tg_user: User, tg_message_id: int):
    result = '''I'm a relay bot between qq and tg.
    Please use "!!show commands" or "!!sc" to show all commands.
    '''
    global_vars.tg_bot.sendMessage(tg_group_id, result, reply_to_message_id=tg_message_id, parse_mode='HTML')
