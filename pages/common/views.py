from kivy.uix.boxlayout import BoxLayout
from pydispatch import dispatcher
import pages.event_signals as event_signals


class PagingLayout(BoxLayout):
    signal_on_prev_click = event_signals.PAGING_ON_PREV_PAGE_BTN_CLICK
    signal_on_next_click = event_signals.PAGING_ON_NEXT_PAGE_BTN_CLICK

    def set_page_info_text(self, info: str):
        self.ids.page_info_label.text = info

    def on_prev_btn_click(self):
        print('on_prev_btn_click clicked signal: ', self.signal_on_prev_click)
        dispatcher.send(signal=self.signal_on_prev_click, sender={})

    def on_next_btn_click(self):
        print('on_next_btn_click clicked signal: ', self.signal_on_next_click)
        dispatcher.send(signal=self.signal_on_next_click, sender={})

    def setup_signal_event_prefix(self, event_name_prefix):
        self.signal_on_next_click, self.signal_on_prev_click = event_signals.get_paging_btn_clicks(event_name_prefix)
