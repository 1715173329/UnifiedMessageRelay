#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from bot_constant import *
import global_vars

from telegram.ext import Updater, CommandHandler

import logging
from DaemonClass import Daemon
import sys

from cqhttp import CQHttp

# region log
logger = logging.getLogger(__name__)
hdlr = logging.FileHandler('bot.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

# endregion


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def start(bot, update):
    update.message.reply_text('This is a QQ <-> Telegram Relay bot, source code is available on [Github](https://github.com/jqqqqqqqqqq/coolq-telegram-bot)', parse_mode='Markdown')


class MainProcess(Daemon):
    def run(self):
        qq_bot = CQHttp(api_root='http://127.0.0.1:5700/',
                        access_token='your-token',
                        secret='your-secret')

        global_vars.qq_bot = qq_bot
        global_vars.tg_bot_id = int(TOKEN.split(':')[0])

        updater = Updater(TOKEN)
        job_queue = updater.job_queue
        global_vars.tg_bot = updater.bot
        # Get the dispatcher to register handlers
        dp = updater.dispatcher
        global_vars.dp = dp
        dp.add_error_handler(error)
        dp.add_handler(CommandHandler('start', start), group=0)

        qq_bot.start()  # start bot before add handler, in order to execute init correctly
        updater.start_polling(poll_interval=1.0, timeout=200)

        import plugins  # load all plugins

        # Block until the you presses Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()


def main():
    daemon = MainProcess('/tmp/coolq-telegram-bot.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        elif 'run' == sys.argv[1]:
            daemon.run()
        else:
            print('error processing command')
            print("usage: %s start|stop|restart|run" % sys.argv[0])
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart|run" % sys.argv[0])
        sys.exit(2)


if __name__ == '__main__':
    main()
