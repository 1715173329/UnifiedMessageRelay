import shelve
import datetime
import time
from bot_constant import FORWARD_LIST


class MessageDB:
    def __init__(self, db_name: str):
        self.db = shelve.open(db_name, writeback=True)
        for idx, forward in enumerate(FORWARD_LIST):
            if str(idx) not in self.db:
                self.db[str(idx)] = dict()

    def append_message(self, qq_message_id: int, tg_message_id, forward_index: int, qq_number: int):
        """
        append qq message list to database
        :param qq_message_id: QQ message id
        :param tg_message_id: Telegram message id
        :param forward_index: forward index
        :param qq_number: If from QQ, then QQ sender's number. If from Telegram, then 0 (used for recall)
        :return:
        """
        self.db[str(forward_index)][str(tg_message_id)] = [int(time.mktime(datetime.datetime.now().timetuple())),
                                                           qq_message_id,
                                                           qq_number]

    def retrieve_message(self, tg_message_id: int, forward_index: int):
        if str(tg_message_id) in self.db[str(forward_index)]:
            return self.db[str(forward_index)][str(tg_message_id)][1:]
        else:
            return None

    def purge_message(self):
        for outer_key, forward in self.db.items():
            for key, value in forward.items():
                timestamp = datetime.datetime.utcfromtimestamp(value[0])
                if datetime.datetime.now() - timestamp > datetime.timedelta(weeks=2):
                    del self.db[outer_key][key]

    def __del__(self):
        self.db.close()
