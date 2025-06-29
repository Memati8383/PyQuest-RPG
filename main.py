import random
import sys
import time

# ANSI renk kodları
class Color:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BRIGHT = '\033[1m'
    RESET = '\033[0m'

# Sabitler
MAX_INVENTORY = 30
RUN_CHANCE = 0.33
GOLD_REWARD = (15, 45)

# Hile kontrol değişkenleri
HILELER_AKTIF = False
MANA_SINIRSIZ = False

# Düşman isimleri ve görevler - EXPANDED
ENEMY_NAMES = ["Ork", "Zombi", "Vampir", "Kurt Adam", "Ejderha", "Kara Büyücü", 
               "Goblin", "Trol", "Hayalet", "Dev Örümcek", "Minotor", "Su Canavarı", 
               "Lamia", "Grifon", "Kiklop", "Harpia", "Kemik Yürüyücü", "Gargoyle",
               "Kara Şövalye", "Kurt Sürüsü", "Yeraltı Yaratığı", "İblis", "Şeytan Köpeği",
               "Yara Bandı", "Taş Golem", "Ateş Elementali", "Buz Cadısı"]

# Boss isimleri - EXPANDED
BOSS_NAMES = ["Kral Ork", "Lich", "Kızıl Ejderha", "Karanlık Lordu", "Ölüm Meleği", 
              "Titan", "Kara Ejder", "Cehennem Lordu", "Buz Kraliçesi", "Ateş Tanrısı",
              "Kaos Şövalyesi", "Ebedi Canavar", "Gölge Avcısı", "Yılan Tanrı", "Korku Prensi"]

# Görevler - EXPANDED
QUESTS = [
    {"hedef": "canavar", "adet": 5, "odul_xp": 80, "odul_altin": 80, "tamamlandi": False, "zorluk": 1},
    {"hedef": "boss", "adet": 1, "odul_xp": 200, "odul_altin": 200, "tamamlandi": False, "zorluk": 3},
    {"hedef": "excalibur", "adet": 1, "odul_xp": 150, "odul_altin": 150, "tamamlandi": False, "zorluk": 2},
    {"hedef": "iksir", "adet": 3, "odul_xp": 60, "odul_altin": 60, "tamamlandi": False, "zorluk": 1},
    {"hedef": "buyu_ogren", "adet": 2, "odul_xp": 100, "odul_altin": 100, "tamamlandi": False, "zorluk": 2},
    {"hedef": "seviye_atla", "adet": 3, "odul_xp": 120, "odul_altin": 120, "tamamlandi": False, "zorluk": 2},
    # Yeni görevler
    {"hedef": "kalkanli_dusman", "adet": 3, "odul_xp": 90, "odul_altin": 90, "tamamlandi": False, "zorluk": 2},
    {"hedef": "buyucu_dusman", "adet": 4, "odul_xp": 110, "odul_altin": 110, "tamamlandi": False, "zorluk": 2},
    {"hedef": "altin_kazan", "adet": 500, "odul_xp": 150, "odul_altin": 200, "tamamlandi": False, "zorluk": 2},
    {"hedef": "dev_ork", "adet": 1, "odul_xp": 250, "odul_altin": 250, "tamamlandi": False, "zorluk": 3},
    {"hedef": "elemental", "adet": 2, "odul_xp": 180, "odul_altin": 180, "tamamlandi": False, "zorluk": 3},
    {"hedef": "golem", "adet": 2, "odul_xp": 170, "odul_altin": 170, "tamamlandi": False, "zorluk": 3},
    {"hedef": "kral_magara", "adet": 1, "odul_xp": 300, "odul_altin": 300, "tamamlandi": False, "zorluk": 4},
    {"hedef": "kutsal_kilic", "adet": 1, "odul_xp": 200, "odul_altin": 200, "tamamlandi": False, "zorluk": 3},
    {"hedef": "efsanevi_zirh", "adet": 1, "odul_xp": 180, "odul_altin": 180, "tamamlandi": False, "zorluk": 3},
    {"hedef": "buyu_kitabi", "adet": 1, "odul_xp": 220, "odul_altin": 220, "tamamlandi": False, "zorluk": 3}
]


def yavas_yaz(metin, renk=Color.WHITE, delay=0.002):
    print(renk, end='', flush=True)
    for harf in metin:
        print(harf, end="", flush=True)
        time.sleep(delay)
    print(Color.RESET, end='', flush=True)

# === TEMEL SINIFLAR ===

class Karakter:
    def __init__(self, isim, hp, seviye, saldiri, savunma):
        self.isim = isim
        self.hp = hp
        self.max_hp = hp
        self.seviye = seviye
        self.saldiri = saldiri
        self.savunma = savunma
        self.zehirli = False

    def hasar_al(self, miktar):
        zarar = max(0, miktar - self.savunma)
        self.hp -= zarar
        return zarar

    def hayatta_mi(self):
        return self.hp > 0

# === OYUNCU SINIFI ===

class Oyuncu(Karakter):
    def __init__(self, isim):
        super().__init__(isim, 100, 1, 10, 5)
        self.xp = 0
        self.altin = 50
        self.mana = 30
        self.max_mana = 30
        self.envanter = []
        self.silah = TemelSilah()
        self.kazandigi_esyalar = []
        self.tamamlanan_gorevler = []
        self.gorev = self.rastgele_tamamlanmamis_gorev()
        self.oldurulen_canavarlar = 0
        self.oldurulen_bosslar = 0
        self.ogrenilen_buyuler = 1  # Başlangıçta 1 büyü biliniyor
        self.gorev = self.rastgele_tamamlanmamis_gorev()
        
        # Yeni görev istatistikleri
        self.oldurulen_kalkanli = 0
        self.oldurulen_buyucu = 0
        self.oldurulen_dev_ork = 0
        self.oldurulen_elemental = 0
        self.oldurulen_golem = 0

    def gorev_metni_olustur(self):
        g = self.gorev
        if g["hedef"] == "canavar":
            return f"{g['adet']} canavar öldür ({self.oldurulen_canavarlar}/{g['adet']})"
        elif g["hedef"] == "boss":
            return f"{g['adet']} boss öldür ({self.oldurulen_bosslar}/{g['adet']})"
        elif g["hedef"] == "excalibur":
            durum = "✅" if "excalibur" in self.kazandigi_esyalar else "❌"
            return f"Excalibur kılıcını bul {durum}"
        elif g["hedef"] == "iksir":
            adet = sum(1 for esya in self.envanter if esya.isim in ["İksir", "Süper İksir"])
            return f"{g['adet']} iksir topla ({adet}/{g['adet']})"
        elif g["hedef"] == "buyu_ogren":
            return f"{g['adet']} yeni büyü öğren ({self.ogrenilen_buyuler-1}/{g['adet']})"
        elif g["hedef"] == "seviye_atla":
            return f"{g['adet']} seviye atla (Şu an: {self.seviye})"
        # Yeni görev metinleri
        elif g["hedef"] == "kalkanli_dusman":
            return f"{g['adet']} kalkanlı düşman öldür ({self.oldurulen_kalkanli}/{g['adet']})"
        elif g["hedef"] == "buyucu_dusman":
            return f"{g['adet']} büyücü düşman öldür ({self.oldurulen_buyucu}/{g['adet']})"
        elif g["hedef"] == "altin_kazan":
            return f"{g['adet']} altın kazan ({self.altin}/{g['adet']})"
        elif g["hedef"] == "dev_ork":
            return f"{g['adet']} Dev Ork öldür ({self.oldurulen_dev_ork}/{g['adet']})"
        elif g["hedef"] == "elemental":
            return f"{g['adet']} Elemental öldür ({self.oldurulen_elemental}/{g['adet']})"
        elif g["hedef"] == "golem":
            return f"{g['adet']} Golem öldür ({self.oldurulen_golem}/{g['adet']})"
        elif g["hedef"] == "kral_magara":
            durum = "✅" if "kral_magara" in self.kazandigi_esyalar else "❌"
            return f"Mağara Kralını yen {durum}"
        elif g["hedef"] == "kutsal_kilic":
            durum = "✅" if "kutsal_kilic" in self.kazandigi_esyalar else "❌"
            return f"Kutsal Kılıcı bul {durum}"
        elif g["hedef"] == "efsanevi_zirh":
            durum = "✅" if "efsanevi_zirh" in self.kazandigi_esyalar else "❌"
            return f"Efsanevi Zırhı bul {durum}"
        elif g["hedef"] == "buyu_kitabi":
            durum = "✅" if "buyu_kitabi" in self.kazandigi_esyalar else "❌"
            return f"Kayıp Büyü Kitabını bul {durum}"
        return "Bilinmeyen görev"

    def gorev_durumunu_kontrol_et(self):
        g = self.gorev
        if g["tamamlandi"]:
            return
            
        tamamlandi = False
        if g["hedef"] == "canavar":
            tamamlandi = self.oldurulen_canavarlar >= g["adet"]
        elif g["hedef"] == "boss":
            tamamlandi = self.oldurulen_bosslar >= g["adet"]
        elif g["hedef"] == "excalibur":
            tamamlandi = "excalibur" in self.kazandigi_esyalar
        elif g["hedef"] == "iksir":
            adet = sum(1 for esya in self.envanter if esya.isim in ["İksir", "Süper İksir"])
            tamamlandi = adet >= g["adet"]
        elif g["hedef"] == "buyu_ogren":
            tamamlandi = self.ogrenilen_buyuler-1 >= g["adet"]
        elif g["hedef"] == "seviye_atla":
            tamamlandi = self.seviye >= g["adet"] + 1  # Başlangıç seviyesi 1 olduğu için
        # Yeni görev kontrolleri
        elif g["hedef"] == "kalkanli_dusman":
            tamamlandi = self.oldurulen_kalkanli >= g["adet"]
        elif g["hedef"] == "buyucu_dusman":
            tamamlandi = self.oldurulen_buyucu >= g["adet"]
        elif g["hedef"] == "altin_kazan":
            tamamlandi = self.altin >= g["adet"]
        elif g["hedef"] == "dev_ork":
            tamamlandi = self.oldurulen_dev_ork >= g["adet"]
        elif g["hedef"] == "elemental":
            tamamlandi = self.oldurulen_elemental >= g["adet"]
        elif g["hedef"] == "golem":
            tamamlandi = self.oldurulen_golem >= g["adet"]
        elif g["hedef"] == "kral_magara":
            tamamlandi = "kral_magara" in self.kazandigi_esyalar
        elif g["hedef"] == "kutsal_kilic":
            tamamlandi = "kutsal_kilic" in self.kazandigi_esyalar
        elif g["hedef"] == "efsanevi_zirh":
            tamamlandi = "efsanevi_zirh" in self.kazandigi_esyalar
        elif g["hedef"] == "buyu_kitabi":
            tamamlandi = "buyu_kitabi" in self.kazandigi_esyalar
            
        if tamamlandi:
            self.gorev_tamamla()
            
    def rastgele_tamamlanmamis_gorev(self):
        # Tamamlanmamış görevler arasından seçim yap
        aktif_gorevler = [g for g in QUESTS if not g["tamamlandi"]]
        if not aktif_gorevler:
            # Tüm görevler tamamlandıysa yenilerini oluştur
            for g in QUESTS:
                g["tamamlandi"] = False
            aktif_gorevler = QUESTS.copy()
        return random.choice(aktif_gorevler)

    def saldir(self):
        return self.saldiri + self.silah.saldiri

    def deneyim_ekle(self, miktar):
        self.xp += miktar
        seviye_gereken_xp = self.seviye * 50
        if self.xp >= seviye_gereken_xp:
            self.xp -= seviye_gereken_xp
            self.seviye += 1
            self.max_hp += 10
            self.hp = self.max_hp
            self.max_mana += 10
            self.mana = self.max_mana
            self.saldiri += 2
            self.savunma += 1
            yavas_yaz(f"\n🔺 Seviye atladınız! Yeni seviye: {self.seviye}", Color.MAGENTA)

    def envantere_ekle(self, esya):
        if len(self.envanter) < MAX_INVENTORY:
            self.envanter.append(esya)
            esya_adi = esya.isim.lower()
            self.kazandigi_esyalar.append(esya_adi)
            yavas_yaz(f"📦 {esya.isim} envantere eklendi.", Color.CYAN)
            
            # Özel eşyalar eklendiyse görevi kontrol et
            if esya_adi in ["excalibur", "kutsal kılıç", "efsanevi zırh", "kayıp büyü kitabı"]:
                self.gorev_durumunu_kontrol_et()
        else:
            yavas_yaz("⚠️ Envanter dolu!", Color.YELLOW)

    def envanteri_goster(self):
        if not self.envanter:
            yavas_yaz("Envanter boş.", Color.YELLOW)
            return None
        for i, esya in enumerate(self.envanter):
            print(f"{i + 1}. {esya.isim}")
        secim = input(Color.CYAN + "Kullanmak istediğiniz eşya numarası (iptal için boş bırak): " + Color.RESET)
        if secim.isdigit():
            index = int(secim) - 1
            if 0 <= index < len(self.envanter):
                esya = self.envanter.pop(index)
                esya.kullan(self)

    def gorev_tamamla(self):
        g = self.gorev
        g["tamamlandi"] = True
        self.tamamlanan_gorevler.append(g.copy())
        
        yavas_yaz(f"\n🎉 Görev tamamlandı: {g['hedef']}!", Color.GREEN)
        yavas_yaz(f"🎁 Ödüller: {g['odul_xp']} XP, {g['odul_altin']} Altın", Color.YELLOW)
        
        self.xp += g["odul_xp"]
        self.altin += g["odul_altin"]
        self.oldurulen_canavarlar = 0
        
        # Yeni görev seç
        self.gorev = self.rastgele_tamamlanmamis_gorev()
        yavas_yaz(f"📜 Yeni görev: {self.gorev_metni_olustur()}", Color.CYAN)

# === SİLAH SINIFLARI ===

class TemelSilah:
    def __init__(self):
        self.saldiri = 0
        self.isim = "Yumruk"

class Hancer(TemelSilah):
    def __init__(self):
        super().__init__()
        self.saldiri = 3
        self.isim = "Hançer"

class KisaKilic(TemelSilah):
    def __init__(self):
        super().__init__()
        self.saldiri = 5
        self.isim = "Kısa Kılıç"

class UzunKilic(TemelSilah):
    def __init__(self):
        super().__init__()
        self.saldiri = 8
        self.isim = "Uzun Kılıç"

class Excalibur(TemelSilah):
    def __init__(self):
        super().__init__()
        self.saldiri = 15
        self.isim = "Excalibur"

# Yeni silahlar
class KutsalKilic(TemelSilah):
    def __init__(self):
        super().__init__()
        self.saldiri = 18
        self.isim = "Kutsal Kılıç"

class EjderhaKilic(TemelSilah):
    def __init__(self):
        super().__init__()
        self.saldiri = 22
        self.isim = "Ejderha Kılıcı"

# === EŞYA SINIFLARI ===

class Esya:
    def __init__(self, isim):
        self.isim = isim

    def kullan(self, oyuncu):
        pass

class Iksir(Esya):
    def __init__(self):
        super().__init__("İksir")

    def kullan(self, oyuncu):
        oyuncu.hp = min(oyuncu.max_hp, oyuncu.hp + 20)
        yavas_yaz("❤️ Can 20 puan yenilendi.", Color.RED)

class SuperIksir(Esya):
    def __init__(self):
        super().__init__("Süper İksir")

    def kullan(self, oyuncu):
        oyuncu.hp = min(oyuncu.max_hp, oyuncu.hp + 50)
        yavas_yaz("❤️ Can 50 puan yenilendi.", Color.RED)

class ManaIksiri(Esya):
    def __init__(self):
        super().__init__("Mana İksiri")

    def kullan(self, oyuncu):
        oyuncu.mana = min(oyuncu.max_mana, oyuncu.mana + 20)
        yavas_yaz("🔷 Mana 20 puan yenilendi.", Color.BLUE)

# Yeni eşyalar
class EfsaneviZirh(Esya):
    def __init__(self):
        super().__init__("Efsanevi Zırh")
        
    def kullan(self, oyuncu):
        oyuncu.savunma += 10
        yavas_yaz("🛡️ Savunmanız +10 arttı! (Kalıcı)", Color.BLUE)

class BuyuKitabi(Esya):
    def __init__(self):
        super().__init__("Kayıp Büyü Kitabı")
        
    def kullan(self, oyuncu):
        oyuncu.ogrenilen_buyuler += 2
        yavas_yaz("📖 2 yeni büyü öğrendiniz!", Color.MAGENTA)
        oyuncu.gorev_durumunu_kontrol_et()

class KralMagaraTaci(Esya):
    def __init__(self):
        super().__init__("Mağara Kralı Tacı")
        
    def kullan(self, oyuncu):
        oyuncu.max_hp += 50
        oyuncu.hp += 50
        yavas_yaz("👑 Maksimum canınız +50 arttı!", Color.RED)

# === BÜYÜLER ===

class Buyu:
    def __init__(self, isim, mana_maliyeti, etkisi, aciklama, seviye_gereksinimi=1):
        self.isim = isim
        self.mana_maliyeti = mana_maliyeti
        self.etkisi = etkisi
        self.aciklama = aciklama
        self.seviye_gereksinimi = seviye_gereksinimi

BUYULER = [
    Buyu("Ateş Topu", 10, lambda o, d: d.hasar_al(25), 
         "Düşmana 25 hasar verir", 1),
    Buyu("Buz Mızrağı", 15, lambda o, d: d.hasar_al(35), 
         "Düşmana 35 hasar verir ve bir tur donmasını sağlar", 2),
    Buyu("Yıldırım Çarpması", 20, lambda o, d: d.hasar_al(50), 
         "Düşmana 50 hasar verir", 3),
    Buyu("Kendini İyileştir", 15, lambda o, d: setattr(o, 'hp', min(o.max_hp, o.hp + 30)), 
         "30 can iyileştirir", 1),
    Buyu("Kalkan", 20, lambda o, d: setattr(o, 'savunma', o.savunma + 5), 
         "3 tur boyunca savunmayı +5 artırır", 2),
    Buyu("Zehir Bulutu", 25, lambda o, d: (d.hasar_al(20), setattr(d, 'zehirli', True)), 
         "20 hasar verir ve düşmanı zehirler", 3),
    Buyu("Hayat Çalma", 30, lambda o, d: (d.hasar_al(40), setattr(o, 'hp', min(o.max_hp, o.hp + 20))), 
         "40 hasar verir ve 20 can çalar", 4),
    Buyu("Meteor Yağmuru", 50, lambda o, d: d.hasar_al(100), 
         "100 hasar verir (Sadece bosslara karşı)", 5),
    # Yeni büyüler
    Buyu("Kutsal Kalkan", 40, lambda o, d: (setattr(o, 'savunma', o.savunma + 10), setattr(o, 'hp', min(o.max_hp, o.hp + 25))), 
         "Savunma +10 ve 25 can iyileştirir", 4),
    Buyu("Zaman Donması", 60, lambda o, d: setattr(d, 'donmus', 2), 
         "Düşmanı 2 tur donuk bırakır", 5),
    Buyu("Kutsal Işın", 45, lambda o, d: d.hasar_al(75), 
         "75 hasar verir (Özellikle karanlık yaratıklara etkili)", 4)
]

def buyu_kullan(oyuncu, dusman):
    print(Color.CYAN + Color.BRIGHT + "\n📜-- Büyü Defteri --" + Color.RESET)
    for i, b in enumerate(BUYULER):
        if oyuncu.seviye >= b.seviye_gereksinimi:
            print(Color.YELLOW + f"{i+1}. {b.isim} (Mana: {b.mana_maliyeti}) - " + 
                  Color.WHITE + f"{b.aciklama}")
    
    secim = input(Color.CYAN + "\nBüyü numarası (iptal için boş bırak): " + Color.RESET)
    if secim.isdigit():
        index = int(secim) - 1
        if 0 <= index < len(BUYULER):
            b = BUYULER[index]
            
            if oyuncu.seviye < b.seviye_gereksinimi:
                yavas_yaz("Bu büyüyü kullanmak için yeterli seviyede değilsiniz!", Color.RED)
                return
                
            if oyuncu.mana >= b.mana_maliyeti or MANA_SINIRSIZ:
                oyuncu.mana -= b.mana_maliyeti
                b.etkisi(oyuncu, dusman)
                
                if b.isim == "Kalkan":
                    yavas_yaz(f"🛡️ Savunmanız 3 tur boyunca +5 arttı!", Color.BLUE)
                elif b.isim == "Zehir Bulutu":
                    yavas_yaz(f"☠️ {dusman.isim} zehirlendi!", Color.GREEN)
                elif b.isim == "Hayat Çalma":
                    yavas_yaz(f"💔 {dusman.isim}'den 20 can çaldınız!", Color.RED)
                elif b.isim == "Kutsal Kalkan":
                    yavas_yaz(f"✨ Savunmanız +10 arttı ve 25 can iyileştirdiniz!", Color.MAGENTA)
                elif b.isim == "Zaman Donması":
                    yavas_yaz(f"⏳ {dusman.isim} 2 tur boyunca dondu!", Color.BLUE)
                else:
                    yavas_yaz(f"✨ {b.isim} büyüsü uygulandı!", Color.MAGENTA)
            else:
                yavas_yaz("Yeterli mana yok!", Color.RED)
        else:
            yavas_yaz("Geçersiz büyü numarası!", Color.RED)

# === GELİŞMİŞ DÜŞMAN SINIFLARI ===

class Düsman(Karakter):
    def __init__(self, boss=False):
        if boss:
            isim = random.choice(BOSS_NAMES)
            seviye = random.randint(5, 10)
            hp = 180 + seviye * 35
            saldiri = 20 + seviye * 4
            savunma = 12 + seviye
        else:
            isim = random.choice(ENEMY_NAMES)
            seviye = random.randint(1, 7)
            hp = 60 + seviye * 25
            saldiri = 10 + seviye * 3
            savunma = 7 + seviye

        super().__init__(isim, hp, seviye, saldiri, savunma)
        self.tur = random.choice(["normal", "iyilesen", "zehirli", "buyucu", "kalkanli"])
        self.boss = boss
        self.donmus = 0
        
        # Özel düşman türleri
        if "Dev" in isim:
            self.tur = "dev"
            self.hp += 50
            self.saldiri += 5
        elif "Elemental" in isim:
            self.tur = "elemental"
            self.hp += 30
            self.saldiri += 8
        elif "Golem" in isim:
            self.tur = "golem"
            self.hp += 80
            self.savunma += 10
            self.saldiri -= 3
        
    def davran(self, oyuncu):
        # Donma kontrolü
        if self.donmus > 0:
            self.donmus -= 1
            yavas_yaz(f"❄️ {self.isim} donmuş ve saldıramıyor!", Color.BLUE)
            return
            
        # Özel yetenekler
        if self.tur == "dev" and random.random() < 0.4:
            zarar = self.saldiri * 1.5
            oyuncu.hp -= zarar
            yavas_yaz(f"💥 {self.isim} size {int(zarar)} hasarlı dev saldırısı yaptı!", Color.RED)
            return
        elif self.tur == "elemental":
            if "Ateş" in self.isim:
                if random.random() < 0.5:
                    oyuncu.hp -= 25
                    yavas_yaz(f"🔥 {self.isim} size 25 hasarlı ateş saldırısı yaptı!", Color.RED)
                    return
            elif "Buz" in self.isim:
                if random.random() < 0.4:
                    oyuncu.zehirli = True
                    yavas_yaz(f"❄️ {self.isim} sizi dondu! Savunma düştü.", Color.BLUE)
                    oyuncu.savunma = max(0, oyuncu.savunma - 3)
                    return
                    
        if self.tur == "iyilesen" and self.hp < self.max_hp // 2 and random.random() < 0.3:
            iyilesme = random.randint(15, 30)
            self.hp = min(self.max_hp, self.hp + iyilesme)
            yavas_yaz(f"{self.isim} kendini {iyilesme} can iyileştirdi!", Color.GREEN)
            return
        elif self.tur == "zehirli" and random.random() < 0.3:
            oyuncu.zehirli = True
            yavas_yaz(f"☠️ {self.isim} sizi zehirledi!", Color.GREEN)
        elif self.tur == "buyucu" and random.random() < 0.4:
            zarar = random.randint(15, 30)
            oyuncu.hp -= zarar
            yavas_yaz(f"🔮 {self.isim} size {zarar} hasarlı büyü saldırısı yaptı!", Color.MAGENTA)
            return
        elif self.tur == "kalkanli" and random.random() < 0.2:
            self.savunma += 3
            yavas_yaz(f"🛡️ {self.isim} savunmasını güçlendirdi!", Color.BLUE)
            
        zarar = oyuncu.hasar_al(self.saldiri)
        yavas_yaz(f"⚔️ {self.isim} size {zarar} hasar verdi!", Color.RED)


# === MAĞAZA SİSTEMİ ===

def magaza(oyuncu):
    print(Color.CYAN + "\n🛒 -- Mağaza -- (Altın: 💰" + Color.YELLOW + f" {oyuncu.altin} " + Color.CYAN + ")" + Color.RESET)
    urunler = [
        ("İksir", 20, Iksir()),
        ("Süper İksir", 40, SuperIksir()),
        ("Mana İksiri", 25, ManaIksiri()),
        ("Kısa Kılıç", 35, KisaKilic()),
        ("Uzun Kılıç", 60, UzunKilic()),
        ("Excalibur", 120, Excalibur()),
        # Yeni ürünler
        ("Kutsal Kılıç", 150, KutsalKilic()),
        ("Ejderha Kılıcı", 200, EjderhaKilic()),
        ("Efsanevi Zırh", 180, EfsaneviZirh()),
        ("Kayıp Büyü Kitabı", 220, BuyuKitabi()),
    ]
    for i, (isim, fiyat, _) in enumerate(urunler):
        print(f"{i+1}. {isim} - {fiyat} altın")
    secim = input(Color.CYAN + "Satın almak istediğiniz ürün numarası (iptal için boş bırak): " + Color.RESET)
    if secim.isdigit():
        index = int(secim) - 1
        if 0 <= index < len(urunler):
            isim, fiyat, nesne = urunler[index]
            if oyuncu.altin >= fiyat:
                oyuncu.altin -= fiyat
                if isinstance(nesne, TemelSilah) and nesne.saldiri > oyuncu.silah.saldiri:
                    oyuncu.silah = nesne
                    yavas_yaz(f"{isim} kuşanıldı!")
                    
                    # Özel silahlar alındıysa görevi kontrol et
                    if nesne.isim.lower() in ["excalibur", "kutsal kılıç"]:
                        oyuncu.gorev_durumunu_kontrol_et()
                else:
                    oyuncu.envantere_ekle(nesne)
            else:
                yavas_yaz("Yetersiz altın.", Color.RED)
                
# === SAVAŞ SİSTEMİ ===

def savas(oyuncu, boss=False):
    dusman = Düsman(boss)
    
    if boss:
        yavas_yaz(f"\n💀 {Color.RED}{Color.BRIGHT}BOSS SAVAŞI: {dusman.isim} {Color.RESET}" +
                 f"{Color.WHITE}(Seviye {dusman.seviye}, HP: {dusman.hp})", Color.RED)
    else:
        yavas_yaz(f"\n⚔️ {Color.RED}{dusman.isim} {Color.WHITE}(Seviye {dusman.seviye}, Tür: {dusman.tur}) ile karşılaştınız!", Color.MAGENTA)

    while oyuncu.hp > 0 and dusman.hp > 0:
        print(Color.CYAN + f"\n🎖️ {oyuncu.isim} | HP: {oyuncu.hp}/{oyuncu.max_hp} | Mana: {oyuncu.mana}/{oyuncu.max_mana}" + Color.RESET)
        print(Color.RED + f"💀 {dusman.isim} | HP: {dusman.hp}/{dusman.max_hp}" + Color.RESET)
        print("\n1. Saldır")
        print("2. Kaç")
        print("3. Eşya Kullan")
        print("4. Büyü Kullan")

        secim = input(Color.CYAN + "Seçiminiz: " + Color.RESET)
        if secim == "1":
            hasar = dusman.hasar_al(oyuncu.saldir())
            yavas_yaz(f"{dusman.isim}'e {hasar} hasar verdiniz.", Color.RED)
        elif secim == "2":
            if random.random() < RUN_CHANCE:
                yavas_yaz("🏃 Başarıyla kaçtınız!", Color.GREEN)
                return
            else:
                yavas_yaz("Kaçamadınız!", Color.YELLOW)
                # Düşmanın saldırması için döngünün devam etmesi gerekir
                # Buraya continue eklemiyoruz ki düşman saldırısı gerçekleşsin
        elif secim == "3":
            oyuncu.envanteri_goster()
            # Eşya kullanıldıktan sonra düşmanın saldırması için döngü devam etmeli
        elif secim == "4":
            buyu_kullan(oyuncu, dusman)
        else:
            yavas_yaz("Geçersiz seçim.")
            continue

        # Düşmanın özel yetenekleri (sadece kaçma girişimi başarısız olduğunda veya diğer seçimlerde)
        if dusman.hp > 0:  # Düşman hala hayattaysa
            # Donma kontrolü
            if dusman.donmus > 0:
                dusman.donmus -= 1
                yavas_yaz(f"❄️ {dusman.isim} donmuş ve saldıramıyor!", Color.BLUE)
            else:
                if dusman.hp <= dusman.max_hp // 4 and not dusman.boss:
                    yavas_yaz(f"⚠️ {dusman.isim} çaresiz durumda ve daha agresif saldırıyor!", Color.RED)
                    dusman.saldiri += 3
                    
                if dusman.boss and dusman.hp <= dusman.max_hp // 2:
                    yavas_yaz(f"💢 {dusman.isim} öfkelendi! Saldırı gücü arttı!", Color.RED)
                    dusman.saldiri += 5
                    
                dusman.davran(oyuncu)

        if oyuncu.zehirli:
            oyuncu.hp -= 3
            yavas_yaz("☠️ Zehir etkisi! -3 HP")

    if oyuncu.hp <= 0:
        yavas_yaz("\n💀 Öldünüz. Oyun bitti.", Color.RED)
        sys.exit()

    # İstatistik güncelleme
    if dusman.boss:
        oyuncu.oldurulen_bosslar += 1
    else:
        oyuncu.oldurulen_canavarlar += 1
        
    # Özel düşman istatistikleri
    if "Dev" in dusman.isim:
        oyuncu.oldurulen_dev_ork += 1
    elif "Elemental" in dusman.isim:
        oyuncu.oldurulen_elemental += 1
    elif "Golem" in dusman.isim:
        oyuncu.oldurulen_golem += 1
    elif dusman.tur == "kalkanli":
        oyuncu.oldurulen_kalkanli += 1
    elif dusman.tur == "buyucu":
        oyuncu.oldurulen_buyucu += 1

    yavas_yaz(f"\n🎉 {dusman.isim} yok edildi! Tecrübe ve altın kazandınız.", Color.GREEN)
    
    # Boss öldürme istatistiği
    if dusman.boss:
        yavas_yaz(f"\n🎉 {Color.YELLOW}BOSS YENDİNİZ! {Color.RESET}" + 
                 f"{Color.GREEN}Büyük ödüller kazandınız!", Color.YELLOW)
        oyuncu.deneyim_ekle(120)
        kazanc = random.randint(150, 300)
    else:
        oyuncu.deneyim_ekle(30)
        kazanc = random.randint(*GOLD_REWARD)
        
    oyuncu.altin += kazanc
    yavas_yaz(f"💰 {kazanc} altın kazandınız.", Color.YELLOW)
   
    # Nadir eşya şansı
    nadir_esya_sansi = 0.4 if boss else 0.15
    if random.random() < nadir_esya_sansi:
        nadir_esyalar = [Excalibur(), Iksir(), SuperIksir(), KutsalKilic(), EfsaneviZirh(), BuyuKitabi()]
        # Boss özel ödülleri
        if boss:
            nadir_esyalar.append(KralMagaraTaci())
            nadir_esyalar.append(EjderhaKilic())
            
        yeni_esya = random.choice(nadir_esyalar)
        oyuncu.envantere_ekle(yeni_esya)
        yavas_yaz(f"✨ {Color.MAGENTA}NADİR EŞYA BULDUNUZ: {yeni_esya.isim}{Color.RESET}", Color.MAGENTA)
        
        # Mağara Kralı tacı alındıysa görevi tamamla
        if yeni_esya.isim == "Mağara Kralı Tacı":
            oyuncu.kazandigi_esyalar.append("kral_magara")
            oyuncu.gorev_durumunu_kontrol_et()

    oyuncu.gorev_durumunu_kontrol_et()

def hile_menusu(oyuncu):
    global MANA_SINIRSIZ, HILELER_AKTIF
    while True:
        print(Color.CYAN + Color.BRIGHT + "\n💻 Hile Menüsü" + Color.RESET)
        print(Color.YELLOW + "1. Canı Tam Doldur" + Color.RESET)
        print(Color.YELLOW + "2. Mana'yı Tam Doldur" + Color.RESET)
        print(Color.YELLOW + "3. Altın Ekle (Miktar Seç)" + Color.RESET)
        print(Color.YELLOW + "4. Seviye Atlama (Miktar Seç)" + Color.RESET)
        print(Color.YELLOW + "5. Excalibur Ver" + Color.RESET)
        print(Color.YELLOW + "6. Mana Sınırsız Modu Aç/Kapa" + Color.RESET)
        print(Color.YELLOW + "7. Envanteri Temizle" + Color.RESET)
        print(Color.YELLOW + "8. Negatif Durumları Temizle" + Color.RESET)
        print(Color.YELLOW + "9. Çıkış" + Color.RESET)
        secim = input(Color.CYAN + "Seçiminiz: " + Color.RESET)

        if secim == "1":
            oyuncu.hp = oyuncu.max_hp
            yavas_yaz("Canınız tam olarak dolduruldu.", Color.GREEN)
        elif secim == "2":
            oyuncu.mana = oyuncu.max_mana
            yavas_yaz("Mananız tam olarak dolduruldu.", Color.BLUE)
        elif secim == "3":
            miktar = input("Eklenecek altın miktarı: ")
            if miktar.isdigit():
                oyuncu.altin += int(miktar)
                yavas_yaz(f"Altın {miktar} adet eklendi.", Color.GREEN)
            else:
                yavas_yaz("Geçersiz miktar.", Color.RED)
        elif secim == "4":
            miktar = input("Eklenecek seviye sayısı: ")
            if miktar.isdigit():
                for _ in range(int(miktar)):
                    oyuncu.deneyim_ekle(oyuncu.seviye * 50)
                yavas_yaz(f"{miktar} seviye atlandı.", Color.MAGENTA)
            else:
                yavas_yaz("Geçersiz sayı.", Color.RED)
        elif secim == "5":
            oyuncu.silah = Excalibur()
            oyuncu.kazandigi_esyalar.append("excalibur")
            yavas_yaz("Excalibur size verildi!", Color.CYAN)
            oyuncu.gorev_durumunu_kontrol_et()  # Görevi kontrol et
        elif secim == "6":
            MANA_SINIRSIZ = not MANA_SINIRSIZ
            durum = "açıldı" if MANA_SINIRSIZ else "kapatıldı"
            yavas_yaz(f"Mana sınırsız modu {durum}.", Color.CYAN)
        elif secim == "7":
            oyuncu.envanter.clear()
            yavas_yaz("Envanter temizlendi.", Color.YELLOW)
        elif secim == "8":
            oyuncu.zehirli = False
            yavas_yaz("Tüm negatif durumlar temizlendi.", Color.GREEN)
        elif secim == "9":
            break
        else:
            yavas_yaz("Geçersiz giriş.", Color.RED)

# === ANA OYUN DÖNGÜSÜ ===

def oyun():
    global HILELER_AKTIF, MANA_SINIRSIZ
    
    print(Color.MAGENTA + Color.BRIGHT + "=== 🧝‍♂️ METİN TABANLI RPG OYUNU ===" + Color.RESET)
    isim = input(Color.CYAN + "Karakter adınızı girin: " + Color.RESET)
    oyuncu = Oyuncu(isim)
    yavas_yaz(Color.CYAN + Color.BRIGHT + f"Hoş geldin, {oyuncu.isim}!" + Color.RESET)
    yavas_yaz(f"📜 Aktif görev: {oyuncu.gorev_metni_olustur()}", Color.CYAN)

    while True:
        print(Color.CYAN + Color.BRIGHT + "\n🔹 Menü 🔹" + Color.RESET)
        print(Color.YELLOW + "1. Savaşa Gir" + Color.RESET)
        print(Color.YELLOW + "2. Envanteri Görüntüle" + Color.RESET)
        print(Color.YELLOW + "3. Mağazaya Git" + Color.RESET)
        print(Color.YELLOW + "4. Görev Durumu" + Color.RESET)
        print(Color.YELLOW + "5. Çıkış" + Color.RESET)
        
        # Hile durumuna göre menü seçenekleri
        if HILELER_AKTIF:
            print(Color.RED + "6. Hile Menüsü" + Color.RESET)
            print(Color.YELLOW + f"7. Hile Modu: {'AÇIK ✅' if HILELER_AKTIF else 'KAPALI ❌'}" + Color.RESET)
        else:
            print(Color.YELLOW + f"6. Hile Modu: {'AÇIK ✅' if HILELER_AKTIF else 'KAPALI ❌'}" + Color.RESET)

        secim = input("Seçiminiz: ")
        if secim == "1":
            # Normal savaş veya boss savaşı şansı
            boss_sansi = 0.1 + (oyuncu.seviye * 0.02)
            if random.random() < boss_sansi and oyuncu.seviye >= 3:
                savas(oyuncu, boss=True)
            else:
                savas(oyuncu)
        elif secim == "2":
            oyuncu.envanteri_goster()
        elif secim == "3":
            magaza(oyuncu)
        elif secim == "4":
            print(Color.GREEN + f"\n📜 Aktif Görev: {oyuncu.gorev_metni_olustur()}")
            
            # Tamamlanan görevleri göster
            if oyuncu.tamamlanan_gorevler:
                print(Color.MAGENTA + "\n🏆 Tamamlanan Görevler:")
                for i, gorev in enumerate(oyuncu.tamamlanan_gorevler):
                    print(f"{i+1}. {gorev['hedef']} - {gorev['odul_xp']} XP, {gorev['odul_altin']} Altın")
        elif secim == "5":
            yavas_yaz("Çıkılıyor... Görüşmek üzere!", Color.CYAN)
            break
        elif secim == "6" and HILELER_AKTIF:
            hile_menusu(oyuncu)
        elif secim == "6" or secim == "7":
            HILELER_AKTIF = not HILELER_AKTIF
            durum = "açıldı" if HILELER_AKTIF else "kapatıldı"
            MANA_SINIRSIZ = False  # Hile modu kapatılınca mana sınırsız da kapat
            yavas_yaz(f"Hile modu {durum}.", Color.CYAN)
        else:
            yavas_yaz("Geçersiz giriş.", Color.RED)

# === OYUNU BAŞLAT ===
if __name__ == "__main__":
    oyun()
