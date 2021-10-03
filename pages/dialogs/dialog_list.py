import atexit

from kivy.properties import ObjectProperty
from pages.base_screen import BaseScreen
from kivy.clock import Clock
from tele_utils.utils import PagingDataSource
from pydispatch import dispatcher

from tele_utils import utils as tele_helper
import asyncio
import pages.event_signals as event_signals


class DialogList(BaseScreen):
    code = ObjectProperty()
    phone: str

    def __init__(self, *args, **kwargs):
        BaseScreen.__init__(self, *args, **kwargs)
        print('DialogList init ***')
        # Clock.schedule_once(self.populateList(), 1)
        self.data_source = PagingDataSource()
        atexit.register(self.on_clean)
        self.setup_event_signal_dispatcher()

    def onItemClick(self):
        print('DialogList, onItemClick: ')
        self.root.on_dialog_item_press()

    def on_enter(self, *args):
        print('DialogList: on_enter')
        self.ids.toolbar.right_action_items = [["logout", lambda x: self.root.on_logout_press()]]
        client = self.root.client
        # coro = tele_helper.is_authorized(client, self.on_dialog_fetch)
        coro = tele_helper.get_current_or_next_dialogs(client, self.data_source, self.on_dialog_fetch)
        Clock.schedule_once(self._finish_init, 0.5)
        asyncio.get_event_loop().run_until_complete(coro)

        # asynckivy.start(coro)
        # self.populateList()

    def on_next_page_btn_click(self, sender):
        print('on_next_page_btn_click called***')
        coro = tele_helper.get_next_dialogs(self.root.client, self.data_source, self.on_dialog_fetch)
        asyncio.get_event_loop().run_until_complete(coro)

    def on_prev_page_btn_click(self, sender):
        print('on_prev_page_btn_click called***')
        tele_helper.get_prev_dialogs(self.root.client, self.data_source, self.on_dialog_fetch)

    def _finish_init(self, param):
        print(self.ids)
        self.ids.paging_layout_dialog.setup_signal_event_prefix(event_signals.DIALOGS_PREFIX)

    def on_sign_in_pressed(self):
        print(' login pressed, code: ', self.code)
        # self.root.ids.w_toolbar.left_action_items.append(menu)

    def on_dialog_fetch(self, result):
        print('on_dialog_fetch called, result: ', result)

        dialogs = self.data_source.get_current_page_items()
        self.ids.dialogs_rv.data = dialogs
        self.ids.paging_layout_dialog.set_page_info_text(self.data_source.page_info())
        # for dialog in dialogs:
        #     # last_message: = dialog.message.message
        #     # title:  dialog.title
        #     #picture: dialog.entity.photo
        #
        #     print('{:>14}: {}'.format(dialog.id, dialog.title))

    def on_back_to_phone_pressed(self):
        print(' on_back_to_phone pressed')
        self.root.on_back_to_phone_pressed()

    def on_clean(self):
        print('Dialog list screen on called----')
        self.ids.dialogs_rv.data = []
        self.data_source.clear()

    def setup_event_signal_dispatcher(self):
        next_, prev_ = event_signals.get_paging_btn_clicks(event_signals.DIALOGS_PREFIX)
        dispatcher.connect(self.on_next_page_btn_click, signal=next_,
                           sender=dispatcher.Any)
        dispatcher.connect(self.on_prev_page_btn_click, signal=prev_,
                           sender=dispatcher.Any)
