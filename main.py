import requests
import urllib3
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, TwoLineAvatarIconListItem, IconLeftWidget
from kivymd.toast import toast
from kivy.properties import StringProperty
from kivy.core.window import Window

# --- AYARLAR ---
# Eski Android cihazlarda (General Mobile vb.) SSL hatasını yoksay
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# API URL'leri
API_BASE_URL = "https://taksipos-api.onrender.com"
LOGIN_URL = f"{API_BASE_URL}/login"
PAYMENT_URL = f"{API_BASE_URL}/process-payment"
HISTORY_URL = f"{API_BASE_URL}/payment-history"

KV = """
MDScreenManager:
    LoginScreen:
    MainScreen:
    HistoryScreen:

# === 1. GİRİŞ EKRANI ===
<LoginScreen>:
    name: 'login'
    md_bg_color: 0.1, 0.1, 0.1, 1

    MDBoxLayout:
        orientation: 'vertical'
        padding: "20dp"
        spacing: "20dp"
        pos_hint: {"center_x": .5, "center_y": .6} # Klavye açılınca yukarı kaysın diye

        # Logo veya Başlık
        MDIconButton:
            icon: "taxi"
            user_font_size: "64sp"
            theme_text_color: "Custom"
            text_color: 1, 0.8, 0, 1 # Sarı
            pos_hint: {"center_x": .5}

        MDLabel:
            text: "RotaCab POS"
            halign: "center"
            font_style: "H4"
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            bold: True

        Widget:
            size_hint_y: None
            height: "20dp"

        # Giriş Alanları
        MDTextField:
            id: user_input
            hint_text: "Kullanıcı Adı"
            mode: "fill"
            fill_color_normal: 0.2, 0.2, 0.2, 1
            fill_color_focus: 0.3, 0.3, 0.3, 1
            text_color_normal: 1, 1, 1, 1
            text_color_focus: 1, 1, 1, 1
            hint_text_color_normal: 0.7, 0.7, 0.7, 1
            hint_text_color_focus: 1, 0.8, 0, 1
            icon_right: "account"
            icon_right_color: 1, 0.8, 0, 1

        MDTextField:
            id: pass_input
            hint_text: "Şifre"
            password: True
            mode: "fill"
            fill_color_normal: 0.2, 0.2, 0.2, 1
            fill_color_focus: 0.3, 0.3, 0.3, 1
            text_color_normal: 1, 1, 1, 1
            text_color_focus: 1, 1, 1, 1
            hint_text_color_normal: 0.7, 0.7, 0.7, 1
            hint_text_color_focus: 1, 0.8, 0, 1
            icon_right: "key"
            icon_right_color: 1, 0.8, 0, 1

        Widget:
            size_hint_y: None
            height: "10dp"

        MDRaisedButton:
            id: login_btn
            text: "GİRİŞ YAP"
            font_size: "18sp"
            size_hint_x: 1
            height: "50dp"
            md_bg_color: 1, 0.6, 0, 1
            text_color: 0, 0, 0, 1
            bold: True
            on_release: root.do_login()

        Widget:
            size_hint_y: 1 # Boşluk doldurucu

# === 2. ANA POS EKRANI ===
<MainScreen>:
    name: 'main'
    md_bg_color: 0.1, 0.1, 0.1, 1

    MDBoxLayout:
        orientation: 'vertical'
        padding: "10dp"
        spacing: "10dp"

        # --- ÜST BİLGİ PANELİ ---
        MDCard:
            size_hint_y: None
            height: "70dp"
            md_bg_color: 0.2, 0.2, 0.2, 1
            radius: [10]
            padding: "5dp"
            
            # Geçmiş Butonu
            MDIconButton:
                icon: "history"
                theme_text_color: "Custom"
                text_color: 1, 0.8, 0, 1
                pos_hint: {"center_y": .5}
                on_release: root.go_to_history()

            MDBoxLayout:
                orientation: "vertical"
                pos_hint: {"center_y": .5}
                padding: ["10dp", 0, 0, 0]
                
                MDLabel:
                    text: "Şoför: İbrahim Efe Çolak"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    bold: True
                    font_style: "Subtitle1"
                    font_size: "14sp"
                
                MDLabel:
                    text: "34 ROTA 01"
                    theme_text_color: "Custom"
                    text_color: 1, 0.8, 0, 1
                    font_style: "Caption"
            
            # Çıkış Butonu
            MDIconButton:
                icon: "logout"
                theme_text_color: "Custom"
                text_color: 1, 0.2, 0.2, 1
                pos_hint: {"center_y": .5}
                on_release: root.logout()

        # --- RAKAM EKRANI ---
        MDCard:
            orientation: "vertical"
            size_hint_y: 0.30
            md_bg_color: 0, 0, 0, 1
            radius: [5]
            padding: "10dp"
            line_color: 1, 0.8, 0, 0.5
            
            MDLabel:
                text: "Tutar Giriniz (TL)"
                theme_text_color: "Custom"
                text_color: 0.5, 0.5, 0.5, 1
                font_style: "Caption"
            
            MDLabel:
                text: root.display_amount + " ₺"
                halign: "right"
                font_style: "H4"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                bold: True

            MDBoxLayout:
                size_hint_y: None
                height: "1dp"
                md_bg_color: 0.3, 0.3, 0.3, 1

            MDGridLayout:
                cols: 2
                size_hint_y: None
                height: "50dp"
                
                MDLabel:
                    text: "+ Hizmet (%13):"
                    theme_text_color: "Custom"
                    text_color: 0.7, 0.7, 0.7, 1
                    font_style: "Caption"
                
                MDLabel:
                    text: root.display_service_fee + " ₺"
                    halign: "right"
                    theme_text_color: "Custom"
                    text_color: 1, 0.8, 0, 1
                    font_style: "Caption"
                    
                MDLabel:
                    text: "GENEL TOPLAM:"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    bold: True
                    font_style: "Subtitle2"
                
                MDLabel:
                    text: root.display_total + " ₺"
                    halign: "right"
                    theme_text_color: "Custom"
                    text_color: 0, 1, 0, 1
                    bold: True
                    font_style: "H6"

        # --- TUŞ TAKIMI (Klavye Yok!) ---
        MDGridLayout:
            cols: 3
            spacing: "8dp"
            size_hint_y: 0.55
            
            NumpadButton:
                text: "1"
                on_release: root.add_digit("1")
            NumpadButton:
                text: "2"
                on_release: root.add_digit("2")
            NumpadButton:
                text: "3"
                on_release: root.add_digit("3")
            
            NumpadButton:
                text: "4"
                on_release: root.add_digit("4")
            NumpadButton:
                text: "5"
                on_release: root.add_digit("5")
            NumpadButton:
                text: "6"
                on_release: root.add_digit("6")
            
            NumpadButton:
                text: "7"
                on_release: root.add_digit("7")
            NumpadButton:
                text: "8"
                on_release: root.add_digit("8")
            NumpadButton:
                text: "9"
                on_release: root.add_digit("9")
            
            MDIconButton:
                icon: "backspace"
                theme_text_color: "Custom"
                text_color: 1, 0.2, 0.2, 1
                size_hint: 1, 1
                on_release: root.remove_digit()

            NumpadButton:
                text: "0"
                on_release: root.add_digit("0")

            MDRaisedButton:
                id: pay_btn
                text: "KREDİ KARTI"
                md_bg_color: 1, 0.6, 0, 1
                text_color: 0, 0, 0, 1
                size_hint: 1, 1
                bold: True
                font_size: "16sp"
                on_release: root.process_payment()

<NumpadButton@MDFlatButton>:
    font_size: "26sp"
    size_hint: 1, 1
    theme_text_color: "Custom"
    text_color: 1, 1, 1, 1
    md_bg_color: 0.18, 0.18, 0.18, 1

# === 3. GEÇMİŞ İŞLEMLER EKRANI ===
<HistoryScreen>:
    name: 'history'
    on_enter: root.load_history()
    md_bg_color: 0.95, 0.95, 0.95, 1

    MDBoxLayout:
        orientation: 'vertical'

        MDBoxLayout:
            size_hint_y: None
            height: "56dp"
            md_bg_color: 0.1, 0.1, 0.1, 1
            padding: "10dp"
            
            MDIconButton:
                icon: "arrow-left"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                on_release: root.go_back()
            
            MDLabel:
                text: "Geçmiş İşlemler"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                bold: True
                font_style: "H6"
            
            Widget:
                size_hint_x: None
                width: "40dp"

        MDScrollView:
            MDList:
                id: history_list
"""

# --- PYTHON KODLARI ---

class LoginScreen(MDScreen):
    def do_login(self):
        username = self.ids.user_input.text
        password = self.ids.pass_input.text

        if not username or not password:
            toast("Lütfen bilgileri doldurun.")
            return

        self.ids.login_btn.text = "GİRİŞ YAPILIYOR..."
        self.ids.login_btn.disabled = True
        
        # API İSTEĞİ (SSL Kapalı)
        try:
            resp = requests.post(
                LOGIN_URL, 
                json={'username': username, 'password': password},
                timeout=10,
                verify=False # DİKKAT: Eski telefonlar için hayat kurtarıcı!
            )

            if resp.status_code == 200:
                token = resp.json().get('access_token')
                app = MDApp.get_running_app()
                app.user_token = token # Token'ı hafızaya at
                
                toast("Giriş Başarılı! Hoşgeldiniz.")
                self.manager.current = 'main' # Ana ekrana geç
            else:
                toast("Hatalı Kullanıcı Adı veya Şifre")
        
        except Exception as e:
            toast(f"Bağlantı Hatası: {str(e)}")
        
        finally:
            self.ids.login_btn.text = "GİRİŞ YAP"
            self.ids.login_btn.disabled = False


class MainScreen(MDScreen):
    display_amount = StringProperty("0")
    display_service_fee = StringProperty("0.00")
    display_total = StringProperty("0.00")
    raw_amount_str = ""

    def add_digit(self, digit):
        if self.raw_amount_str == "" and digit == "0": return
        if len(self.raw_amount_str) > 6: return
        self.raw_amount_str += digit
        self.calculate()

    def remove_digit(self):
        self.raw_amount_str = self.raw_amount_str[:-1]
        self.calculate()

    def calculate(self):
        if not self.raw_amount_str:
            self.display_amount = "0"
            self.display_service_fee = "0.00"
            self.display_total = "0.00"
            return
        try:
            amount = float(self.raw_amount_str)
            service_fee = amount * 0.13
            total = amount + service_fee
            self.display_amount = f"{amount:,.0f}"
            self.display_service_fee = f"{service_fee:,.2f}"
            self.display_total = f"{total:,.2f}"
        except:
            pass

    def process_payment(self):
        app = MDApp.get_running_app()
        token = app.user_token

        if not self.raw_amount_str or float(self.raw_amount_str) == 0:
            toast("Lütfen tutar giriniz!")
            return
        
        if not token:
            toast("Oturum süresi dolmuş, lütfen tekrar giriş yapın.")
            self.manager.current = 'login'
            return

        try:
            amount = float(self.raw_amount_str)
            self.ids.pay_btn.text = "İŞLENİYOR..."
            self.ids.pay_btn.disabled = True
            
            headers = {'Authorization': f'Bearer {token}'}
            
            # API İsteği (SSL Kapalı)
            response = requests.post(
                PAYMENT_URL, 
                json={'amount': amount}, 
                headers=headers, 
                timeout=15,
                verify=False
            )
            
            if response.status_code == 200:
                self.show_success_dialog()
                self.raw_amount_str = ""
                self.calculate()
            else:
                toast("❌ Kart Reddedildi!")
                
        except Exception as e:
            toast(f"Hata: {str(e)}")
        finally:
            self.ids.pay_btn.text = "KREDİ KARTI"
            self.ids.pay_btn.disabled = False

    def show_success_dialog(self):
        dialog = MDDialog(
            title="✅ İşlem Başarılı!",
            text="Ödeme başarıyla alındı ve sisteme işlendi.",
            buttons=[MDFlatButton(text="TAMAM", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

    def go_to_history(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'history'

    def logout(self):
        app = MDApp.get_running_app()
        app.user_token = None
        self.manager.transition.direction = 'right'
        self.manager.current = 'login'
        toast("Çıkış yapıldı.")


class HistoryScreen(MDScreen):
    def go_back(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'main'

    def load_history(self):
        self.ids.history_list.clear_widgets()
        app = MDApp.get_running_app()
        token = app.user_token
        
        if not token:
            return

        try:
            headers = {'Authorization': f'Bearer {token}'}
            # SSL Hatasını Yoksay (Eski Telefonlar İçin)
            response = requests.get(HISTORY_URL, headers=headers, timeout=10, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                transactions = data.get('transactions', [])
                
                if not transactions:
                    self.ids.history_list.add_widget(
                        MDLabel(text="Henüz işlem yok.", halign="center")
                    )
                    return

                for tx in reversed(transactions):
                    amt = tx.get('amount', 0)
                    status = tx.get('status', 'unknown')
                    date_str = tx.get('created_at', '')[:16].replace('T', ' ')
                    
                    icon = "check-circle" if status == "succeeded" else "close-circle"
                    color = (0, 0.7, 0, 1) if status == "succeeded" else (0.8, 0.2, 0.2, 1)
                    
                    item = TwoLineAvatarIconListItem(
                        text=f"{amt} TL",
                        secondary_text=f"{date_str} - {status}"
                    )
                    item.add_widget(IconLeftWidget(icon=icon, theme_text_color="Custom", text_color=color))
                    self.ids.history_list.add_widget(item)

        except Exception as e:
            toast("Geçmiş yüklenemedi.")

class TaksiPosApp(MDApp):
    user_token = None # Token'ı burada saklayacağız

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Amber"
        return Builder.load_string(KV)

if __name__ == '__main__':
    TaksiPosApp().run()
