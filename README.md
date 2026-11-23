# PyQuest - Terminal RPG Oyunu ⚔️

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/version-2.0.0-orange)
![Code Size](https://img.shields.io/github/languages/code-size/Memati8383/PyQuest-RPG)
![Issues](https://img.shields.io/github/issues/Memati8383/PyQuest-RPG)
![Forks](https://img.shields.io/github/forks/Memati8383/PyQuest-RPG)
![Stars](https://img.shields.io/github/stars/Memati8383/PyQuest-RPG)
![Last Commit](https://img.shields.io/github/last-commit/Memati8383/PyQuest-RPG)
![Contributors](https://img.shields.io/github/contributors/Memati8383/PyQuest-RPG)
![Top Language](https://img.shields.io/github/languages/top/Memati8383/PyQuest-RPG)

Python ile geliştirilmiş terminal tabanlı interaktif RPG oyunu. Kahramanınızı geliştirin, düşmanlarla savaşın, görevleri tamamlayın ve dünyayı keşfedin.

## ✨ Öne Çıkan Özellikler

- 🎨 **Renkli Terminal Arayüzü:** ANSI renk kodları ve can/mana/XP çubukları ile görsel olarak zenginleştirilmiş arayüz. Harici kütüphane gerektirmez.
- 💾 **Kayıt Sistemi:** JSON tabanlı kayıt ve yükleme. Kayıtlar atomik yazılır, bozuk dosya silinmek yerine `.bozuk` olarak yedeklenir.
- 🧝 **Üç Karakter Sınıfı:** Savaşçı, Büyücü ve Haydut; her biri farklı başlangıç bonusları ve oynanış sunar.
- 🎚️ **Zorluk Seviyeleri:** Kolay, Normal ve Zor. Zorluk düşman gücünü ve ödülleri birlikte ölçekler, oyun içinden değiştirilebilir.
- ⚔️ **Sıra Tabanlı Savaş:** Saldır, kaç, eşya kullan, büyü yap, savun veya düşmanı incele. Kritik vuruş ve kaçış şansı sınıfa göre değişir.
- ☠️ **Durum Etkileri:** Zehir, donma ve geçici savunma etkileri tur tur işler.
- 🧙 **11 Büyü:** Seviye atladıkça açılır, mana harcar. Meteor Yağmuru yalnızca bosslara, Kutsal Işın karanlık yaratıklara karşı etkilidir.
- 🏆 **18 Görev:** Rastgele atanır, ilerleme sayılır ve tamamlanınca XP ile altın verir. Hepsi bittiğinde döngü baştan başlar.
- 🧭 **Keşif:** Sandık, tuzak, şifalı pınar, gezgin tüccar ve pusu olayları.
- 🛒 **Mağaza:** Ekipman ve iksir alım-satımı, gereksiz ekipmanı tek seferde satma, daha iyi ekipmanı otomatik kuşanma.
- 🛏️ **Han:** Altın karşılığı can ve mana doldurma; ücret seviyeyle artar.
- 🎒 **Envanter:** En fazla 30 eşya; aynı eşyalar gruplanır.
- 💻 **Hile ve Ayar Menüsü:** Can/mana doldurma, altın, seviye, sınırsız mana, animasyon ve otomatik kayıt açma-kapama.
- 🛡️ **8 Düşman Türü:** Normal, iyileşen, zehirli, büyücü, kalkanlı, dev, elemental ve golem. Boss'lar ayrı davranış ve ödüller sunar.
- 💀 **Ölüm Sonrası Devam:** Öldüğünüzde son kayıttan devam etme seçeneği sunulur.

## 🚀 Kurulum

Harici bağımlılık yoktur; yalnızca Python standart kütüphanesi kullanılır.

1. Bilgisayarınızda Python 3.8 veya üzeri sürümün yüklü olduğundan emin olun.
   (Python yüklü değilse [python.org](https://www.python.org/downloads/) adresinden indirebilirsiniz.)

2. Projenin bulunduğu klasöre gidin ve oyunu başlatın:

```
python main.py
```

3. Karakter adınızı girin, sınıfınızı seçin ve maceraya başlayın. Kayıt varsa devam etmeniz önerilir.

## 🎮 Kontroller

Menü numaralarla çalışır. Ana menü:

| Tuş | Eylem |
|-----|-------|
| `1` | Savaşa gir (seviye 4'ten sonra boss şansı) |
| `2` | Keşfet |
| `3` | Envanteri görüntüle |
| `4` | Mağaza |
| `5` | Handa dinlen |
| `6` | Görev durumu |
| `7` | Karakter durumu |
| `8` | Kaydet |
| `9` | Ayarlar |
| `0` | Çıkış (kaydetme sorulur) |

Savaş menüsü: `1` saldır, `2` kaç, `3` eşya kullan, `4` büyü kullan, `5` savun, `6` incele. `6` tur harcamaz.

### İpuçları

- Boş bırakılan girişler işlemi iptal eder; iptal edilen eylem tur harcamaz.
- Savunmak o tur gelen hasarı yarıya indirir ve 5 mana kazandırır.
- Meteor Yağmuru yalnızca boss savaşlarında kullanılabilir.
- Can doluyken iyileştirme büyüleri ve iksirler boşa harcanmaz.
- Tuzaklar sizi asla öldürmez, en az 1 can bırakır.
- Savaş ve keşif sonrası otomatik kayıt varsayılan olarak açıktır.

## 🧩 Oyun Mekanikleri

### 🧝 Sınıflar

| Sınıf | Bonus |
|-------|-------|
| Savaşçı | +30 can, +3 saldırı, +2 savunma, -10 mana |
| Büyücü | +20 mana, büyüler %25 daha güçlü, -10 can |
| Haydut | +%10 kritik şansı, +%15 kaçış şansı, +2 saldırı, +30 altın |

### 🎚️ Zorluk

| Zorluk | Düşman gücü | Ödül |
|--------|-------------|------|
| Kolay | x0.8 | x1.2 |
| Normal | x1.0 | x1.0 |
| Zor | x1.3 | x1.4 |

### 🏆 Seviye Sistemi

- Düşmanları yenerek XP kazanın; gereken XP seviyeyle birlikte artar.
- Seviye atladıkça maksimum can, mana, saldırı ve savunma yükselir, yeni büyüler açılır.
- Seviye atlamanın bir üst sınırı yoktur; hile menüsü tek seferde en fazla 50 seviye ekler.

### ⚔️ Savaş

- Temel kritik şansı %10, temel kaçış şansı %33'tür; Haydut bunları artırır.
- Boss savaşlarında kaçış şansı yarıya iner.
- Düşmanlar canları azaldığında öfkelenip saldırı gücünü artırır.
- Kalkanlı düşmanlar en fazla 3 kez savunma yükseltebilir.
- Nadir eşya düşme şansı normal düşmanlarda %15, boss'larda %40'tır.

### 🛒 Mağaza

Satın alma, tek tek satış ve gereksiz ekipmanı toplu satış. Kuşanılan ekipmandan daha iyisini alırsanız otomatik kuşanılır, daha kötüsü envantere girer. Satış fiyatı liste fiyatının yarısıdır.

### 🏆 Görevler

Görevler canavar/boss öldürme, belirli eşyayı bulma (Excalibur, Kutsal Kılıç, Efsanevi Zırh, Büyü Kitabı, Mağara Kralı Tacı), seviye atlama, büyü öğrenme, altın kazanma, keşif ve sandık bulma gibi hedefler içerir. Aynı görev tekrar atanmaz; tümü tamamlanınca havuz sıfırlanır.

### 🧙 Büyüler

| Büyü | Mana | Seviye | Etki |
|------|------|--------|------|
| Ateş Topu | 10 | 1 | 25 hasar |
| Kendini İyileştir | 15 | 1 | 30 can |
| Buz Mızrağı | 15 | 2 | 35 hasar, 1 tur dondurma |
| Kalkan | 20 | 2 | 3 tur +5 savunma |
| Yıldırım Çarpması | 20 | 3 | 50 hasar |
| Zehir Bulutu | 25 | 3 | 20 hasar, 3 tur zehir |
| Hayat Çalma | 30 | 4 | 40 hasar, 20 can çalma |
| Kutsal Kalkan | 40 | 4 | 3 tur +10 savunma, 25 can |
| Kutsal Işın | 45 | 4 | 75 hasar, karanlık yaratıklara %50 fazla |
| Meteor Yağmuru | 50 | 5 | 100 hasar, sadece boss |
| Zaman Donması | 60 | 5 | 2 tur dondurma |

### 🛡️ Düşman Türleri

Normal, iyileşen, zehirli, büyücü, kalkanlı, dev, elemental ve golem. Savaşta `6` ile düşmanı inceleyip yeteneğini öğrenebilirsiniz.

### 🧭 Keşif

Sandık (%25), tuzak (%15), şifalı pınar (%15), gezgin tüccar (%10), pusu (%20) veya boş (%15). Tüccar ürünü %30 indirimle satar.

### 🛏️ Han

Can ve manayı tamamen doldurur. Ücret 20 + seviye × 5 altındır.

## 💾 Kayıt Sistemi

- Kayıt dosyası `rpg_kayit.json` olarak proje klasörüne yazılır.
- Kayıt önce geçici dosyaya yazılıp sonra yerine taşınır, böylece yarıda kalan yazma dosyayı bozmaz.
- Okunamayan kayıt `rpg_kayit.json.bozuk` olarak yedeklenir ve oyun yeni karakterle başlar.
- Ölümden sonra son kayıttan devam etme seçeneği sunulur.
- `rpg_kayit.json` ve `.bozuk` dosyaları sürüm kontrolüne eklenmemelidir.

## ⚙️ Ayarlar

Yazı animasyonu, otomatik kayıt, zorluk ve hile modu buradan yönetilir. Hile modu açıkken hile menüsüne erişilir; kapatıldığında sınırsız mana da kapanır.

## 🤝 Katkıda Bulunma

1. Repoyu fork'layın
2. Yeni branch oluşturun (`git checkout -b feature/awesome-feature`)
3. Değişikliklerinizi commit'leyin
4. Branch'inizi push'layın
5. Pull Request açın

## 📜 Lisans

MIT Lisansı - Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 📞 İletişim

Memati - [@Memati8383](https://github.com/Memati8383)

Proje Linki: [https://github.com/Memati8383/PyQuest-RPG](https://github.com/Memati8383/PyQuest-RPG)

---

> "Bir kod satırı, bin söze bedeldir." - Bilge Programcı
