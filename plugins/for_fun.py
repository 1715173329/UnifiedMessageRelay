from command import command_listener
import global_vars
from utils import get_full_user_name, get_forward_index, send_all_except_current
from telegram.ext.dispatcher import DispatcherHandlerStop
import telegram


@command_listener('dice', 'dice', tg_only=True, description='throw a dice')
def dice(tg_group_id: int, tg_user: telegram.User, tg_message_id: int):
    forward_index = get_forward_index(tg_group_id=tg_group_id)
    if forward_index == -1:
        raise DispatcherHandlerStop()

    username = get_full_user_name(tg_user)
    msg = username + 'rolled a dice:'
    send_all_except_current(forward_index, msg, tg_group_id=tg_group_id)
    msg = '[CQ: dice]'
    send_all_except_current(forward_index, msg, tg_group_id=tg_group_id, auto_escape=False)


@command_listener('rps', 'rps', tg_only=True, description='rock paper stone')
def rps(tg_group_id: int, tg_user: telegram.User, tg_message_id: int):
    forward_index = get_forward_index(tg_group_id=tg_group_id)
    if forward_index == -1:
        raise DispatcherHandlerStop()

    username = get_full_user_name(tg_user)
    msg = username + 'played rock–paper–scissors:'
    send_all_except_current(forward_index, msg, tg_group_id=tg_group_id)
    msg = '[CQ: rps]'
    send_all_except_current(forward_index, msg, tg_group_id=tg_group_id, auto_escape=False)

