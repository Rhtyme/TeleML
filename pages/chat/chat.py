import asyncio
import atexit

from kivy.properties import ObjectProperty
from kivymd.toast import toast
from kivymd.uix.list import TwoLineAvatarListItem, ImageLeftWidget
from pydispatch import dispatcher

from pages import event_signals
from pages.base_screen import BaseScreen
from kivy.clock import Clock

from tele_utils.utils import PagingDataSource
from tele_utils import utils as tele_helper


class ChatScreen(BaseScreen):
    chat_title = ''
    chat_id = 0

    def setup_info(self, title_, id_):
        self.chat_title = title_
        self.chat_id = id_
        self.data_source.clear()

    def __init__(self, *args, **kwargs):
        BaseScreen.__init__(self, *args, **kwargs)
        self.data_source = PagingDataSource()
        atexit.register(self.on_clean)
        self.setup_event_signal_dispatcher()

    def on_enter(self, *args):
        print('DialogList: on_enter')
        self.ids.toolbar_chat.left_action_items = [["arrow-left", lambda x: self.on_back_pressed()]]
        client = self.root.client
        # coro = tele_helper.is_authorized(client, self.on_messages_fetch)
        model = self.root.model
        toast('Loading messages, please be patient...')
        coro = tele_helper.get_current_or_next_messages(client, self.chat_id, self.data_source, model,
                                                        self.on_messages_fetch)
        Clock.schedule_once(self._finish_init, 0.5)
        asyncio.get_event_loop().run_until_complete(coro)

    def on_next_page_btn_click(self, sender):
        print('on_next_page_btn_click called***')
        model = self.root.model
        coro = tele_helper.get_next_messages(self.root.client, self.chat_id, self.data_source, model,
                                             self.on_messages_fetch)
        asyncio.get_event_loop().run_until_complete(coro)

    def on_prev_page_btn_click(self, sender):
        print('on_prev_page_btn_click called***')
        tele_helper.get_prev_messages(self.root.client, self.chat_id, self.data_source, self.on_messages_fetch)

    def on_messages_fetch(self, result):
        print('on_messages_fetch called, result: ', result)
        toast('Messages loaded!')
        messages = self.data_source.get_current_page_items()
        self.ids.rv_messages.data = messages
        self.ids.paging_layout_chat.set_page_info_text(self.data_source.page_info())

    def _finish_init(self, dt):
        print(self.ids)
        self.ids.paging_layout_chat.setup_signal_event_prefix(event_signals.MESSAGES_PREFIX)

    def on_back_pressed(self):
        self.on_clean()
        self.root.on_chat_back_btn_pressed()

    def setup_event_signal_dispatcher(self):
        next_, prev_ = event_signals.get_paging_btn_clicks(event_signals.MESSAGES_PREFIX)
        dispatcher.connect(self.on_next_page_btn_click, signal=next_,
                           sender=dispatcher.Any)
        dispatcher.connect(self.on_prev_page_btn_click, signal=prev_,
                           sender=dispatcher.Any)

    def on_clean(self):
        print('Chat screen on called----')
        self.ids.rv_messages.data = []
        self.data_source.clear()
