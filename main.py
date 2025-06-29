import random
import sys
import time
from colorama import init, Fore, Style

# Renkleri başlat
init(autoreset=True)

CHEATS = True

# Sabitler
MAX_INVENTORY = 30
RUN_CHANCE = 0.33
GOLD_REWARD = (15, 45)
mana_sinirsiz = False

# Düşman isimleri ve görevler
ENEMY_NAMES = ["Ork", "Zombi", "Vampir", "Kurt Adam", "Ejderha", "Kara Büyücü", "Goblin", "Trol", "Hayalet"]
BOSS_NAMES = ["Kral Ork", "Lich", "Kızıl Ejderha", "Karanlık Lordu"]

QUESTS = [
    {"hedef": "canavar", "adet": 5, "odul_xp": 80, "odul_altin": 80, "tamamlandi": False, "zorluk": 1},
    {"hedef": "boss", "adet": 1, "odul_xp": 200, "odul_altin": 200, "tamamlandi": False, "zorluk": 3},
    {"hedef": "excalibur", "adet": 1, "odul_xp": 150, "odul_altin": 150, "tamamlandi": False, "zorluk": 2},
    {"hedef": "iksir", "adet": 3, "odul_xp": 60, "odul_altin": 60, "tamamlandi": False, "zorluk": 1},
    {"hedef": "buyu_ogren", "adet": 2, "odul_xp": 100, "odul_altin": 100, "tamamlandi": False, "zorluk": 2},
    {"hedef": "seviye_atla", "adet": 3, "odul_xp": 120, "odul_altin": 120, "tamamlandi": False, "zorluk": 2}
]


def yavas_yaz(metin, renk=Fore.WHITE, delay=0.002):
    for harf in renk + metin:
        print(harf, end="", flush=True)
        time.sleep(delay)
    print(Style.RESET_ALL)

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
            yavas_yaz(f"\n🔺 Seviye atladınız! Yeni seviye: {self.seviye}", Fore.MAGENTA)

    def envantere_ekle(self, esya):
        if len(self.envanter) < MAX_INVENTORY:
            self.envanter.append(esya)
            esya_adi = esya.isim.lower()
            self.kazandigi_esyalar.append(esya_adi)
            yavas_yaz(f"📦 {esya.isim} envantere eklendi.", Fore.CYAN)
            
            # Excalibur eklendiyse görevi kontrol et
            if esya_adi == "excalibur":
                self.gorev_durumunu_kontrol_et()
        else:
            yavas_yaz("⚠️ Envanter dolu!", Fore.YELLOW)

    def envanteri_goster(self):
        if not self.envanter:
            yavas_yaz("Envanter boş.", Fore.YELLOW)
            return None
        for i, esya in enumerate(self.envanter):
            print(f"{i + 1}. {esya.isim}")
        secim = input(Fore.CYAN + "Kullanmak istediğiniz eşya numarası (iptal için boş bırak): " + Style.RESET_ALL)
        if secim.isdigit():
            index = int(secim) - 1
            if 0 <= index < len(self.envanter):
                esya = self.envanter.pop(index)
                esya.kullan(self)
                
    def gorev_durumunu_kontrol_et(self):
        g = self.gorev
        
        # Görev zaten tamamlanmışsa tekrar kontrol etme
        if g["tamamlandi"]:
            return
            
        tamamlandi = False
        if g["hedef"] == "canavar":
            if self.oldurulen_canavarlar >= g["adet"]:
            	tamamlandi = self.oldurulen_canavarlar >= g["adet"]
        elif g["hedef"] == "boss":
        	tamamlandi = self.oldurulen_bosslar >= g["adet"]
        elif g["hedef"] == "iksir":
        	adet = sum(1 for esya in self.envanter if esya.isim in ["İksir", "Süper İksir"])
        	tamamlandi = adet >= g["adet"]
        elif g["hedef"] == "buyu_ogren":
        	tamamlandi = self.ogrenilen_buyuler-1 >= g["adet"]
        elif g["hedef"] == "seviye_atla":
        	tamamlandi = self.seviye >= g["adet"] + 1  # Başlangıç seviyesi 1 olduğu için
        elif g["hedef"] == "excalibur":
            tamamlandi = "excalibur" in self.kazandigi_esyalar
            
        if tamamlandi:
            self.gorev_tamamla()
            
    def gorev_tamamla(self):
        g = self.gorev
        g["tamamlandi"] = True
        self.tamamlanan_gorevler.append(g.copy())
        
        yavas_yaz(f"\n🎉 Görev tamamlandı: {g['hedef']}!", Fore.GREEN)
        yavas_yaz(f"🎁 Ödüller: {g['odul_xp']} XP, {g['odul_altin']} Altın", Fore.YELLOW)
        
        self.xp += g["odul_xp"]
        self.altin += g["odul_altin"]
        self.oldurulen_canavarlar = 0
        
        # Yeni görev seç
        self.gorev = self.rastgele_tamamlanmamis_gorev()
        yavas_yaz(f"📜 Yeni görev: {self.gorev_metni_olustur()}", Fore.CYAN)

    def gorev_metni_olustur(self):
        g = self.gorev
        if g["hedef"] == "canavar":
            return f"{g['adet']} canavar öldür ({self.oldurulen_canavarlar}/{g['adet']})"
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
        return "Bilinmeyen görev"

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
        self.saldiri = 50 if CHEATS else 15
        self.isim = "Excalibur"

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
        yavas_yaz("❤️ Can 20 puan yenilendi.", Fore.RED)

class SuperIksir(Esya):
    def __init__(self):
        super().__init__("Süper İksir")

    def kullan(self, oyuncu):
        oyuncu.hp = min(oyuncu.max_hp, oyuncu.hp + 50)
        yavas_yaz("❤️ Can 50 puan yenilendi.", Fore.RED)

class ManaIksiri(Esya):
    def __init__(self):
        super().__init__("Mana İksiri")

    def kullan(self, oyuncu):
        oyuncu.mana = min(oyuncu.max_mana, oyuncu.mana + 20)
        yavas_yaz("🔷 Mana 20 puan yenilendi.", Fore.BLUE)

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
         "100 hasar verir (Sadece bosslara karşı)", 5)
]

def buyu_kullan(oyuncu, dusman, mana_sinirsiz=False):
    print(Fore.CYAN + Style.BRIGHT + "\n📜-- Büyü Defteri --" + Style.RESET_ALL)
    for i, b in enumerate(BUYULER):
        if oyuncu.seviye >= b.seviye_gereksinimi:
            print(Fore.YELLOW + f"{i+1}. {b.isim} (Mana: {b.mana_maliyeti}) - " + 
                  Fore.WHITE + f"{b.aciklama}")
    
    secim = input(Fore.CYAN + "\nBüyü numarası (iptal için boş bırak): " + Style.RESET_ALL)
    if secim.isdigit():
        index = int(secim) - 1
        if 0 <= index < len(BUYULER):
            b = BUYULER[index]
            
            if oyuncu.seviye < b.seviye_gereksinimi:
                yavas_yaz("Bu büyüyü kullanmak için yeterli seviyede değilsiniz!", Fore.RED)
                return
                
            if oyuncu.mana >= b.mana_maliyeti or mana_sinirsiz:
                oyuncu.mana -= b.mana_maliyeti
                b.etkisi(oyuncu, dusman)
                
                if b.isim == "Kalkan":
                    yavas_yaz(f"🛡️ Savunmanız 3 tur boyunca +5 arttı!", Fore.BLUE)
                elif b.isim == "Zehir Bulutu":
                    yavas_yaz(f"☠️ {dusman.isim} zehirlendi!", Fore.GREEN)
                elif b.isim == "Hayat Çalma":
                    yavas_yaz(f"💔 {dusman.isim}'den 20 can çaldınız!", Fore.RED)
                else:
                    yavas_yaz(f"✨ {b.isim} büyüsü uygulandı!", Fore.MAGENTA)
            else:
                yavas_yaz("Yeterli mana yok!", Fore.RED)
        else:
            yavas_yaz("Geçersiz büyü numarası!", Fore.RED)

# === GELİŞMİŞ DÜŞMAN SINIFLARI ===

class Düsman(Karakter):
    def __init__(self, boss=False):
        if boss:
            isim = random.choice(BOSS_NAMES)
            seviye = random.randint(5, 8)
            hp = 150 + seviye * 30
            saldiri = 15 + seviye * 3
            savunma = 10 + seviye
        else:
            isim = random.choice(ENEMY_NAMES)
            seviye = random.randint(1, 5)
            hp = 50 + seviye * 20
            saldiri = 8 + seviye * 2
            savunma = 5 + seviye

        super().__init__(isim, hp, seviye, saldiri, savunma)
        self.tur = random.choice(["normal", "iyilesen", "zehirli", "buyucu", "kalkanli"])
        self.boss = boss
        self.donmus = 0
        
    def davran(self, oyuncu):
        # Donma kontrolü
        if self.donmus > 0:
            self.donmus -= 1
            yavas_yaz(f"❄️ {self.isim} donmuş ve saldıramıyor!", Fore.BLUE)
            return
            
        if self.tur == "iyilesen" and self.hp < self.max_hp // 2 and random.random() < 0.3:
            iyilesme = random.randint(15, 30)
            self.hp = min(self.max_hp, self.hp + iyilesme)
            yavas_yaz(f"{self.isim} kendini {iyilesme} can iyileştirdi!", Fore.GREEN)
            return
        elif self.tur == "zehirli" and random.random() < 0.3:
            oyuncu.zehirli = True
            yavas_yaz(f"☠️ {self.isim} sizi zehirledi!", Fore.GREEN)
        elif self.tur == "buyucu" and random.random() < 0.4:
            zarar = random.randint(15, 30)
            oyuncu.hp -= zarar
            yavas_yaz(f"🔮 {self.isim} size {zarar} hasarlı büyü saldırısı yaptı!", Fore.MAGENTA)
            return
        elif self.tur == "kalkanli" and random.random() < 0.2:
            self.savunma += 3
            yavas_yaz(f"🛡️ {self.isim} savunmasını güçlendirdi!", Fore.BLUE)
            
        zarar = oyuncu.hasar_al(self.saldiri)
        yavas_yaz(f"⚔️ {self.isim} size {zarar} hasar verdi!", Fore.RED)


# === MAĞAZA SİSTEMİ ===

def magaza(oyuncu):
    print(Fore.CYAN + "\n🛒 -- Mağaza -- (Altın: 💰" + Fore.YELLOW + f" {oyuncu.altin} " + Fore.CYAN + ")" + Style.RESET_ALL)
    urunler = [
        ("İksir", 20, Iksir()),
        ("Süper İksir", 40, SuperIksir()),
        ("Mana İksiri", 25, ManaIksiri()),
        ("Kısa Kılıç", 35, KisaKilic()),
        ("Uzun Kılıç", 60, UzunKilic()),
        ("Excalibur", 120, Excalibur()),
    ]
    for i, (isim, fiyat, _) in enumerate(urunler):
        print(f"{i+1}. {isim} - {fiyat} altın")
    secim = input(Fore.CYAN + "Satın almak istediğiniz ürün numarası (iptal için boş bırak): " + Style.RESET_ALL)
    if secim.isdigit():
        index = int(secim) - 1
        if 0 <= index < len(urunler):
            isim, fiyat, nesne = urunler[index]
            if oyuncu.altin >= fiyat:
                oyuncu.altin -= fiyat
                if isinstance(nesne, TemelSilah) and nesne.saldiri > oyuncu.silah.saldiri:
                    oyuncu.silah = nesne
                    yavas_yaz(f"{isim} kuşanıldı!")
                    
                    # Excalibur alındıysa görevi kontrol et
                    if nesne.isim.lower() == "excalibur":
                        oyuncu.gorev_durumunu_kontrol_et()
                else:
                    oyuncu.envantere_ekle(nesne)
            else:
                yavas_yaz("Yetersiz altın.", Fore.RED)
                
# === SAVAŞ SİSTEMİ ===

def savas(oyuncu, boss=False):
    dusman = Düsman(boss)
    
    if boss:
        yavas_yaz(f"\n💀 {Fore.RED}{Style.BRIGHT}BOSS SAVAŞI: {dusman.isim} {Style.RESET_ALL}" +
                 f"{Fore.WHITE}(Seviye {dusman.seviye}, HP: {dusman.hp})", Fore.RED)
    else:
        yavas_yaz(f"\n⚔️ {Fore.RED}{dusman.isim} {Fore.WHITE}(Seviye {dusman.seviye}, Tür: {dusman.tur}) ile karşılaştınız!", Fore.MAGENTA)

    while oyuncu.hp > 0 and dusman.hp > 0:
        print(Fore.CYAN + f"\n🎖️ {oyuncu.isim} | HP: {oyuncu.hp}/{oyuncu.max_hp} | Mana: {oyuncu.mana}/{oyuncu.max_mana}" + Style.RESET_ALL)
        print(Fore.RED + f"💀 {dusman.isim} | HP: {dusman.hp}/{dusman.max_hp}" + Style.RESET_ALL)
        print("\n1. Saldır")
        print("2. Kaç")
        print("3. Eşya Kullan")
        print("4. Büyü Kullan")

        secim = input(Fore.CYAN + "Seçiminiz: " + Style.RESET_ALL)
        if secim == "1":
            hasar = dusman.hasar_al(oyuncu.saldir())
            yavas_yaz(f"{dusman.isim}'e {hasar} hasar verdiniz.", Fore.RED)
        elif secim == "2":
            if random.random() < RUN_CHANCE:
                yavas_yaz("🏃 Başarıyla kaçtınız!", Fore.GREEN)
                return
            else:
                yavas_yaz("Kaçamadınız!", Fore.YELLOW)
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
                yavas_yaz(f"❄️ {dusman.isim} donmuş ve saldıramıyor!", Fore.BLUE)
            else:
                if dusman.hp <= dusman.max_hp // 4 and not dusman.boss:
                    yavas_yaz(f"⚠️ {dusman.isim} çaresiz durumda ve daha agresif saldırıyor!", Fore.RED)
                    dusman.saldiri += 3
                    
                if dusman.boss and dusman.hp <= dusman.max_hp // 2:
                    yavas_yaz(f"💢 {dusman.isim} öfkelendi! Saldırı gücü arttı!", Fore.RED)
                    dusman.saldiri += 5
                    
                dusman.davran(oyuncu)

        if oyuncu.zehirli:
            oyuncu.hp -= 3
            yavas_yaz("☠️ Zehir etkisi! -3 HP")

    if oyuncu.hp <= 0:
        yavas_yaz("\n💀 Öldünüz. Oyun bitti.", Fore.RED)
        sys.exit()

   

    yavas_yaz(f"\n🎉 {dusman.isim} yok edildi! Tecrübe ve altın kazandınız.", Fore.GREEN)
    
    # Boss öldürme istatistiği
    if dusman.boss:
        oyuncu.oldurulen_bosslar += 1
        yavas_yaz(f"\n🎉 {Fore.YELLOW}BOSS YENDİNİZ! {Style.RESET_ALL}" + 
                 f"{Fore.GREEN}Büyük ödüller kazandınız!", Fore.YELLOW)
        oyuncu.deneyim_ekle(100)
        kazanc = random.randint(100, 200)
    else:
        oyuncu.oldurulen_canavarlar += 1
        oyuncu.deneyim_ekle(25)
        kazanc = random.randint(*GOLD_REWARD)
        
    oyuncu.altin += kazanc
    yavas_yaz(f"💰 {kazanc} altın kazandınız.", Fore.YELLOW)
    
    # Nadir eşya şansı
    if random.random() < (0.3 if boss else 0.1):
        nadir_esyalar = [Excalibur(), BuyuKitabi(), EfsaneviZirh()]
        yeni_esya = random.choice(nadir_esyalar)
        oyuncu.envantere_ekle(yeni_esya)
        yavas_yaz(f"✨ {Fore.MAGENTA}NADİR EŞYA BULDUNUZ: {yeni_esya.isim}{Style.RESET_ALL}", Fore.MAGENTA)

    oyuncu.gorev_durumunu_kontrol_et()

def hile_menusu(oyuncu):
    global mana_sinirsiz
    while True:
        print(Fore.CYAN + Style.BRIGHT + "\n💻 Hile Menüsü" + Style.RESET_ALL)
        print(Fore.YELLOW + "1. Canı Tam Doldur" + Style.RESET_ALL)
        print(Fore.YELLOW + "2. Mana'yı Tam Doldur" + Style.RESET_ALL)
        print(Fore.YELLOW + "3. Altın Ekle (Miktar Seç)" + Style.RESET_ALL)
        print(Fore.YELLOW + "4. Seviye Atlama (Miktar Seç)" + Style.RESET_ALL)
        print(Fore.YELLOW + "5. Excalibur Ver" + Style.RESET_ALL)
        print(Fore.YELLOW + "6. Mana Sınırsız Modu Aç/Kapa" + Style.RESET_ALL)
        print(Fore.YELLOW + "7. Envanteri Temizle" + Style.RESET_ALL)
        print(Fore.YELLOW + "8. Negatif Durumları Temizle" + Style.RESET_ALL)
        print(Fore.YELLOW + "9. Çıkış" + Style.RESET_ALL)
        secim = input(Fore.CYAN + "Seçiminiz: " + Style.RESET_ALL)

        if secim == "1":
            oyuncu.hp = oyuncu.max_hp
            yavas_yaz("Canınız tam olarak dolduruldu.", Fore.GREEN)
        elif secim == "2":
            oyuncu.mana = oyuncu.max_mana
            yavas_yaz("Mananız tam olarak dolduruldu.", Fore.BLUE)
        elif secim == "3":
            miktar = input("Eklenecek altın miktarı: ")
            if miktar.isdigit():
                oyuncu.altin += int(miktar)
                yavas_yaz(f"Altın {miktar} adet eklendi.", Fore.GREEN)
            else:
                yavas_yaz("Geçersiz miktar.", Fore.RED)
        elif secim == "4":
            miktar = input("Eklenecek seviye sayısı: ")
            if miktar.isdigit():
                for _ in range(int(miktar)):
                    oyuncu.deneyim_ekle(oyuncu.seviye * 50)
                yavas_yaz(f"{miktar} seviye atlandı.", Fore.MAGENTA)
            else:
                yavas_yaz("Geçersiz sayı.", Fore.RED)
        elif secim == "5":
            oyuncu.silah = Excalibur()
            oyuncu.kazandigi_esyalar.append("excalibur")
            yavas_yaz("Excalibur size verildi!", Fore.CYAN)
            oyuncu.gorev_durumunu_kontrol_et()  # Görevi kontrol et
        elif secim == "6":
            mana_sinirsiz = not mana_sinirsiz
            durum = "açıldı" if mana_sinirsiz else "kapatıldı"
            yavas_yaz(f"Mana sınırsız modu {durum}.", Fore.CYAN)
        elif secim == "7":
            oyuncu.envanter.clear()
            yavas_yaz("Envanter temizlendi.", Fore.YELLOW)
        elif secim == "8":
            oyuncu.zehirli = False
            yavas_yaz("Tüm negatif durumlar temizlendi.", Fore.GREEN)
        elif secim == "9":
            break
        else:
            yavas_yaz("Geçersiz giriş.", Fore.RED)

# === ANA OYUN DÖNGÜSÜ ===

def oyun():
    print(Fore.MAGENTA + Style.BRIGHT + "=== 🧝‍♂️ METİN TABANLI RPG OYUNU ===" + Style.RESET_ALL)
    isim = input(Fore.CYAN + "Karakter adınızı girin: " + Style.RESET_ALL)
    oyuncu = Oyuncu(isim)
    yavas_yaz(Fore.CYAN + Style.BRIGHT + f"Hoş geldin, {oyuncu.isim}!" + Style.RESET_ALL)
    yavas_yaz(f"📜 Aktif görev: {oyuncu.gorev_metni_olustur()}", Fore.CYAN)

    while True:
        print(Fore.CYAN + Style.BRIGHT + "\n🔹 Menü 🔹" + Style.RESET_ALL)
        print(Fore.YELLOW + "1. Savaşa Gir" + Style.RESET_ALL)
        print(Fore.YELLOW + "2. Envanteri Görüntüle" + Style.RESET_ALL)
        print(Fore.YELLOW + "3. Mağazaya Git" + Style.RESET_ALL)
        print(Fore.YELLOW + "4. Görev Durumu" + Style.RESET_ALL)
        print(Fore.YELLOW + "5. Çıkış" + Style.RESET_ALL)
        print(Fore.RED + "6. Hile Menüsü" + Style.RESET_ALL)

        secim = input("Seçiminiz: ")
        if secim == "1":
            # Normal savaş veya boss savaşı şansı
            if random.random() < 0.1 and oyuncu.seviye >= 3:
                savas(oyuncu, boss=True)
            else:
                savas(oyuncu)
        elif secim == "2":
            oyuncu.envanteri_goster()
        elif secim == "3":
            magaza(oyuncu)
        elif secim == "4":
            print(Fore.GREEN + f"\n📜 Aktif Görev: {oyuncu.gorev_metni_olustur()}")
            
            # Tamamlanan görevleri göster
            if oyuncu.tamamlanan_gorevler:
                print(Fore.MAGENTA + "\n🏆 Tamamlanan Görevler:")
                for i, gorev in enumerate(oyuncu.tamamlanan_gorevler):
                    print(f"{i+1}. {gorev['hedef']} - {gorev['odul_xp']} XP, {gorev['odul_altin']} Altın")
        elif secim == "5":
            yavas_yaz("Çıkılıyor... Görüşmek üzere!", Fore.CYAN)
            break
        elif secim == "6":
            hile_menusu(oyuncu)
        else:
            yavas_yaz("Geçersiz giriş.", Fore.RED)

# === OYUNU BAŞLAT ===
if __name__ == "__main__":
    oyun()