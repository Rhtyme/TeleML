from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivymd.uix.list import TwoLineAvatarListItem
from pydispatch import dispatcher
from pages.screen_names import SCREEN_DIALOGS


class TwoLineAvatarListItemImpl(RecycleDataViewBehavior, TwoLineAvatarListItem):
    index = None

    def onItemClick(self, value_dialog_id, value_dialog_title):
        # todo fix the below temporary solution:
        self.get_root_window().children[0].on_dialog_item_press(value_dialog_id, value_dialog_title)
        # self.parent.parent.parent.onItemClick()
        print('onItemClick: ', self.index)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(TwoLineAvatarListItemImpl, self).refresh_view_attrs(
            rv, index, data)


class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        # self.data = [{'text': str(x)} for x in range(100)]
