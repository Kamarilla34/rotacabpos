import requests
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import TwoLineAvatarIconListItem, ImageLeftWidget
from kivy.clock import Clock

# --- DİKKAT: BURAYA KENDİ SİTE ADRESİNİ YAZ ---
BASE_URL = "https://kamarilla.pythonanywhere.com"

KV = '''
ScreenManager:
    LoginScreen:
    DashboardScreen:
    HistoryScreen:

<LoginScreen>:
    name: "login"
    MDCard:
        size_hint: .85, .5
        pos_hint: {"center_x": .5, "center_y": .5}
        elevation: 10
        padding: 25
        spacing: 25
        orientation: "vertical"
        radius: [20,]

        MDLabel:
            text: "Sürücü Girişi"
            font_style: "H5"
            halign: "center"
            theme_text_color: "Primary"

        MDTextField:
            id: tckn
            hint_text: "TC Kimlik No"
            icon_right: "account"
            mode: "rectangle"

        MDTextField:
            id: pin
            hint_text: "PIN Kodu"
            icon_right: "key"
            password: True
            mode: "rectangle"

        MDRaisedButton:
            text: "GİRİŞ YAP"
            font_size: "18sp"
            pos_hint: {"center_x": .5}
            on_release: root.do_login()

<DashboardScreen>:
    name: "dashboard"
    MDBoxLayout:
        orientation: 'vertical'

        MDTopAppBar:
            title: "Taksi POS Terminali"
            right_action_items: [["history", lambda x: app.show_history()], ["logout", lambda x: app.logout()]]
            elevation: 4

        MDBoxLayout:
            orientation: 'vertical'
            padding: 30
            spacing: 30
            pos_hint: {"center_x": .5, "center_y": .6}

            MDLabel:
                id: lbl_welcome
                text: "Hoşgeldiniz"
                halign: "center"
                font_style: "H6"

            MDTextField:
                id: amount
                hint_text: "Tutar (TL)"
                helper_text: "Örn: 150.50"
                helper_text_mode: "on_focus"
                icon_right: "currency-try"
                font_size: "32sp"
                mode: "fill"
                halign: "center"

            MDRaisedButton:
                text: "ÖDEME AL"
                font_size: "24sp"
                size_hint_x: 1
                md_bg_color: 0, 0.7, 0, 1
                on_release: root.process_payment()

            Widget:

<HistoryScreen>:
    name: "history"
    MDBoxLayout:
        orientation: 'vertical'

        MDTopAppBar:
            title: "Geçmiş İşlemler"
            left_action_items: [["arrow-left", lambda x: app.go_back()]]
            elevation: 4

        ScrollView:
            MDList:
                id: history_list
'''

class LoginScreen(Screen):
    def do_login(self):
        tckn = self.ids.tckn.text
        pin = self.ids.pin.text

        if not tckn or not pin:
            self.show_alert("Hata", "Lütfen alanları doldurun.")
            return

        try:
            url = f"{BASE_URL}/api/login"
            data = {'tckn': tckn, 'pin': pin}
            # verify=False, SSL hatası almamak için (Geçici çözüm)
            response = requests.post(url, data=data, timeout=10)

            if response.status_code == 200:
                json_data = response.json()
                app = MDApp.get_running_app()
                app.driver_id = json_data['driver_id']
                app.driver_name = json_data['driver_name']

                self.manager.get_screen('dashboard').ids.lbl_welcome.text = f"Sürücü: {app.driver_name}\nAraç: {json_data['plate']}"
                self.manager.current = 'dashboard'
            else:
                self.show_alert("Giriş Başarısız", "TCKN veya Şifre hatalı.")

        except Exception as e:
            self.show_alert("Bağlantı Hatası", str(e))

    def show_alert(self, title, text):
        dialog = MDDialog(title=title, text=text, buttons=[MDFlatButton(text="TAMAM", on_release=lambda x: dialog.dismiss())])
        dialog.open()

class DashboardScreen(Screen):
    def process_payment(self):
        amount = self.ids.amount.text
        app = MDApp.get_running_app()

        if not amount.replace('.','',1).isdigit():
            self.show_alert("Hata", "Geçerli bir tutar girin.")
            return

        try:
            url = f"{BASE_URL}/api/pos_payment"
            data = {'driver_id': app.driver_id, 'amount': amount}

            response = requests.post(url, data=data, timeout=15)

            if response.status_code == 200:
                self.show_alert("BAŞARILI", f"{amount} TL Ödeme Alındı!\nFiş sisteme işlendi.")
                self.ids.amount.text = ""
            else:
                err_msg = response.json().get('message', 'Bilinmeyen Hata')
                self.show_alert("HATA", err_msg)

        except Exception as e:
            self.show_alert("Sunucu Hatası", str(e))

    def show_alert(self, title, text):
        dialog = MDDialog(title=title, text=text, buttons=[MDFlatButton(text="TAMAM", on_release=lambda x: dialog.dismiss())])
        dialog.open()

class HistoryScreen(Screen):
    def on_enter(self):
        # Listeyi temizle
        self.ids.history_list.clear_widgets()
        app = MDApp.get_running_app()

        if not app.driver_id: return

        # Sunucudan geçmişi çek
        try:
            url = f"{BASE_URL}/api/driver_history/{app.driver_id}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                history_data = response.json()

                if not history_data:
                    self.add_item("Henüz işlem yok.", "gray")
                    return

                for item in history_data:
                    status = item.get('status', 'UNKNOWN')
                    amount = item.get('amount', 0)
                    date = item.get('date', '')

                    # Renk ve İkon Mantığı
                    if "SUCCESS" in status or "SENT" in status:
                        icon = "check-circle"
                        color = (0, 0.7, 0, 1) # Yeşil
                        desc = "Başarılı"
                    elif "PENDING" in status:
                        icon = "clock-outline"
                        color = (1, 0.7, 0, 1) # Turuncu
                        desc = "Bekliyor"
                    else:
                        icon = "close-circle"
                        color = (0.9, 0, 0, 1) # Kırmızı
                        desc = "Hata"

                    self.add_item(f"{amount} TL", desc, f"{date}", icon, color)
            else:
                self.add_item("Veri Alınamadı", "red")

        except Exception as e:
            self.add_item(f"Hata: {str(e)}", "red")

    def add_item(self, text, desc, date="", icon="alert-circle", color=(0.5,0.5,0.5,1)):
        if desc == "red": color = (1,0,0,1)

        item = TwoLineAvatarIconListItem(
            text=text,
            secondary_text=f"{date} - {desc}"
        )
        img = ImageLeftWidget(icon=icon)
        img.theme_text_color = "Custom"
        img.text_color = color

        item.add_widget(img)
        self.ids.history_list.add_widget(item)

class TaksiApp(MDApp):
    driver_id = None
    driver_name = ""

    def build(self):
        self.theme_cls.primary_palette = "Amber"
        self.theme_cls.theme_style = "Light"
        return Builder.load_string(KV)

    def show_history(self):
        self.root.current = 'history'

    def go_back(self):
        self.root.current = 'dashboard'

    def logout(self):
        self.driver_id = None
        self.root.current = 'login'

if __name__ == '__main__':
    TaksiApp().run()
