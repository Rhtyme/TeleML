from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior, RecycleDataAdapter

r_data = tuple(range(1, 101))


class MessageItem(RecycleDataViewBehavior, BoxLayout):
    index = None

    def onItemClick(self):
        print('onItemClick: ', self.index)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        # ind = data["user_name_label"]
        #        print('on refresh_view_attrs: data: ', ind)
        # self.ids.user_name_label.text = str(ind)
        # self.label_user_id.text = "helloooo"
        # self.index = index
        return super(MessageItem, self).refresh_view_attrs(
            rv, index, data)

    def refresh_view_layout(self, rv, index, layout, viewport):
        # self.label_user_id.text = "helloooo"
        return super(MessageItem, self).refresh_view_layout(
            rv, index, layout, viewport)


class ChatRV(RecycleView):
    def __init__(self, **kwargs):
        super(ChatRV, self).__init__(**kwargs)
        # https://www.gravatar.com/avatar/205e460b479e2e5b48aec07710c08d50
        #self.data = [{'value_label_user': str(x), 'value_label_msg': str(x),
        #              'value_avatar': 'https://www.gravatar.com/avatar/205e460b479e2e5b48aec07710c08d50'} for x in
        #             range(100)]
