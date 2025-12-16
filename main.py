import requests
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.list import MDList, TwoLineAvatarIconListItem, IconLeftWidget
from kivymd.toast import toast
from kivy.properties import StringProperty, NumericProperty

# API URL'leri
API_BASE_URL = "https://taksipos-api.onrender.com"
LOGIN_URL = f"{API_BASE_URL}/login"
PAYMENT_URL = f"{API_BASE_URL}/process-payment"
HISTORY_URL = f"{API_BASE_URL}/payment-history"

KV = """
MDScreenManager:
    MainScreen:
    HistoryScreen:

# === ANA EKRAN (POS CİHAZI TASARIMI) ===
<MainScreen>:
    name: 'main'
    md_bg_color: 0.1, 0.1, 0.1, 1  # Koyu Arka Plan

    MDBoxLayout:
        orientation: 'vertical'
        padding: "10dp"
        spacing: "10dp"

        # --- ÜST BİLGİ PANELİ ---
        MDCard:
            size_hint_y: None
            height: "80dp"
            md_bg_color: 0.2, 0.2, 0.2, 1
            radius: [10]
            padding: "10dp"
            
            MDIconButton:
                icon: "history"
                theme_text_color: "Custom"
                text_color: 1, 0.8, 0, 1  # Sarı Renk
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
                
                MDLabel:
                    text: "34 ROTA 01"
                    theme_text_color: "Custom"
                    text_color: 1, 0.8, 0, 1  # Sarı Plaka Rengi
                    font_style: "H6"

        # --- EKRAN (RAKAMLAR) ---
        MDCard:
            orientation: "vertical"
            size_hint_y: 0.35
            md_bg_color: 0, 0, 0, 1
            radius: [5]
            padding: "15dp"
            line_color: 1, 0.8, 0, 0.5  # Sarı Çerçeve
            
            MDLabel:
                text: "Tutar Giriniz (TL)"
                theme_text_color: "Custom"
                text_color: 0.5, 0.5, 0.5, 1
                font_style: "Caption"
            
            # GİRİLEN TUTAR
            MDLabel:
                text: root.display_amount + " ₺"
                halign: "right"
                font_style: "H3"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                bold: True

            MDBoxLayout:
                size_hint_y: None
                height: "1dp"
                md_bg_color: 0.3, 0.3, 0.3, 1

            # HESAPLAMALAR
            MDGridLayout:
                cols: 2
                size_hint_y: None
                height: "60dp"
                padding: [0, "10dp", 0, 0]
                
                MDLabel:
                    text: "+ Hizmet Bedeli (%13):"
                    theme_text_color: "Custom"
                    text_color: 0.7, 0.7, 0.7, 1
                    font_style: "Body2"
                
                MDLabel:
                    text: root.display_service_fee + " ₺"
                    halign: "right"
                    theme_text_color: "Custom"
                    text_color: 1, 0.8, 0, 1
                    font_style: "Body2"
                    
                MDLabel:
                    text: "GENEL TOPLAM:"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    bold: True
                    font_style: "Subtitle1"
                
                MDLabel:
                    text: root.display_total + " ₺"
                    halign: "right"
                    theme_text_color: "Custom"
                    text_color: 0, 1, 0, 1  # Yeşil Toplam
                    bold: True
                    font_style: "H5"

        # --- TUŞ TAKIMI (NUMPAD) ---
        MDGridLayout:
            cols: 3
            spacing: "10dp"
            size_hint_y: 0.5
            
            # Tuşlar (Fonksiyonel)
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
                pos_hint: {"center_x": .5, "center_y": .5}
                size_hint: 1, 1
                on_release: root.remove_digit()

            NumpadButton:
                text: "0"
                on_release: root.add_digit("0")

            # ÖDEME AL BUTONU (Yeşil)
            MDRaisedButton:
                id: pay_btn
                text: "KREDİ KARTI"
                md_bg_color: 1, 0.6, 0, 1 # Turuncu/Sarı Kart Rengi
                text_color: 0, 0, 0, 1
                size_hint: 1, 1
                bold: True
                font_size: "16sp"
                on_release: root.process_payment()

# Özel Tuş Tasarımı
<NumpadButton@MDFlatButton>:
    font_size: "24sp"
    size_hint: 1, 1
    theme_text_color: "Custom"
    text_color: 1, 1, 1, 1
    md_bg_color: 0.2, 0.2, 0.2, 1

# === GEÇMİŞ İŞLEMLER EKRANI ===
<HistoryScreen>:
    name: 'history'
    on_enter: root.load_history()
    md_bg_color: 0.95, 0.95, 0.95, 1

    MDBoxLayout:
        orientation: 'vertical'

        # Toolbar
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

class MainScreen(MDScreen):
    display_amount = StringProperty("0")
    display_service_fee = StringProperty("0.00")
    display_total = StringProperty("0.00")
    raw_amount_str = "" # Hesaplama için ham veri
    
    # Giriş Token'ı (Bunu daha sonra otomatik alabiliriz, şimdilik sabit veya login ile)
    token = None 

    def on_enter(self):
        # Uygulama açılınca otomatik giriş yapmayı dene (Demo amaçlı)
        self.login_silently()

    def login_silently(self):
        # Arka planda giriş yapıp token alır
        try:
            # Demo kullanıcı (Senin API'deki)
            resp = requests.post(LOGIN_URL, json={'username': 'admin', 'password': 'password123'}, timeout=5)
            if resp.status_code == 200:
                self.token = resp.json().get('access_token')
                toast("Sürücü Girişi Yapıldı 👍")
            else:
                toast("Giriş başarısız, interneti kontrol et.")
        except:
            pass

    def add_digit(self, digit):
        # 0 ise ve başta 0 varsa ekleme
        if self.raw_amount_str == "" and digit == "0":
            return
        
        # Maksimum karakter sınırı (ekran taşmasın)
        if len(self.raw_amount_str) > 6:
            return

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
        if not self.raw_amount_str or float(self.raw_amount_str) == 0:
            toast("Lütfen tutar giriniz!")
            return
        
        if not self.token:
            toast("Giriş yapılmamış! İnterneti kontrol edin.")
            self.login_silently()
            return

        # Toplam tutarı gönderiyoruz
        try:
            amount = float(self.raw_amount_str)
            # DİKKAT: API'ye ham tutarı mı yoksa komisyonluyu mu göndereceksin?
            # Buraya komisyonsuz tutarı yazıyorum, API hesaplıyorsa öyle kalsın.
            
            toast("Kart Okunuyor... ⏳")
            headers = {'Authorization': f'Bearer {self.token}'}
            
            # API İsteği
            response = requests.post(PAYMENT_URL, json={'amount': amount}, headers=headers, timeout=15)
            
            if response.status_code == 200:
                toast("✅ ÖDEME BAŞARILI!")
                self.raw_amount_str = ""
                self.calculate() # Ekranı sıfırla
            else:
                toast("❌ Hata: Kart Bakiyesi Yetersiz veya Red")
                
        except Exception as e:
            toast(f"Bağlantı Hatası: {str(e)}")

    def go_to_history(self):
        if not self.token:
            toast("Önce giriş yapmalısınız.")
            return
        self.manager.transition.direction = 'left'
        self.manager.current = 'history'

class HistoryScreen(MDScreen):
    def go_back(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'main'

    def load_history(self):
        self.ids.history_list.clear_widgets()
        
        main_screen = self.manager.get_screen('main')
        if not main_screen.token:
            return

        try:
            headers = {'Authorization': f'Bearer {main_screen.token}'}
            response = requests.get(HISTORY_URL, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                transactions = data.get('transactions', [])
                
                if not transactions:
                    self.ids.history_list.add_widget(
                        MDLabel(text="Henüz işlem yok.", halign="center", padding=[0, 50, 0, 0])
                    )
                    return

                for tx in reversed(transactions): # En yeniler üstte
                    amt = tx.get('amount', 0)
                    status = tx.get('status', 'unknown')
                    date_str = tx.get('created_at', '')[:16].replace('T', ' ')
                    
                    icon = "check-circle" if status == "succeeded" else "close-circle"
                    color = (0, 0.7, 0, 1) if status == "succeeded" else (0.8, 0.2, 0.2, 1)
                    
                    # Liste Elemanı
                    item = TwoLineAvatarIconListItem(
                        text=f"{amt} TL",
                        secondary_text=f"{date_str} - {status}"
                    )
                    # İkon
                    item.add_widget(IconLeftWidget(icon=icon, theme_text_color="Custom", text_color=color))
                    self.ids.history_list.add_widget(item)

        except Exception as e:
            toast(f"Geçmiş yüklenemedi: {str(e)}")

class TaksiPosApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark" # Komple Siyah Tema
        self.theme_cls.primary_palette = "Amber" # Sarı vurgular
        return Builder.load_string(KV)

if __name__ == '__main__':
    TaksiPosApp().run()
