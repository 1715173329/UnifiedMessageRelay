import global_vars
from cqsdk import RcvdGroupMessage
from cq_utils import cq_regex, cq_share_regex, cq_music_regex, cq_dice_regex,\
    cq_custom_music_regex, cq_shake_regex, cq_rps_regex, cq_record_regex, cq_rich_regex, \
    extract_cq_share, extract_cq_dice, extract_cq_music, extract_cq_record, \
    extract_cq_rich, extract_cq_rps, extract_cq_custom_music
from utils import get_forward_index, get_qq_name


@global_vars.qq_bot.listener((RcvdGroupMessage, ), 99)  # priority 100
def new(message):
    qq_group_id = int(message.group)
    _, tg_group_id, forward_index = get_forward_index(qq_group_id=qq_group_id)
    if cq_regex.match(message.text):
        text = ''
        if cq_dice_regex.match(message.text):
            dice = extract_cq_dice(message.text)
            text = '掷出了 <b>' + str(dice) + '</b>'
        elif cq_shake_regex.match(message.text):
            text = '发送了一个抖动'
        elif cq_rps_regex.match(message.text):
            rps = extract_cq_rps(message.text)
            text = '出了 <b>' + {'1': '石头', '2': '剪刀', '3': '布'}[rps] + '</b>'
        elif cq_rich_regex.match(message.text):
            url, _text = extract_cq_rich(message.text)
            if url:
                text = '<a href="' + url + '">' + _text + '</a>'
            else:
                text = _text
        elif cq_share_regex.match(message.text):
            url, title, content, image_url = extract_cq_share(message.text)
            text = '分享了<a href="' + url + '">' + title + '</a>'
        elif cq_custom_music_regex.match(message.text):
            url, audio, title, content, image = extract_cq_custom_music(message.text)
            text = '分享了<a href="' + url + '">' + title + '</a>'
        elif cq_music_regex.match(message.text):
            _type, _id = extract_cq_music(message.text)
            text = '分享了<a href="https://y.qq.com/n/yqq/song/' + + str(_id) + + '_num.html"> qq 音乐</a>'
        elif cq_record_regex.match(message.text):
            file, magic = extract_cq_record(message.text)
            text = '说了句话，懒得转了'
        if text:
            full_msg = '<b>' + get_qq_name(int(message.qq), forward_index) + '</b>: ' + text.strip()
            global_vars.tg_bot.sendMessage(tg_group_id, full_msg, parse_mode='HTML')
            return True
    return False
