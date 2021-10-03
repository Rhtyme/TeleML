from kivy.properties import ObjectProperty
from kivymd.toast import toast

from pages.base_screen import BaseScreen


class SignInCode(BaseScreen):
    code = ObjectProperty()
    phone: str

    def __init__(self, *args, **kwargs):
        BaseScreen.__init__(self, *args, **kwargs)
        print('SignInCode init ***')

    # def _finish_init(self, dt):
    #     print(self.ids)

    def on_sign_in_pressed(self):
        code_ = self.code.text
        print(' login pressed, code: ', code_)
        if not code_:
            toast('Code can not be empty')
            return
        self.root.on_sign_in_btn_pressed(phone=self.phone, code=code_)

    def on_back_to_phone_pressed(self):
        print(' on_back_to_phone pressed')
        self.root.on_back_to_phone_pressed()
