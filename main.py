import json
import os
import random
import time
from collections import defaultdict


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


# === SABİTLER ===
MAX_INVENTORY = 30
RUN_CHANCE = 0.33
GOLD_REWARD = (15, 45)
KRITIK_SANS = 0.10
HAN_TABAN_UCRET = 20       # Han ücreti = taban + seviye * çarpan
HAN_SEVIYE_UCRET = 5
ZEHIR_HASARI = 4
MANA_YENILEME = 3          # Her savaş turunda
SAVUN_MANA_BONUSU = 5      # "Savun" eylemi ekstra mana verir
YAVAS_YAZ_GECIKME = 0.002
HASAR_VARYANS = 0.10       # Hasar ±%10 oynar
MAX_KALKAN_YUKSELTME = 3   # Kalkanlı düşman en fazla kaç kez savunma artırabilir
KAYIT_DOSYASI = "rpg_kayit.json"

# Çalışma zamanı ayarları (global değişken yerine tek bir sözlük)
AYARLAR = {"animasyon": True, "hile": False, "mana_sinirsiz": False, "otokayit": True}

# Zorluk: düşman gücü çarpanı ve ödül (XP/altın) çarpanı
ZORLUKLAR = {
    "Kolay":  {"dusman": 0.8, "odul": 1.2},
    "Normal": {"dusman": 1.0, "odul": 1.0},
    "Zor":    {"dusman": 1.3, "odul": 1.4},
}

# Karakter sınıfları (başlangıç bonusları)
SINIFLAR = {
    "Savaşçı": {"aciklama": "+30 can, +3 saldırı, +2 savunma, -10 mana",
                "hp": 30, "mana": -10, "saldiri": 3, "savunma": 2,
                "altin": 0, "kritik": 0.0, "kac": 0.0, "buyu": 1.0},
    "Büyücü":  {"aciklama": "+20 mana, büyüler %25 daha güçlü, -10 can",
                "hp": -10, "mana": 20, "saldiri": 0, "savunma": 0,
                "altin": 0, "kritik": 0.0, "kac": 0.0, "buyu": 1.25},
    "Haydut":  {"aciklama": "+%10 kritik şansı, +%15 kaçış şansı, +2 saldırı, +30 altın",
                "hp": 0, "mana": 0, "saldiri": 2, "savunma": 0,
                "altin": 30, "kritik": 0.10, "kac": 0.15, "buyu": 1.0},
}

ENEMY_NAMES = ["Ork", "Zombi", "Vampir", "Kurt Adam", "Ejderha", "Kara Büyücü",
               "Goblin", "Trol", "Hayalet", "Dev Örümcek", "Dev Ork", "Minotor",
               "Su Canavarı", "Lamia", "Grifon", "Kiklop", "Harpia", "Kemik Yürüyücü",
               "Gargoyle", "Kara Şövalye", "Kurt Sürüsü", "Yeraltı Yaratığı", "İblis",
               "Şeytan Köpeği", "Yara Bandı", "Taş Golem", "Ateş Elementali",
               "Buz Elementali", "Buz Cadısı"]

BOSS_NAMES = ["Kral Ork", "Lich", "Kızıl Ejderha", "Karanlık Lordu", "Ölüm Meleği",
              "Titan", "Kara Ejder", "Cehennem Lordu", "Buz Kraliçesi", "Ateş Tanrısı",
              "Kaos Şövalyesi", "Ebedi Canavar", "Gölge Avcısı", "Yılan Tanrı", "Korku Prensi"]

# Kutsal Işın bu isimleri taşıyan yaratıklara %50 fazla hasar verir
KARANLIK_ISIMLER = ("Vampir", "Zombi", "Hayalet", "İblis", "Şeytan", "Kara", "Lich",
                    "Karanlık", "Ölüm", "Kemik", "Gölge", "Cehennem")


class OyuncuOldu(Exception):
    """Oyuncunun canı bittiğinde ana döngüye haber verir."""


# === YARDIMCI FONKSİYONLAR ===

def yavas_yaz(metin, renk=Color.WHITE, delay=None):
    if not AYARLAR["animasyon"]:
        print(renk + metin + Color.RESET, flush=True)
        return
    delay = YAVAS_YAZ_GECIKME if delay is None else delay
    print(renk, end='', flush=True)
    for harf in metin:
        print(harf, end="", flush=True)
        time.sleep(delay)
    print(Color.RESET, flush=True)


def sayi_oku(mesaj):
    """Kullanıcıdan sayı okur; geçersiz/boş/negatif girişte None döner."""
    girdi = input(Color.CYAN + mesaj + Color.RESET).strip()
    try:
        sayi = int(girdi)
    except ValueError:
        return None
    return sayi if sayi >= 0 else None


def evet_mi(mesaj):
    return input(Color.CYAN + mesaj + Color.RESET).strip().lower() in ("e", "evet", "y", "yes")


def bar(deger, maks, uzunluk=16, renk=Color.GREEN):
    oran = max(0.0, min(1.0, deger / maks)) if maks else 0.0
    dolu = round(oran * uzunluk)
    return f"{renk}{'█' * dolu}{Color.WHITE}{'░' * (uzunluk - dolu)}{Color.RESET}"


def varyans(deger):
    return int(deger * random.uniform(1 - HASAR_VARYANS, 1 + HASAR_VARYANS))


def envanter_gruplari(envanter):
    """Aynı id'li eşyaları gruplar: [[ornek_esya, adet], ...] (ilk görülme sırasıyla)."""
    gruplar = {}
    for e in envanter:
        if e.id in gruplar:
            gruplar[e.id][1] += 1
        else:
            gruplar[e.id] = [e, 1]
    return list(gruplar.values())


def envanterden_cikar(envanter, id_):
    """Verilen id'ye sahip ilk eşyayı envanterden çıkarıp döner."""
    for i, e in enumerate(envanter):
        if e.id == id_:
            return envanter.pop(i)
    return None


# === GÖREVLER ===
# tur="sayac": istatistik sayacı görev başladığından beri artmalı
# tur="esya" : belirtilen eşya bulunmalı
def _gorev(id_, tur, anahtar, adet, metin, xp, altin):
    return {"id": id_, "tur": tur, "anahtar": anahtar, "adet": adet,
            "metin": metin, "xp": xp, "altin": altin}


QUESTS = [
    _gorev("canavar", "sayac", "canavar", 5, "{adet} canavar öldür", 80, 80),
    _gorev("boss", "sayac", "boss", 1, "{adet} boss öldür", 200, 200),
    _gorev("excalibur", "esya", "excalibur", 1, "Excalibur kılıcını bul", 150, 150),
    _gorev("iksir", "sayac", "iksir", 3, "{adet} iksir edin", 60, 60),
    _gorev("buyu_ogren", "sayac", "buyu_ogren", 2, "{adet} yeni büyü öğren", 100, 100),
    _gorev("seviye_atla", "sayac", "seviye_atla", 3, "{adet} seviye atla", 120, 120),
    _gorev("kalkanli", "sayac", "kalkanli", 3, "{adet} kalkanlı düşman öldür", 90, 90),
    _gorev("buyucu", "sayac", "buyucu", 4, "{adet} büyücü düşman öldür", 110, 110),
    _gorev("altin_kazan", "sayac", "altin_kazan", 500, "{adet} altın kazan", 150, 200),
    _gorev("dev", "sayac", "dev", 1, "{adet} dev düşman öldür (Dev Ork, Dev Örümcek)", 250, 250),
    _gorev("elemental", "sayac", "elemental", 2, "{adet} Elemental öldür", 180, 180),
    _gorev("golem", "sayac", "golem", 2, "{adet} Golem öldür", 170, 170),
    _gorev("kral_magara", "esya", "kral_magara", 1, "Mağara Kralı Tacı'nı bul (bosslardan düşer)", 300, 300),
    _gorev("kutsal_kilic", "esya", "kutsal_kilic", 1, "Kutsal Kılıç'ı bul", 200, 200),
    _gorev("efsanevi_zirh", "esya", "efsanevi_zirh", 1, "Efsanevi Zırh'ı bul", 180, 180),
    _gorev("buyu_kitabi", "esya", "buyu_kitabi", 1, "Kayıp Büyü Kitabı'nı bul", 220, 220),
    _gorev("kesif", "sayac", "kesif", 4, "{adet} kez keşfe çık", 70, 70),
    _gorev("sandik", "sayac", "sandik", 2, "{adet} sandık bul", 90, 90),
]
QUEST_ID = {q["id"]: q for q in QUESTS}


# === TEMEL SINIFLAR ===

class Karakter:
    def __init__(self, isim, hp, seviye, saldiri, savunma):
        self.isim = isim
        self.hp = hp
        self.max_hp = hp
        self.seviye = seviye
        self.saldiri = saldiri
        self.savunma = savunma
        self.zehir_tur = 0
        self.donmus = 0

    def hasar_al(self, miktar):
        """Savunmaya takılan normal hasar (en az 1)."""
        zarar = max(1, int(miktar) - self.savunma)
        self.hp -= zarar
        return zarar

    def dogrudan_hasar(self, miktar):
        """Savunmayı yok sayan hasar (büyü, zehir vb.)."""
        zarar = max(0, int(miktar))
        self.hp -= zarar
        return zarar

    def iyiles(self, miktar):
        onceki = self.hp
        self.hp = min(self.max_hp, self.hp + int(miktar))
        return self.hp - onceki

    def hayatta_mi(self):
        return self.hp > 0

    def zehir_isle(self):
        if self.zehir_tur > 0:
            self.zehir_tur -= 1
            return self.dogrudan_hasar(ZEHIR_HASARI)
        return 0


# === EŞYALAR ===

class Esya:
    def __init__(self, id_, isim, aciklama=""):
        self.id = id_
        self.isim = isim
        self.aciklama = aciklama

    def etiket(self):
        return f"{self.isim} - {self.aciklama}" if self.aciklama else self.isim

    def kullan(self, oyuncu):
        """Eşya tüketildiyse True/None, tüketilmediyse False döner."""
        return True


class Iksir(Esya):
    def __init__(self):
        super().__init__("iksir", "İksir", "20 can yeniler")

    def kullan(self, oyuncu):
        if oyuncu.hp >= oyuncu.max_hp:
            yavas_yaz("Canınız zaten dolu!", Color.YELLOW)
            return False
        yavas_yaz(f"❤️ Can {oyuncu.iyiles(20)} puan yenilendi.", Color.RED)


class SuperIksir(Esya):
    def __init__(self):
        super().__init__("super_iksir", "Süper İksir", "50 can yeniler")

    def kullan(self, oyuncu):
        if oyuncu.hp >= oyuncu.max_hp:
            yavas_yaz("Canınız zaten dolu!", Color.YELLOW)
            return False
        yavas_yaz(f"❤️ Can {oyuncu.iyiles(50)} puan yenilendi.", Color.RED)


class ManaIksiri(Esya):
    def __init__(self):
        super().__init__("mana_iksiri", "Mana İksiri", "20 mana yeniler")

    def kullan(self, oyuncu):
        if oyuncu.mana >= oyuncu.max_mana:
            yavas_yaz("Mananız zaten dolu!", Color.YELLOW)
            return False
        onceki = oyuncu.mana
        oyuncu.mana = min(oyuncu.max_mana, oyuncu.mana + 20)
        yavas_yaz(f"🔷 Mana {oyuncu.mana - onceki} puan yenilendi.", Color.BLUE)


class EfsaneviZirh(Esya):
    def __init__(self):
        super().__init__("efsanevi_zirh", "Efsanevi Zırh", "kalıcı +10 savunma")

    def kullan(self, oyuncu):
        oyuncu.savunma += 10
        yavas_yaz("🛡️ Savunmanız +10 arttı! (Kalıcı)", Color.BLUE)


class BuyuKitabi(Esya):
    def __init__(self):
        super().__init__("buyu_kitabi", "Kayıp Büyü Kitabı", "2 yeni büyü öğretir")

    def kullan(self, oyuncu):
        bilinmeyenler = [b for b in BUYULER if b.isim not in oyuncu.bilinen_buyuler]
        if not bilinmeyenler:
            yavas_yaz("Tüm büyüleri zaten biliyorsunuz!", Color.YELLOW)
            return False
        yavas_yaz("📖 Kitabı okuyorsunuz...", Color.MAGENTA)
        for b in random.sample(bilinmeyenler, min(2, len(bilinmeyenler))):
            oyuncu.buyu_ogren(b.isim)


class KralMagaraTaci(Esya):
    def __init__(self):
        super().__init__("kral_magara", "Mağara Kralı Tacı", "kalıcı +50 maksimum can")

    def kullan(self, oyuncu):
        oyuncu.max_hp += 50
        oyuncu.hp += 50
        yavas_yaz("👑 Maksimum canınız +50 arttı! (Kalıcı)", Color.RED)


# === SİLAHLAR ve ZIRHLAR (kuşanılabilir eşyalar) ===

class TemelSilah(Esya):
    def __init__(self, id_="yumruk", isim="Yumruk", saldiri=0):
        super().__init__(id_, isim)
        self.saldiri = saldiri

    def etiket(self):
        return f"{self.isim} (+{self.saldiri} saldırı)"

    def kullan(self, oyuncu):
        oyuncu.silah_kusan(self)


class Hancer(TemelSilah):
    def __init__(self):
        super().__init__("hancer", "Hançer", 3)


class KisaKilic(TemelSilah):
    def __init__(self):
        super().__init__("kisa_kilic", "Kısa Kılıç", 5)


class UzunKilic(TemelSilah):
    def __init__(self):
        super().__init__("uzun_kilic", "Uzun Kılıç", 8)


class Excalibur(TemelSilah):
    def __init__(self):
        super().__init__("excalibur", "Excalibur", 15)


class KutsalKilic(TemelSilah):
    def __init__(self):
        super().__init__("kutsal_kilic", "Kutsal Kılıç", 18)


class EjderhaKilic(TemelSilah):
    def __init__(self):
        super().__init__("ejderha_kilici", "Ejderha Kılıcı", 22)


class TemelZirh(Esya):
    def __init__(self, id_, isim, savunma):
        super().__init__(id_, isim)
        self.savunma = savunma

    def etiket(self):
        return f"{self.isim} (+{self.savunma} savunma)"

    def kullan(self, oyuncu):
        oyuncu.zirh_kusan(self)


class DeriZirh(TemelZirh):
    def __init__(self):
        super().__init__("deri_zirh", "Deri Zırh", 2)


class ZincirZirh(TemelZirh):
    def __init__(self):
        super().__init__("zincir_zirh", "Zincir Zırh", 4)


class PlakaZirh(TemelZirh):
    def __init__(self):
        super().__init__("plaka_zirh", "Plaka Zırh", 7)


class EjderhaZirhi(TemelZirh):
    def __init__(self):
        super().__init__("ejderha_zirhi", "Ejderha Pulu Zırhı", 9)


# Kayıt/yükleme için id -> sınıf eşlemesi
ESYA_SINIFLARI = {s().id: s for s in (
    TemelSilah, Iksir, SuperIksir, ManaIksiri, EfsaneviZirh, BuyuKitabi, KralMagaraTaci,
    Hancer, KisaKilic, UzunKilic, Excalibur, KutsalKilic, EjderhaKilic,
    DeriZirh, ZincirZirh, PlakaZirh, EjderhaZirhi,
)}


def esya_olustur(id_):
    sinif = ESYA_SINIFLARI.get(id_)
    return sinif() if sinif else None


# === BÜYÜLER ===
# Her büyü efekt fonksiyonu (oyuncu, düşman) alır ve ekrana yazılacak metni döner.

class Buyu:
    def __init__(self, isim, mana_maliyeti, etkisi, aciklama, seviye_gereksinimi=1,
                 sadece_boss=False, iyilestirici=False):
        self.isim = isim
        self.mana_maliyeti = mana_maliyeti
        self.etkisi = etkisi
        self.aciklama = aciklama
        self.seviye_gereksinimi = seviye_gereksinimi
        self.sadece_boss = sadece_boss
        self.iyilestirici = iyilestirici   # Can doluyken kullanılamaz


def _ates_topu(o, d):
    return f"🔥 Ateş Topu {d.isim}'e {d.dogrudan_hasar(25)} hasar verdi!"


def _buz_mizragi(o, d):
    z = d.dogrudan_hasar(35)
    d.donmus = max(d.donmus, 1)
    return f"❄️ Buz Mızrağı {d.isim}'e {z} hasar verdi ve onu dondurdu!"


def _yildirim(o, d):
    return f"⚡ Yıldırım {d.isim}'e {d.dogrudan_hasar(50)} hasar verdi!"


def _iyilestir(o, d):
    return f"💚 {o.iyiles(30)} can iyileştirdiniz."


def _kalkan(o, d):
    o.savunma_buff_ekle(5, 3)
    return "🛡️ Savunmanız 3 tur boyunca +5 arttı!"


def _zehir_bulutu(o, d):
    z = d.dogrudan_hasar(20)
    d.zehir_tur = 3
    return f"☠️ {d.isim} {z} hasar aldı ve zehirlendi!"


def _hayat_calma(o, d):
    z = d.dogrudan_hasar(40)
    c = o.iyiles(20)
    return f"💔 {d.isim}'den {z} hasar verip {c} can çaldınız!"


def _meteor(o, d):
    return f"☄️ Meteor Yağmuru {d.isim}'e {d.dogrudan_hasar(100)} hasar verdi!"


def _kutsal_kalkan(o, d):
    o.savunma_buff_ekle(10, 3)
    return f"✨ Savunmanız 3 tur +10 arttı ve {o.iyiles(25)} can iyileştirdiniz!"


def _zaman_donmasi(o, d):
    d.donmus = max(d.donmus, 2)
    return f"⏳ {d.isim} 2 tur boyunca dondu!"


def _kutsal_isin(o, d):
    hasar = 75
    ek = ""
    if any(k in d.isim for k in KARANLIK_ISIMLER):
        hasar = int(hasar * 1.5)
        ek = " (Karanlık yaratığa karşı etkili!)"
    return f"🌟 Kutsal Işın {d.isim}'e {d.dogrudan_hasar(hasar)} hasar verdi!{ek}"


BUYULER = [
    Buyu("Ateş Topu", 10, _ates_topu, "25 hasar verir", 1),
    Buyu("Buz Mızrağı", 15, _buz_mizragi, "35 hasar verir ve 1 tur dondurur", 2),
    Buyu("Yıldırım Çarpması", 20, _yildirim, "50 hasar verir", 3),
    Buyu("Kendini İyileştir", 15, _iyilestir, "30 can iyileştirir", 1, iyilestirici=True),
    Buyu("Kalkan", 20, _kalkan, "3 tur boyunca savunmayı +5 artırır", 2),
    Buyu("Zehir Bulutu", 25, _zehir_bulutu, "20 hasar verir ve 3 tur zehirler", 3),
    Buyu("Hayat Çalma", 30, _hayat_calma, "40 hasar verir ve 20 can çalar", 4),
    Buyu("Meteor Yağmuru", 50, _meteor, "100 hasar verir (Sadece bosslara karşı)", 5, sadece_boss=True),
    Buyu("Kutsal Kalkan", 40, _kutsal_kalkan, "3 tur savunma +10 ve 25 can iyileştirir", 4),
    Buyu("Zaman Donması", 60, _zaman_donmasi, "Düşmanı 2 tur dondurur", 5),
    Buyu("Kutsal Işın", 45, _kutsal_isin, "75 hasar verir (karanlık yaratıklara %50 fazla)", 4),
]
BUYU_ISIMLERI = {b.isim for b in BUYULER}


def buyu_kullan(oyuncu, dusman):
    """Büyü yapıldıysa True (tur harcandı), iptal/hata durumunda False döner."""
    bilinen = [b for b in BUYULER if b.isim in oyuncu.bilinen_buyuler]
    print(Color.CYAN + Color.BRIGHT + "\n📜-- Büyü Defteri --" + Color.RESET)
    for i, b in enumerate(bilinen, 1):
        print(Color.YELLOW + f"{i}. {b.isim} (Mana: {b.mana_maliyeti}) - " +
              Color.WHITE + b.aciklama + Color.RESET)

    secim = sayi_oku("\nBüyü numarası (iptal için boş bırak): ")
    if secim is None:
        return False
    if not 1 <= secim <= len(bilinen):
        yavas_yaz("Geçersiz büyü numarası!", Color.RED)
        return False

    b = bilinen[secim - 1]
    if b.sadece_boss and not dusman.boss:
        yavas_yaz("Bu büyü sadece bosslara karşı kullanılabilir!", Color.YELLOW)
        return False
    if b.iyilestirici and oyuncu.hp >= oyuncu.max_hp:
        yavas_yaz("Canınız zaten dolu!", Color.YELLOW)
        return False
    if not AYARLAR["mana_sinirsiz"]:
        if oyuncu.mana < b.mana_maliyeti:
            yavas_yaz("Yeterli mana yok!", Color.RED)
            return False
        oyuncu.mana -= b.mana_maliyeti

    onceki_hp = dusman.hp
    yavas_yaz(b.etkisi(oyuncu, dusman), Color.MAGENTA)

    # Sınıf bonusu (Büyücü): verilen hasarı çarpanla büyüt
    carpan = oyuncu.buyu_carpani
    verilen = onceki_hp - dusman.hp
    if carpan > 1 and verilen > 0:
        ek = int(verilen * (carpan - 1))
        if ek > 0:
            dusman.hp -= ek
            yavas_yaz(f"🧙 Büyücü gücü: +{ek} ek hasar!", Color.MAGENTA)
    return True


# === OYUNCU SINIFI ===

class Oyuncu(Karakter):
    def __init__(self, isim, sinif="Savaşçı"):
        super().__init__(isim, 100, 1, 10, 5)
        if sinif not in SINIFLAR:
            sinif = "Savaşçı"
        self.sinif = sinif
        self.zorluk = "Normal"
        self.xp = 0
        self.altin = 50
        self.mana = 30
        self.max_mana = 30
        self._sinif_bonusu_uygula()
        self.envanter = []
        self.silah = TemelSilah()
        self.zirh = None
        self.savunuyor = False
        self.bulunan = set()               # Şimdiye kadar edinilen eşya id'leri
        self.istatistik = defaultdict(int)
        self.bilinen_buyuler = [b.isim for b in BUYULER if b.seviye_gereksinimi <= 1]
        self.buffler = []                  # [miktar, kalan_tur]
        self.tamamlanan_gorevler = []
        self.biten_gorev_idleri = set()
        self.gorev = None
        self.gorev_baslangic = {}
        self.yeni_gorev_sec()

    def _sinif_bonusu_uygula(self):
        b = SINIFLAR[self.sinif]
        self.max_hp += b["hp"]
        self.hp = self.max_hp
        self.max_mana += b["mana"]
        self.mana = self.max_mana
        self.saldiri += b["saldiri"]
        self.savunma += b["savunma"]
        self.altin += b["altin"]

    @property
    def kritik_sansi(self):
        return KRITIK_SANS + SINIFLAR[self.sinif]["kritik"]

    @property
    def kac_bonusu(self):
        return SINIFLAR[self.sinif]["kac"]

    @property
    def buyu_carpani(self):
        return SINIFLAR[self.sinif]["buyu"]

    # --- Kayıt / yükleme ---
    def sozluge(self):
        return {
            "isim": self.isim, "sinif": self.sinif, "zorluk": self.zorluk,
            "hp": self.hp, "max_hp": self.max_hp,
            "seviye": self.seviye, "saldiri": self.saldiri, "savunma": self.savunma,
            "xp": self.xp, "altin": self.altin, "mana": self.mana, "max_mana": self.max_mana,
            "silah": self.silah.id, "zirh": self.zirh.id if self.zirh else None,
            "envanter": [e.id for e in self.envanter],
            "bulunan": sorted(self.bulunan),
            "istatistik": dict(self.istatistik),
            "bilinen_buyuler": list(self.bilinen_buyuler),
            "tamamlanan_gorevler": [g["id"] for g in self.tamamlanan_gorevler],
            "biten_gorev_idleri": sorted(self.biten_gorev_idleri),
            "gorev": self.gorev["id"] if self.gorev else None,
            "gorev_baslangic": self.gorev_baslangic,
        }

    @classmethod
    def sozlukten(cls, v):
        o = cls(v["isim"], v.get("sinif", "Savaşçı"))
        for alan in ("hp", "max_hp", "seviye", "saldiri", "savunma", "xp", "altin", "mana", "max_mana"):
            setattr(o, alan, int(v[alan]))   # Sınıf bonusları kayıtlı değerlerle ezilir
        zorluk = v.get("zorluk", "Normal")
        o.zorluk = zorluk if zorluk in ZORLUKLAR else "Normal"
        o.silah = esya_olustur(v.get("silah", "yumruk")) or TemelSilah()
        o.zirh = esya_olustur(v["zirh"]) if v.get("zirh") else None
        o.envanter = [e for e in (esya_olustur(i) for i in v.get("envanter", [])) if e]
        o.bulunan = set(v.get("bulunan", []))
        o.istatistik = defaultdict(int, {k: int(x) for k, x in v.get("istatistik", {}).items()})
        o.bilinen_buyuler = [b for b in v.get("bilinen_buyuler", []) if b in BUYU_ISIMLERI]
        o.tamamlanan_gorevler = [QUEST_ID[i] for i in v.get("tamamlanan_gorevler", []) if i in QUEST_ID]
        o.biten_gorev_idleri = {i for i in v.get("biten_gorev_idleri", []) if i in QUEST_ID}
        kayitli_gorev = QUEST_ID.get(v.get("gorev"))
        if kayitli_gorev:
            o.gorev = kayitli_gorev
            o.gorev_baslangic = {k: int(x) for k, x in v.get("gorev_baslangic", {}).items()}
        return o

    # --- Savaş yardımcıları ---
    def saldir(self):
        return self.saldiri + self.silah.saldiri

    def hasar_al(self, miktar):
        if self.savunuyor:
            miktar *= 0.5
        return super().hasar_al(miktar)

    def savunma_buff_ekle(self, miktar, tur):
        self.savunma += miktar
        self.buffler.append([miktar, tur])

    def tur_sonu(self):
        """Her savaş turunun sonunda çağrılır: buff süreleri ve mana yenileme."""
        self.savunuyor = False
        kalan = []
        for b in self.buffler:
            b[1] -= 1
            if b[1] <= 0:
                self.savunma -= b[0]
                yavas_yaz("Geçici savunma etkisi sona erdi.", Color.BLUE)
            else:
                kalan.append(b)
        self.buffler = kalan
        self.mana = min(self.max_mana, self.mana + MANA_YENILEME)

    def savas_temizle(self):
        for miktar, _ in self.buffler:
            self.savunma -= miktar
        self.buffler = []
        self.zehir_tur = 0
        self.savunuyor = False

    # --- Gelişim ---
    def deneyim_ekle(self, miktar):
        self.xp += miktar
        while self.xp >= self.seviye * 50:
            self.xp -= self.seviye * 50
            self.seviye += 1
            self.max_hp += 10
            self.hp = self.max_hp
            self.max_mana += 10
            self.mana = self.max_mana
            self.saldiri += 2
            self.savunma += 1
            self.istatistik["seviye_atla"] += 1
            yavas_yaz(f"\n🔺 Seviye atladınız! Yeni seviye: {self.seviye}", Color.MAGENTA)
            for b in BUYULER:
                if b.seviye_gereksinimi <= self.seviye and b.isim not in self.bilinen_buyuler:
                    self.buyu_ogren(b.isim)
        self.gorev_kontrol()

    def altin_ekle(self, miktar):
        self.altin += miktar
        self.istatistik["altin_kazan"] += miktar

    def buyu_ogren(self, isim):
        if isim not in self.bilinen_buyuler:
            self.bilinen_buyuler.append(isim)
            self.istatistik["buyu_ogren"] += 1
            yavas_yaz(f"📖 Yeni büyü öğrendiniz: {isim}!", Color.MAGENTA)
            self.gorev_kontrol()

    # --- Eşya yönetimi ---
    def esya_kaydet(self, esya):
        """Bir eşya edinildiğinde istatistik ve görev takibini günceller."""
        self.bulunan.add(esya.id)
        if esya.id in ("iksir", "super_iksir"):
            self.istatistik["iksir"] += 1
        self.gorev_kontrol()

    def envantere_ekle(self, esya):
        if len(self.envanter) >= MAX_INVENTORY:
            yavas_yaz("⚠️ Envanter dolu!", Color.YELLOW)
            return False
        self.envanter.append(esya)
        yavas_yaz(f"📦 {esya.isim} envantere eklendi.", Color.CYAN)
        self.esya_kaydet(esya)
        return True

    def _eski_ekipmani_birak(self, eski):
        if len(self.envanter) < MAX_INVENTORY:
            self.envanter.append(eski)
            yavas_yaz(f"📦 {eski.isim} envantere kondu.", Color.CYAN)
        else:
            yavas_yaz(f"⚠️ Envanter dolu, {eski.isim} yerde kaldı.", Color.YELLOW)

    def silah_kusan(self, silah):
        eski = self.silah
        self.silah = silah
        yavas_yaz(f"⚔️ {silah.isim} kuşanıldı!", Color.CYAN)
        if eski.saldiri > 0:
            self._eski_ekipmani_birak(eski)
        self.esya_kaydet(silah)

    def zirh_kusan(self, zirh):
        eski = self.zirh
        self.zirh = zirh
        self.savunma += zirh.savunma - (eski.savunma if eski else 0)
        yavas_yaz(f"🛡️ {zirh.isim} giyildi! (+{zirh.savunma} savunma)", Color.CYAN)
        if eski:
            self._eski_ekipmani_birak(eski)
        self.esya_kaydet(zirh)

    def ekipman_daha_iyi_mi(self, esya):
        if isinstance(esya, TemelSilah):
            return esya.saldiri > self.silah.saldiri
        if isinstance(esya, TemelZirh):
            return esya.savunma > (self.zirh.savunma if self.zirh else 0)
        return False

    def envanteri_goster(self):
        """Bir eşya kullanıldıysa True döner."""
        if not self.envanter:
            yavas_yaz("Envanter boş.", Color.YELLOW)
            return False
        gruplar = envanter_gruplari(self.envanter)
        print(Color.CYAN + f"\n🎒 Envanter ({len(self.envanter)}/{MAX_INVENTORY})" + Color.RESET)
        for i, (esya, adet) in enumerate(gruplar, 1):
            print(f"{i}. {esya.etiket()}" + (f"  x{adet}" if adet > 1 else ""))
        secim = sayi_oku("Kullanmak istediğiniz eşya numarası (iptal için boş bırak): ")
        if secim is None or not 1 <= secim <= len(gruplar):
            return False
        esya = envanterden_cikar(self.envanter, gruplar[secim - 1][0].id)
        if esya.kullan(self) is False:
            self.envanter.append(esya)
            return False
        return True

    # --- Görevler ---
    def yeni_gorev_sec(self):
        def uygun(q):
            return not (q["tur"] == "esya" and q["anahtar"] in self.bulunan)

        adaylar = [q for q in QUESTS if q["id"] not in self.biten_gorev_idleri and uygun(q)]
        if not adaylar:  # Hepsi bitti: döngüyü baştan başlat
            self.biten_gorev_idleri.clear()
            adaylar = [q for q in QUESTS if uygun(q)]
        self.gorev = random.choice(adaylar)
        self.gorev_baslangic = dict(self.istatistik)

    def gorev_ilerleme(self):
        g = self.gorev
        if g["tur"] == "esya":
            return (1 if g["anahtar"] in self.bulunan else 0), 1
        ilerleme = self.istatistik[g["anahtar"]] - self.gorev_baslangic.get(g["anahtar"], 0)
        return min(ilerleme, g["adet"]), g["adet"]

    def gorev_metni_olustur(self):
        g = self.gorev
        ilerleme, hedef = self.gorev_ilerleme()
        metin = g["metin"].format(adet=g["adet"])
        if g["tur"] == "esya":
            return f"{metin} {'✅' if ilerleme else '❌'}"
        return f"{metin} ({ilerleme}/{hedef})"

    def gorev_kontrol(self):
        if self.gorev is None:
            return
        ilerleme, hedef = self.gorev_ilerleme()
        if ilerleme >= hedef:
            self.gorev_tamamla()

    def gorev_tamamla(self):
        g = self.gorev
        self.gorev = None  # Ödül verirken tekrar tetiklenmesin
        self.biten_gorev_idleri.add(g["id"])
        self.tamamlanan_gorevler.append(g)

        yavas_yaz(f"\n🎉 Görev tamamlandı: {g['metin'].format(adet=g['adet'])}", Color.GREEN)
        yavas_yaz(f"🎁 Ödüller: {g['xp']} XP, {g['altin']} Altın", Color.YELLOW)
        self.altin_ekle(g["altin"])
        self.deneyim_ekle(g["xp"])

        self.yeni_gorev_sec()
        yavas_yaz(f"📜 Yeni görev: {self.gorev_metni_olustur()}", Color.CYAN)


# === DÜŞMAN SINIFI ===

class Dusman(Karakter):
    def __init__(self, oyuncu_seviye, boss=False, zorluk="Normal"):
        if boss:
            isim = random.choice(BOSS_NAMES)
            seviye = random.randint(4 + oyuncu_seviye // 2, 7 + oyuncu_seviye // 2)
            hp = 150 + seviye * 30
            saldiri = 16 + seviye * 3
            savunma = 6 + seviye
        else:
            isim = random.choice(ENEMY_NAMES)
            seviye = random.randint(max(1, oyuncu_seviye // 2), oyuncu_seviye // 2 + 3)
            hp = 40 + seviye * 20
            saldiri = 8 + seviye * 2
            savunma = 1 + seviye

        super().__init__(isim, hp, seviye, saldiri, savunma)
        self.tur = random.choice(["normal", "iyilesen", "zehirli", "buyucu", "kalkanli"])
        self.boss = boss
        self.ofkeli = False
        self.kalkan_sayisi = 0

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
            self.savunma += 6
            self.saldiri -= 3

        # Zorluk çarpanı
        carpan = ZORLUKLAR.get(zorluk, ZORLUKLAR["Normal"])["dusman"]
        self.hp = max(1, int(self.hp * carpan))
        self.saldiri = max(1, int(self.saldiri * carpan))
        self.max_hp = self.hp

    def ofke_kontrol(self):
        """Can azaldığında bir kez güçlenir."""
        if self.ofkeli:
            return
        if self.boss and self.hp <= self.max_hp // 2:
            self.ofkeli = True
            self.saldiri += 5
            yavas_yaz(f"💢 {self.isim} öfkelendi! Saldırı gücü arttı!", Color.RED)
        elif not self.boss and self.hp <= self.max_hp // 4:
            self.ofkeli = True
            self.saldiri += 3
            yavas_yaz(f"⚠️ {self.isim} çaresiz durumda ve daha agresif saldırıyor!", Color.RED)

    def davran(self, oyuncu):
        if self.donmus > 0:
            self.donmus -= 1
            yavas_yaz(f"❄️ {self.isim} donmuş ve saldıramıyor!", Color.BLUE)
            return

        # Özel yetenekler
        if self.tur == "dev" and random.random() < 0.4:
            zarar = oyuncu.hasar_al(self.saldiri * 1.5)
            yavas_yaz(f"💥 {self.isim} size {zarar} hasarlı dev saldırısı yaptı!", Color.RED)
            return
        if self.tur == "elemental":
            if "Ateş" in self.isim and random.random() < 0.5:
                zarar = oyuncu.dogrudan_hasar(25)
                yavas_yaz(f"🔥 {self.isim} size {zarar} hasarlı ateş saldırısı yaptı!", Color.RED)
                return
            if "Buz" in self.isim and random.random() < 0.4:
                oyuncu.savunma_buff_ekle(-3, 3)
                yavas_yaz(f"❄️ {self.isim} sizi yavaşlattı! 3 tur savunmanız düştü.", Color.BLUE)
                return

        if self.tur == "iyilesen" and self.hp < self.max_hp // 2 and random.random() < 0.3:
            iyilesme = self.iyiles(random.randint(15, 30))
            yavas_yaz(f"💚 {self.isim} kendini {iyilesme} can iyileştirdi!", Color.GREEN)
            return
        elif self.tur == "zehirli" and random.random() < 0.3:
            oyuncu.zehir_tur = 3
            yavas_yaz(f"☠️ {self.isim} sizi zehirledi!", Color.GREEN)
        elif self.tur == "buyucu" and random.random() < 0.4:
            zarar = oyuncu.dogrudan_hasar(random.randint(15, 30))
            yavas_yaz(f"🔮 {self.isim} size {zarar} hasarlı büyü saldırısı yaptı!", Color.MAGENTA)
            return
        elif (self.tur == "kalkanli" and self.kalkan_sayisi < MAX_KALKAN_YUKSELTME
              and random.random() < 0.2):
            self.kalkan_sayisi += 1
            self.savunma += 3
            yavas_yaz(f"🛡️ {self.isim} savunmasını güçlendirdi!", Color.BLUE)

        zarar = oyuncu.hasar_al(varyans(self.saldiri))
        yavas_yaz(f"⚔️ {self.isim} size {zarar} hasar verdi!", Color.RED)

    def incele(self):
        """Savaşta tur harcamadan düşman bilgisi gösterir."""
        yetenek = {
            "normal": "Özel yeteneği yok.",
            "iyilesen": "Canı yarının altına düşünce kendini iyileştirebilir.",
            "zehirli": "Saldırırken sizi zehirleyebilir.",
            "buyucu": "Savunmayı yok sayan büyü saldırıları yapabilir.",
            "kalkanli": f"Savunmasını artırabilir ({self.kalkan_sayisi}/{MAX_KALKAN_YUKSELTME}).",
            "dev": "%40 ihtimalle 1.5 kat güçlü saldırı yapar.",
            "elemental": "Ateş/Buz yetenekleri kullanır.",
            "golem": "Çok sağlam ama yavaştır (yüksek can ve savunma).",
        }.get(self.tur, "Bilinmiyor.")
        karanlik = any(k in self.isim for k in KARANLIK_ISIMLER)
        print(Color.CYAN + f"\n🔍 {self.isim} (Seviye {self.seviye}{', BOSS' if self.boss else ''})" + Color.RESET)
        print(f"   ❤️ Can: {max(0, self.hp)}/{self.max_hp}   ⚔️ Saldırı: {self.saldiri}   🛡️ Savunma: {self.savunma}")
        print(f"   ✨ Tür: {self.tur} - {yetenek}")
        if karanlik:
            print(Color.YELLOW + "   🌑 Karanlık yaratık: Kutsal Işın'a karşı zayıf." + Color.RESET)


# === MAĞAZA ve HAN ===

MAGAZA_URUNLERI = [
    (Iksir, 20), (SuperIksir, 40), (ManaIksiri, 25),
    (Hancer, 20), (KisaKilic, 35), (UzunKilic, 60), (Excalibur, 120),
    (KutsalKilic, 150), (EjderhaKilic, 200),
    (DeriZirh, 30), (ZincirZirh, 70), (PlakaZirh, 130), (EjderhaZirhi, 200),
    (EfsaneviZirh, 180), (BuyuKitabi, 220),
]
FIYATLAR = {sinif().id: fiyat for sinif, fiyat in MAGAZA_URUNLERI}
FIYATLAR["kral_magara"] = 150   # Mağazada satılmaz ama satılabilir


def satis_fiyati(esya):
    return FIYATLAR.get(esya.id, 100) // 2


def satin_alma_uygula(oyuncu, nesne, fiyat):
    """Satın alma başarılıysa True döner."""
    if oyuncu.altin < fiyat:
        yavas_yaz("Yetersiz altın.", Color.RED)
        return False

    if oyuncu.ekipman_daha_iyi_mi(nesne):
        oyuncu.altin -= fiyat
        nesne.kullan(oyuncu)       # Doğrudan kuşan/giy
        return True

    if len(oyuncu.envanter) >= MAX_INVENTORY:
        yavas_yaz("⚠️ Envanter dolu, satın alınamadı!", Color.YELLOW)
        return False
    oyuncu.altin -= fiyat
    oyuncu.envantere_ekle(nesne)
    return True


def esya_al(oyuncu):
    for i, (sinif, fiyat) in enumerate(MAGAZA_URUNLERI, 1):
        print(f"{i}. {sinif().etiket()} - {fiyat} altın")

    secim = sayi_oku("Satın almak istediğiniz ürün numarası (iptal için boş bırak): ")
    if secim is None or not 1 <= secim <= len(MAGAZA_URUNLERI):
        return
    sinif, fiyat = MAGAZA_URUNLERI[secim - 1]
    satin_alma_uygula(oyuncu, sinif(), fiyat)


def esya_sat(oyuncu):
    if not oyuncu.envanter:
        yavas_yaz("Satacak bir şeyiniz yok.", Color.YELLOW)
        return
    gruplar = envanter_gruplari(oyuncu.envanter)
    for i, (esya, adet) in enumerate(gruplar, 1):
        print(f"{i}. {esya.etiket()}" + (f"  x{adet}" if adet > 1 else "") +
              f" - tanesi {satis_fiyati(esya)} altın")

    secim = sayi_oku("Satmak istediğiniz eşya numarası (iptal için boş bırak): ")
    if secim is None or not 1 <= secim <= len(gruplar):
        return
    esya = envanterden_cikar(oyuncu.envanter, gruplar[secim - 1][0].id)
    fiyat = satis_fiyati(esya)
    oyuncu.altin += fiyat   # Satış geliri "altın kazan" görevine sayılmaz
    yavas_yaz(f"💰 {esya.isim} satıldı: +{fiyat} altın.", Color.YELLOW)


def gereksiz_ekipman_sat(oyuncu):
    """Kuşanılandan daha kötü olan tüm silah/zırhları toplu satar."""
    gereksiz = [e for e in oyuncu.envanter
                if isinstance(e, (TemelSilah, TemelZirh)) and not oyuncu.ekipman_daha_iyi_mi(e)]
    if not gereksiz:
        yavas_yaz("Satılacak gereksiz ekipman yok.", Color.YELLOW)
        return
    toplam = sum(satis_fiyati(e) for e in gereksiz)
    isimler = ", ".join(e.isim for e in gereksiz)
    if evet_mi(f"{isimler} → {toplam} altına satılsın mı? (e/h): "):
        for e in gereksiz:
            oyuncu.envanter.remove(e)
        oyuncu.altin += toplam
        yavas_yaz(f"💰 {len(gereksiz)} ekipman satıldı: +{toplam} altın.", Color.YELLOW)


def magaza(oyuncu):
    while True:
        print(Color.CYAN + f"\n🛒 -- Mağaza -- (Altın: 💰 {Color.YELLOW}{oyuncu.altin}{Color.CYAN})" + Color.RESET)
        print("1. Satın Al\n2. Eşya Sat\n3. Gereksiz Ekipmanı Toplu Sat\n0. Çık")
        secim = input(Color.CYAN + "Seçiminiz: " + Color.RESET).strip()
        if secim == "1":
            esya_al(oyuncu)
        elif secim == "2":
            esya_sat(oyuncu)
        elif secim == "3":
            gereksiz_ekipman_sat(oyuncu)
        elif secim == "0":
            return
        else:
            yavas_yaz("Geçersiz giriş.", Color.RED)


def han_ucreti(oyuncu):
    return HAN_TABAN_UCRET + oyuncu.seviye * HAN_SEVIYE_UCRET


def han(oyuncu):
    ucret = han_ucreti(oyuncu)
    if oyuncu.altin < ucret:
        yavas_yaz(f"Handa dinlenmek için {ucret} altın gerekir.", Color.RED)
        return
    if oyuncu.hp >= oyuncu.max_hp and oyuncu.mana >= oyuncu.max_mana:
        yavas_yaz("Zaten dinçsiniz!", Color.YELLOW)
        return
    oyuncu.altin -= ucret
    oyuncu.hp = oyuncu.max_hp
    oyuncu.mana = oyuncu.max_mana
    yavas_yaz(f"🛏️ Handa dinlendiniz. Can ve mana tamamen doldu. (-{ucret} altın)", Color.GREEN)


def karakter_durumu(oyuncu):
    print(Color.CYAN + Color.BRIGHT +
          f"\n🧝 {oyuncu.isim} - {oyuncu.sinif} - Seviye {oyuncu.seviye}  [{oyuncu.zorluk}]" + Color.RESET)
    print(f"❤️  Can:   {bar(oyuncu.hp, oyuncu.max_hp)} {oyuncu.hp}/{oyuncu.max_hp}")
    print(f"🔷 Mana:  {bar(oyuncu.mana, oyuncu.max_mana, renk=Color.BLUE)} {oyuncu.mana}/{oyuncu.max_mana}")
    print(f"✨ XP:    {bar(oyuncu.xp, oyuncu.seviye * 50, renk=Color.MAGENTA)} {oyuncu.xp}/{oyuncu.seviye * 50}")
    print(f"⚔️  Saldırı: {oyuncu.saldir()} ({oyuncu.silah.isim})   "
          f"🛡️ Savunma: {oyuncu.savunma} ({oyuncu.zirh.isim if oyuncu.zirh else 'Zırh yok'})")
    print(f"🎯 Kritik şansı: %{round(oyuncu.kritik_sansi * 100)}   "
          f"🏃 Kaçış şansı: %{round((RUN_CHANCE + oyuncu.kac_bonusu) * 100)}")
    print(f"💰 Altın: {oyuncu.altin}")
    print(f"📖 Büyüler: {', '.join(oyuncu.bilinen_buyuler)}")
    print(f"💀 Öldürülen: {oyuncu.istatistik['canavar']} canavar, {oyuncu.istatistik['boss']} boss")


# === KAYIT SİSTEMİ ===

def kaydet(oyuncu, sessiz=False):
    """Önce geçici dosyaya yazar, sonra yerine taşır (yarım kalan kayıt dosyayı bozmaz)."""
    gecici = KAYIT_DOSYASI + ".tmp"
    try:
        with open(gecici, "w", encoding="utf-8") as f:
            json.dump(oyuncu.sozluge(), f, ensure_ascii=False, indent=2)
        os.replace(gecici, KAYIT_DOSYASI)
        if sessiz:
            print(Color.GREEN + "💾 Otomatik kayıt." + Color.RESET)
        else:
            yavas_yaz(f"💾 Oyun kaydedildi ({KAYIT_DOSYASI}).", Color.GREEN)
    except OSError as hata:
        yavas_yaz(f"⚠️ Kayıt başarısız: {hata}", Color.RED)


def yukle():
    """Kayıt varsa Oyuncu döner; yoksa veya bozuksa None (bozuk dosya yedeklenir)."""
    if not os.path.exists(KAYIT_DOSYASI):
        return None
    try:
        with open(KAYIT_DOSYASI, encoding="utf-8") as f:
            return Oyuncu.sozlukten(json.load(f))
    except (OSError, ValueError, KeyError, TypeError) as hata:
        yavas_yaz(f"⚠️ Kayıt okunamadı: {hata}", Color.RED)
        try:
            os.replace(KAYIT_DOSYASI, KAYIT_DOSYASI + ".bozuk")
            yavas_yaz(f"Bozuk kayıt {KAYIT_DOSYASI}.bozuk olarak yedeklendi.", Color.YELLOW)
        except OSError:
            pass
        return None


# === SAVAŞ SİSTEMİ ===

def oyun_bitti(oyuncu):
    yavas_yaz("\n💀 Öldünüz. Oyun bitti.", Color.RED)
    print(Color.YELLOW + f"Son durum: {oyuncu.sinif} | Seviye {oyuncu.seviye} | "
          f"{oyuncu.istatistik['canavar']} canavar, {oyuncu.istatistik['boss']} boss | "
          f"{len(oyuncu.tamamlanan_gorevler)} görev" + Color.RESET)
    raise OyuncuOldu()


def savas(oyuncu, boss=False):
    dusman = Dusman(oyuncu.seviye, boss, oyuncu.zorluk)

    if boss:
        yavas_yaz(f"\n💀 BOSS SAVAŞI: {dusman.isim} (Seviye {dusman.seviye}, HP: {dusman.hp})",
                  Color.RED + Color.BRIGHT)
    else:
        yavas_yaz(f"\n⚔️ {dusman.isim} (Seviye {dusman.seviye}, Tür: {dusman.tur}) ile karşılaştınız!",
                  Color.MAGENTA)

    while oyuncu.hayatta_mi() and dusman.hayatta_mi():
        zehir_notu = " ☠️" if oyuncu.zehir_tur else ""
        buff_notu = f" 🛡️+{sum(b[0] for b in oyuncu.buffler)}" if oyuncu.buffler else ""
        print(Color.CYAN + f"\n🎖️ {oyuncu.isim:<12} {bar(oyuncu.hp, oyuncu.max_hp)} "
              f"{oyuncu.hp}/{oyuncu.max_hp} | 🔷 {oyuncu.mana}/{oyuncu.max_mana}{zehir_notu}{buff_notu}" + Color.RESET)
        dusman_notu = (" ☠️" if dusman.zehir_tur else "") + (" ❄️" if dusman.donmus else "")
        print(Color.RED + f"💀 {dusman.isim:<12} {bar(dusman.hp, dusman.max_hp, renk=Color.RED)} "
              f"{max(0, dusman.hp)}/{dusman.max_hp}{dusman_notu}" + Color.RESET)
        print("\n1. Saldır\n2. Kaç\n3. Eşya Kullan\n4. Büyü Kullan\n5. Savun\n6. İncele (tur harcamaz)")

        secim = input(Color.CYAN + "Seçiminiz: " + Color.RESET).strip()
        tur_harcandi = True

        if secim == "1":
            ham = varyans(oyuncu.saldir())
            kritik = random.random() < oyuncu.kritik_sansi
            if kritik:
                ham = int(ham * 1.5)
            hasar = dusman.hasar_al(ham)
            yavas_yaz(f"{'💥 KRİTİK! ' if kritik else ''}{dusman.isim}'e {hasar} hasar verdiniz.", Color.RED)
        elif secim == "2":
            sans = (RUN_CHANCE + oyuncu.kac_bonusu) * (0.5 if dusman.boss else 1)
            if random.random() < sans:
                oyuncu.savas_temizle()
                yavas_yaz("🏃 Başarıyla kaçtınız!", Color.GREEN)
                return
            yavas_yaz("Kaçamadınız!", Color.YELLOW)
        elif secim == "3":
            tur_harcandi = oyuncu.envanteri_goster()
        elif secim == "4":
            tur_harcandi = buyu_kullan(oyuncu, dusman)
        elif secim == "5":
            oyuncu.savunuyor = True
            oyuncu.mana = min(oyuncu.max_mana, oyuncu.mana + SAVUN_MANA_BONUSU)
            yavas_yaz(f"🛡️ Savunma duruşuna geçtiniz: bu tur darbeler yarıya düşer (+{SAVUN_MANA_BONUSU} mana).",
                      Color.BLUE)
        elif secim == "6":
            dusman.incele()
            continue
        else:
            yavas_yaz("Geçersiz seçim.")
            continue

        if not tur_harcandi:  # İptal edilen eylemler tur harcamaz
            continue

        # Düşman turu
        if dusman.hayatta_mi():
            dusman.ofke_kontrol()
            dusman.davran(oyuncu)
        if dusman.hayatta_mi():
            zehir = dusman.zehir_isle()
            if zehir:
                yavas_yaz(f"☠️ {dusman.isim} zehirden {zehir} hasar aldı.", Color.GREEN)

        # Tur sonu etkileri
        if oyuncu.hayatta_mi():
            zehir = oyuncu.zehir_isle()
            if zehir:
                yavas_yaz(f"☠️ Zehir etkisi! -{zehir} HP", Color.GREEN)
            oyuncu.tur_sonu()

    oyuncu.savas_temizle()

    if not oyuncu.hayatta_mi():
        oyun_bitti(oyuncu)

    # --- Zafer ---
    ist = oyuncu.istatistik
    if dusman.boss:
        ist["boss"] += 1
    else:
        ist["canavar"] += 1
    if "Dev" in dusman.isim:
        ist["dev"] += 1
    if "Elemental" in dusman.isim:
        ist["elemental"] += 1
    if "Golem" in dusman.isim:
        ist["golem"] += 1
    if dusman.tur == "kalkanli":
        ist["kalkanli"] += 1
    if dusman.tur == "buyucu":
        ist["buyucu"] += 1

    yavas_yaz(f"\n🎉 {dusman.isim} yok edildi!", Color.GREEN)

    if dusman.boss:
        yavas_yaz("🏆 BOSS YENDİNİZ! Büyük ödüller kazandınız!", Color.YELLOW)
        xp = 120 + dusman.seviye * 10
        kazanc = random.randint(150, 300)
    else:
        xp = 30 + dusman.seviye * 5
        kazanc = random.randint(*GOLD_REWARD) + dusman.seviye * 3

    odul = ZORLUKLAR[oyuncu.zorluk]["odul"]
    xp, kazanc = int(xp * odul), int(kazanc * odul)

    oyuncu.altin_ekle(kazanc)
    yavas_yaz(f"💰 {kazanc} altın ve ✨ {xp} XP kazandınız.", Color.YELLOW)

    # Nadir eşya şansı
    if random.random() < (0.4 if boss else 0.15):
        havuz = [Excalibur, Iksir, SuperIksir, ManaIksiri, KutsalKilic, EfsaneviZirh,
                 BuyuKitabi, ZincirZirh, PlakaZirh]
        if boss:
            havuz += [KralMagaraTaci, EjderhaKilic, EjderhaZirhi]
        yeni_esya = random.choice(havuz)()
        yavas_yaz(f"✨ NADİR EŞYA BULDUNUZ: {yeni_esya.isim}", Color.MAGENTA)
        oyuncu.envantere_ekle(yeni_esya)

    oyuncu.deneyim_ekle(xp)  # En sonda: seviye atlama ve görev kontrolünü de tetikler


# === KEŞİF ===

def kesfet(oyuncu):
    oyuncu.istatistik["kesif"] += 1
    yavas_yaz("\n🧭 Etrafı keşfe çıktınız...", Color.CYAN)
    olay = random.choices(["sandik", "tuzak", "pinar", "tuccar", "pusu", "bos"],
                          weights=[25, 15, 15, 10, 20, 15])[0]

    if olay == "sandik":
        oyuncu.istatistik["sandik"] += 1
        yavas_yaz("📦 Eski bir sandık buldunuz!", Color.YELLOW)
        if random.random() < 0.6:
            altin = random.randint(20, 60) + oyuncu.seviye * 5
            oyuncu.altin_ekle(altin)
            yavas_yaz(f"💰 Sandıktan {altin} altın çıktı!", Color.YELLOW)
        else:
            esya = random.choice([Iksir, Iksir, ManaIksiri, SuperIksir, DeriZirh, Hancer])()
            yavas_yaz(f"🎁 Sandıktan {esya.isim} çıktı!", Color.MAGENTA)
            oyuncu.envantere_ekle(esya)
    elif olay == "tuzak":
        zarar = max(0, min(5 + oyuncu.seviye * 3, oyuncu.hp - 1))   # Tuzak öldürmez
        oyuncu.dogrudan_hasar(zarar)
        yavas_yaz(f"🪤 Gizli bir tuzağa yakalandınız! -{zarar} HP", Color.RED)
    elif olay == "pinar":
        can = oyuncu.iyiles(oyuncu.max_hp * 0.3)
        mana = min(oyuncu.max_mana - oyuncu.mana, int(oyuncu.max_mana * 0.3))
        oyuncu.mana += mana
        yavas_yaz(f"⛲ Şifalı bir pınar buldunuz! +{can} can, +{mana} mana.", Color.GREEN)
    elif olay == "tuccar":
        sinif, fiyat = random.choice(MAGAZA_URUNLERI)
        nesne = sinif()
        indirimli = int(fiyat * 0.7)
        yavas_yaz(f"🧳 Gezgin bir tüccar {nesne.isim} satıyor: {indirimli} altın (normalde {fiyat}).",
                  Color.CYAN)
        if evet_mi("Satın alınsın mı? (e/h): "):
            satin_alma_uygula(oyuncu, nesne, indirimli)
    elif olay == "pusu":
        yavas_yaz("⚠️ Pusuya düştünüz!", Color.RED)
        savas(oyuncu)
    else:
        yavas_yaz("Etrafta ilginç bir şey bulamadınız.", Color.WHITE)

    oyuncu.gorev_kontrol()


# === AYARLAR ve HİLE MENÜSÜ ===

def hile_menusu(oyuncu):
    while True:
        print(Color.CYAN + Color.BRIGHT + "\n💻 Hile Menüsü" + Color.RESET)
        for satir in ["1. Canı Tam Doldur", "2. Mana'yı Tam Doldur", "3. Altın Ekle (Miktar Seç)",
                      "4. Seviye Atlama (Miktar Seç, en fazla 50)", "5. Excalibur Ver",
                      "6. Mana Sınırsız Modu Aç/Kapa", "7. Envanteri Temizle",
                      "8. Negatif Durumları Temizle", "9. Çıkış"]:
            print(Color.YELLOW + satir + Color.RESET)
        secim = input(Color.CYAN + "Seçiminiz: " + Color.RESET).strip()

        if secim == "1":
            oyuncu.hp = oyuncu.max_hp
            yavas_yaz("Canınız tam olarak dolduruldu.", Color.GREEN)
        elif secim == "2":
            oyuncu.mana = oyuncu.max_mana
            yavas_yaz("Mananız tam olarak dolduruldu.", Color.BLUE)
        elif secim == "3":
            miktar = sayi_oku("Eklenecek altın miktarı: ")
            if miktar is None:
                yavas_yaz("Geçersiz miktar.", Color.RED)
            else:
                oyuncu.altin_ekle(miktar)
                yavas_yaz(f"{miktar} altın eklendi.", Color.GREEN)
        elif secim == "4":
            miktar = sayi_oku("Eklenecek seviye sayısı: ")
            if miktar is None:
                yavas_yaz("Geçersiz sayı.", Color.RED)
            else:
                miktar = min(miktar, 50)
                for _ in range(miktar):
                    oyuncu.deneyim_ekle(oyuncu.seviye * 50 - oyuncu.xp)
                yavas_yaz(f"{miktar} seviye atlandı.", Color.MAGENTA)
        elif secim == "5":
            oyuncu.silah_kusan(Excalibur())
        elif secim == "6":
            AYARLAR["mana_sinirsiz"] = not AYARLAR["mana_sinirsiz"]
            durum = "açıldı" if AYARLAR["mana_sinirsiz"] else "kapatıldı"
            yavas_yaz(f"Mana sınırsız modu {durum}.", Color.CYAN)
        elif secim == "7":
            oyuncu.envanter.clear()
            yavas_yaz("Envanter temizlendi.", Color.YELLOW)
        elif secim == "8":
            oyuncu.zehir_tur = 0
            yavas_yaz("Tüm negatif durumlar temizlendi.", Color.GREEN)
        elif secim == "9":
            break
        else:
            yavas_yaz("Geçersiz giriş.", Color.RED)


def ayarlar_menusu(oyuncu):
    def durum(acik):
        return "AÇIK ✅" if acik else "KAPALI ❌"

    while True:
        print(Color.CYAN + Color.BRIGHT + "\n⚙️ Ayarlar" + Color.RESET)
        print(Color.YELLOW + f"1. Yazı animasyonu: {durum(AYARLAR['animasyon'])}")
        print(f"2. Otomatik kayıt: {durum(AYARLAR['otokayit'])}")
        print(f"3. Zorluk: {oyuncu.zorluk}")
        print(f"4. Hile modu: {durum(AYARLAR['hile'])}" + Color.RESET)
        if AYARLAR["hile"]:
            print(Color.RED + "5. Hile Menüsü" + Color.RESET)
        print(Color.YELLOW + "0. Geri" + Color.RESET)

        secim = input(Color.CYAN + "Seçiminiz: " + Color.RESET).strip()
        if secim == "1":
            AYARLAR["animasyon"] = not AYARLAR["animasyon"]
        elif secim == "2":
            AYARLAR["otokayit"] = not AYARLAR["otokayit"]
        elif secim == "3":
            liste = list(ZORLUKLAR)
            oyuncu.zorluk = liste[(liste.index(oyuncu.zorluk) + 1) % len(liste)]
            z = ZORLUKLAR[oyuncu.zorluk]
            yavas_yaz(f"Zorluk: {oyuncu.zorluk} (düşman gücü x{z['dusman']}, ödül x{z['odul']})", Color.CYAN)
        elif secim == "4":
            AYARLAR["hile"] = not AYARLAR["hile"]
            if not AYARLAR["hile"]:
                AYARLAR["mana_sinirsiz"] = False
            yavas_yaz(f"Hile modu {'açıldı' if AYARLAR['hile'] else 'kapatıldı'}.", Color.CYAN)
        elif secim == "5" and AYARLAR["hile"]:
            hile_menusu(oyuncu)
        elif secim == "0":
            return
        else:
            yavas_yaz("Geçersiz giriş.", Color.RED)


# === ANA OYUN DÖNGÜSÜ ===

def gorev_durumu(oyuncu):
    print(Color.GREEN + f"\n📜 Aktif Görev: {oyuncu.gorev_metni_olustur()}" + Color.RESET)
    if oyuncu.tamamlanan_gorevler:
        print(Color.MAGENTA + "\n🏆 Tamamlanan Görevler:" + Color.RESET)
        for i, g in enumerate(oyuncu.tamamlanan_gorevler, 1):
            print(f"{i}. {g['metin'].format(adet=g['adet'])} - {g['xp']} XP, {g['altin']} Altın")


def olum_sonrasi():
    """Ölümden sonra: son kayıttan devam edilirse Oyuncu, aksi halde None döner."""
    kayitli = yukle()
    if kayitli and evet_mi(f"💾 Son kayıttan devam edilsin mi? ({kayitli.isim}, Seviye {kayitli.seviye}) (e/h): "):
        yavas_yaz("Kayıt yüklendi. Yeniden hoş geldin!", Color.GREEN)
        return kayitli
    return None


def sinif_sec():
    print(Color.CYAN + Color.BRIGHT + "\nSınıfınızı seçin:" + Color.RESET)
    isimler = list(SINIFLAR)
    for i, ad in enumerate(isimler, 1):
        print(Color.YELLOW + f"{i}. {ad}" + Color.WHITE + f" - {SINIFLAR[ad]['aciklama']}" + Color.RESET)
    while True:
        secim = sayi_oku("Sınıf numarası: ")
        if secim is not None and 1 <= secim <= len(isimler):
            return isimler[secim - 1]
        yavas_yaz("Geçersiz seçim.", Color.RED)


def baslangic():
    kayitli = yukle()
    if kayitli and evet_mi(f"💾 Kayıt bulundu: {kayitli.isim} ({kayitli.sinif}, Seviye {kayitli.seviye}). "
                           f"Devam edilsin mi? (e/h): "):
        yavas_yaz(f"Tekrar hoş geldin, {kayitli.isim}!", Color.CYAN + Color.BRIGHT)
        return kayitli
    isim = input(Color.CYAN + "Karakter adınızı girin: " + Color.RESET).strip() or "Kahraman"
    sinif = sinif_sec()
    oyuncu = Oyuncu(isim, sinif)
    yavas_yaz(f"Hoş geldin, {oyuncu.sinif} {oyuncu.isim}!", Color.CYAN + Color.BRIGHT)
    return oyuncu


def oyun():
    print(Color.MAGENTA + Color.BRIGHT + "=== 🧝‍♂️ METİN TABANLI RPG OYUNU ===" + Color.RESET)
    oyuncu = baslangic()
    yavas_yaz(f"📜 Aktif görev: {oyuncu.gorev_metni_olustur()}", Color.CYAN)

    while True:
        print(Color.CYAN + Color.BRIGHT + "\n🔹 Menü 🔹" + Color.RESET)
        for satir in ["1. Savaşa Gir", "2. Keşfet", "3. Envanteri Görüntüle", "4. Mağazaya Git",
                      f"5. Handa Dinlen ({han_ucreti(oyuncu)} altın)", "6. Görev Durumu",
                      "7. Karakter Durumu", "8. Kaydet", "9. Ayarlar", "0. Çıkış"]:
            print(Color.YELLOW + satir + Color.RESET)

        secim = input("Seçiminiz: ").strip()
        try:
            if secim == "1":
                boss_sansi = 0.1 + oyuncu.seviye * 0.02
                savas(oyuncu, boss=(oyuncu.seviye >= 4 and random.random() < boss_sansi))
            elif secim == "2":
                kesfet(oyuncu)
            elif secim == "3":
                oyuncu.envanteri_goster()
            elif secim == "4":
                magaza(oyuncu)
            elif secim == "5":
                han(oyuncu)
            elif secim == "6":
                gorev_durumu(oyuncu)
            elif secim == "7":
                karakter_durumu(oyuncu)
            elif secim == "8":
                kaydet(oyuncu)
            elif secim == "9":
                ayarlar_menusu(oyuncu)
            elif secim == "0":
                if evet_mi("Çıkmadan önce kaydedilsin mi? (e/h): "):
                    kaydet(oyuncu)
                yavas_yaz("Çıkılıyor... Görüşmek üzere!", Color.CYAN)
                break
            else:
                yavas_yaz("Geçersiz giriş.", Color.RED)

            # Savaş/keşif sonrası otomatik kayıt (ölüm durumunda buraya gelinmez)
            if AYARLAR["otokayit"] and secim in ("1", "2"):
                kaydet(oyuncu, sessiz=True)
        except OyuncuOldu:
            oyuncu = olum_sonrasi()
            if oyuncu is None:
                break


if __name__ == "__main__":
    try:
        oyun()
    except (KeyboardInterrupt, EOFError):
        print(Color.CYAN + "\nÇıkılıyor... Görüşmek üzere!" + Color.RESET)