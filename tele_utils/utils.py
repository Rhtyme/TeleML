
from telethon import TelegramClient

__api_id = 0
__api_hash = ''

__db_name = 'anon'

# test constants
dc = 0
dc_ip = ''
dc_port = 0

limit = 5

META_INFO_DATE = 'meta_info_date'

META_INFO_DIALOG_ID = 'meta_info_dialog_id'

META_INFO_MESSAGE_ID = 'meta_info_message_id'


class PagingDataSource:
    __current_page = -1
    __items = {}
    __total = 0

    def on_next_result_delivered(self, dialog_list, total):
        self.__current_page = self.__current_page + 1
        self.__total = total
        self.__set_items(self.__current_page, dialog_list)

    def __set_items(self, page, dialog_list):
        self.__items[page] = dialog_list
        self.__current_page = page

    def get_current_page_items(self):
        current_list = self.__items.get(self.__current_page)
        if not current_list:
            return []
        return current_list

    def get_current_page(self):
        return self.__current_page

    def page_info(self):
        if self.__current_page < 0:
            return 'No items found'
        hr_page = self.__current_page + 1
        cur_last = hr_page * limit
        if cur_last > self.__total:
            cur_last = self.__total

        cur_items_count = len(self.get_current_page_items())

        cur_first = cur_last - cur_items_count + 1
        print('on page_info: current_page: %d, hr_page: %d, cur_last: %d, cur_first: %d ' % (
            self.__current_page, hr_page, cur_last, cur_first))

        return str(cur_first) + '-' + str(cur_last) + ' of ' + str(self.__total)

    def has_next(self):
        total_current = (self.__current_page + 1) * limit
        return len(self.__items.values()) > 0 and self.__total > total_current

    def has_prev(self):
        return len(self.__items.values()) > 0 and self.__current_page > 0

    def is_empty(self):
        return not (len(self.__items.values()) > 0 and self.__current_page >= 0)

    def items_for_page(self, page):
        return self.__items.get(page)

    def prev(self):
        prev_page = self.__current_page - 1
        prev_list = self.__items.get(prev_page)
        if prev_list:
            self.__current_page = prev_page
        return prev_list

    def next(self):
        next_page = self.__current_page + 1
        next_list = self.__items.get(next_page)
        if next_list:
            self.__current_page = next_page
        return next_list

    def get_meta_info_last_row_current_items(self, meta_info_key, default_value):
        curr_list = self.get_current_page_items()
        if curr_list:
            meta_info = curr_list[-1][meta_info_key]
        else:
            meta_info = default_value
        return meta_info

    def get_total(self):
        return self.__total

    def clear(self):
        self.__current_page = -1
        self.__items = {}
        self.__total = 0


class TelegramClientImlp(TelegramClient):
    test_account = False


def init_tele_client(test=False):
    if not test:
        return TelegramClientImlp(__db_name, __api_id, __api_hash)
    else:
        client = TelegramClientImlp(None, __api_id, __api_hash)
        client.session.set_dc(dc, dc_ip, dc_port)
        client.test_account = True
        return client


async def is_authorized(client: TelegramClientImlp, callback):
    # if True:
    #     await asyncio.sleep(5)
    #     callback(False)
    #     return

    print('is_authorized called')
    if not client.test_account:
        await client.connect()
        res = await client.is_user_authorized()
        print('is_authorized result: ', res)
        callback(res)
    else:
        await client.connect()
        # await client.start(phone=number1, code_callback=lambda: '22222')
        res = await client.is_user_authorized()
        print('is_authorized result: ', res)
        callback(res)


async def send_code_request(client: TelegramClientImlp, phone: str, callback):
    print('send_code_request called')
    try:
        res = await client.send_code_request(phone)
        print('send request result: ', res)
        callback(phone, True)
    except Exception as e:
        print('send request error: ', e)
        callback(phone, False)


async def sign_in_request(client: TelegramClientImlp, phone: str, code: str, callback):
    print('sign_in_request called')
    try:
        res = await client.sign_in(phone=phone, code=code)
        print('sign_in_request result: ', res)
        callback(True)
    except Exception as e:
        print('sign_in_request error: ', e)
        callback(False)


'''below are telegram dialog methods'''


async def get_current_or_next_dialogs(client: TelegramClientImlp, data_source: PagingDataSource, callback):
    if not data_source.is_empty():
        callback(True)
    else:
        await get_next_dialogs(client, data_source, callback)


async def get_next_dialogs(client: TelegramClientImlp, data_source: PagingDataSource, callback):
    print('on get_next_dialogs, current_page: ', data_source.get_current_page())
    local_dialogs = data_source.next()
    if local_dialogs:
        callback(True)
    else:
        last_date = data_source.get_meta_info_last_row_current_items(META_INFO_DATE, default_value=None)
        try:
            dialogs = await client.get_dialogs(limit=limit, offset_date=last_date)
            if dialogs:
                parsed = parse_dialogs(dialogs)
                data_source.on_next_result_delivered(parsed, total=dialogs.total)
                callback(True)
            else:
                raise Exception('dialogs empty')
        except Exception as e:
            print('could not fetch dialogs, ', e)
            callback(False)


def get_prev_dialogs(client: TelegramClientImlp, data_source: PagingDataSource, callback):
    print('on get_prev_dialogs, current_page: ', data_source.get_current_page())
    if not data_source.has_prev():
        callback(False)
    else:
        local_dialogs = data_source.prev()
        if local_dialogs:
            callback(True)
        else:
            # todo if local_dialogs does not exist do something!!!
            print('local dialogs does not exist!!!')
            callback(False)


def parse_dialogs(dialogs):
    parsed = []
    for dialog in dialogs:
        msg = dialog.message.message
        if not msg:
            msg = "no message"
        parsed.append({'value_dialog_title': dialog.title, 'value_dialog_msg': msg,
                       META_INFO_DATE: dialog.date, 'value_dialog_id': dialog.id})

    return parsed


'''----------above are telegram dialog methods'''

'''below are telegram message methods'''


async def get_current_or_next_messages(client: TelegramClientImlp, chat_id, data_source: PagingDataSource, model,
                                       callback):
    if not data_source.is_empty():
        callback(True)
    else:
        await get_next_messages(client, chat_id, data_source, model, callback)


async def get_next_messages(client: TelegramClientImlp, chat_id, data_source: PagingDataSource, model, callback):
    print('on get_next_messages, current_page: ', data_source.get_current_page())
    local_messages = data_source.next()
    if local_messages:
        callback(True)
    else:
        last_id = data_source.get_meta_info_last_row_current_items(META_INFO_MESSAGE_ID, 0)
        try:
            print('on fetching messages, params: chat_id: %s, limit: %s, last_id:%s' % (
                str(chat_id), str(limit), str(last_id)))
            messages = await client.get_messages(chat_id, limit=limit, offset_id=last_id)
            if messages:
                parsed = parse_messages(messages, model)
                data_source.on_next_result_delivered(parsed, total=messages.total)
                callback(True)
            else:
                raise Exception('messages empty')
        except Exception as e:
            print('could not fetch messages, ', e)
            callback(False)


def get_prev_messages(client: TelegramClientImlp, chat_id, data_source: PagingDataSource, callback):
    print('on get_prev_dialogs, current_page: ', data_source.get_current_page())
    if not data_source.has_prev():
        callback(False)
    else:
        local_dialogs = data_source.prev()
        if local_dialogs:
            callback(True)
        else:
            # todo if local_dialogs does not exist do something!!!
            print('local dialogs does not exist!!!')
            callback(False)


def parse_messages(messages, model):
    parsed = []
    print('got messages, total: %s, fields: ' % messages.total)
    for message in messages:
        # message: message.message
        # sender info:
        #       firstname: message.sender.first_name
        #       lastname: message.sender.last_name
        #       phone: message.sender.phone
        #       username: message.sender.username
        # sender_id: message.sender_id
        # text: message.text
        # id: message.id
        # date: message.date (in datetime format, 2020-12-06 07:13:17+00:00)
        author = ''
        sender = message.sender

        if hasattr(sender, 'first_name') and sender.first_name:
            author = author + str(sender.first_name) + ' '
        if hasattr(sender, 'title') and sender.title:
            author = author + str(sender.title)
        if hasattr(sender, 'last_name') and sender.last_name:
            author = author + str(sender.last_name) + ', '
        if hasattr(sender, 'username') and sender.username:
            author = author + str(sender.username)
        msg_date = message.date.strftime("%m/%d/%Y, %H:%M")
        msg = message.message
        sentiment_text = 'Sentiment is not applicable!'
        if not msg:
            msg = message.text
        else:
            sentiment, confidence, probabilities = model.predict(msg)
            sentiment_text = get_sentiment_text(sentiment, confidence)
        if not msg:
            msg = "no message"

        parsed.append({'value_message_text': msg, 'value_message_author': author,
                       'value_message_sentiment_score': sentiment_text,
                       'value_message_date': msg_date, META_INFO_DATE: message.date,
                       META_INFO_MESSAGE_ID: message.id})
        print('id: %s, author: %s, message: %s, last_date: %s' % (message.id, author, message.message, message.date))
    return parsed


def get_sentiment_text(sentiment, confidence):
    text = ''
    if sentiment and confidence:
        text = sentiment + " {:.3%}".format(float(confidence))
    return text


'''----------above are telegram messages methods'''


async def log_out(client: TelegramClientImlp, callback):
    res = await client.log_out()
    await client.disconnect()
    callback(res)
