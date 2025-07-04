
# PyQuest - Terminal RPG Oyunu �⚔️

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/version-1.0.0-orange)
![Code Size](https://img.shields.io/github/languages/code-size/Memati8383/PyQuest-RPG)
![Issues](https://img.shields.io/github/issues/Memati8383/PyQuest-RPG)
![Forks](https://img.shields.io/github/forks/Memati8383/PyQuest-RPG)
![Stars](https://img.shields.io/github/stars/Memati8383/PyQuest-RPG)
![Last Commit](https://img.shields.io/github/last-commit/Memati8383/PyQuest-RPG)
![Contributors](https://img.shields.io/github/contributors/Memati8383/PyQuest-RPG)
![Top Language](https://img.shields.io/github/languages/top/Memati8383/PyQuest-RPG)


Python ile geliştirilmiş terminal tabanlı interaktif RPG oyunu. Macera dolu bir dünyada kahramanınızı geliştirin, düşmanlarla savaşın ve efsanevi hazineleri keşfedin!

## ✨ Öne Çıkan Özellikler

- 🎨 **Renkli ve Etkileşimli Terminal Arayüzü:** Colorama kütüphanesi ile görsel olarak zenginleştirilmiş metin tabanlı oyun deneyimi.
- ⚔️ **Sıra Tabanlı Savaş Sistemi:** Stratejik kararlar alarak düşmanlarla mücadele edin.
- 📊 **Karakter Geliştirme ve Seviye Atlama:** Deneyim puanları kazanarak karakterinizi güçlendirin, yeni yetenekler edinin.
- 🛒 **Dinamik Mağaza Sistemi:** Altın kazanıp ekipman ve iksir satın alarak karakterinizi donatın.
- 🏆 **Görev ve Ödül Mekanikleri:** Çeşitli görevleri tamamlayarak ödüller kazanın ve hikayede ilerleyin.
- 🧙 **Büyü ve Özel Yetenekler:** Farklı büyüler öğrenip savaşlarda avantaj sağlayın.
- 💻 **Hile Modu (Geliştirici Seçenekleri):** Oyunu kişiselleştirmek ve test etmek için hile menüsünü kullanın.
- 🎒 **Envanter Yönetimi:** Maksimum 20 eşya taşıyabilir, eşyaları kullanabilir veya yönetebilirsiniz.
- 🛡️ **Çeşitli Düşman ve Boss Karakterleri:** Farklı türlerde düşmanlarla karşılaşarak zorlu mücadelelere katılın.
- 🔄 **Rastgele Görev ve Eşya Sistemi:** Her oyunda farklı görevler ve nadir eşyalarla benzersiz deneyim yaşayın.

## 🚀 Kurulum

1. Bilgisayarınızda Python 3.8 veya üzeri sürümün yüklü olduğundan emin olun.  
   (Python yüklü değilse [python.org](https://www.python.org/downloads/) adresinden indirebilirsiniz.)

2. Oyunu başlatmak için terminalde projenin bulunduğu klasöre gidin ve şu komutu çalıştırın:

```
python main.py
```

3. Oyun açıldığında karakter adınızı girerek maceraya başlayabilirsiniz.

## 🎮 Oyun Kontrolleri

| Komut        | Açıklama                          |
|--------------|----------------------------------|
| `savaş`      | Düşmanlarla mücadeleye girin      |
| `envanter`   | Eşyalarınızı görüntüleyin ve kullanın |
| `mağaza`     | Ekipman ve iksir satın alın       |
| `özellikler` | Karakterinizin istatistiklerini görün |
| `çıkış`      | Oyundan çıkış yapın               |

### Kontrol İpuçları

- Savaşta seçimler menü üzerinden yapılır; saldırı, kaçma, eşya kullanma veya büyü kullanma seçenekleri vardır.
- Envanterde eşyaları numara ile seçip kullanabilirsiniz.
- Mağazada altınınız kadar ürün satın alabilirsiniz.
- Görev durumunuzu menüden takip ederek ilerlemenizi kontrol edin.
- Hile modu aktifse ekstra seçenekler ve kolaylıklar kullanabilirsiniz.

## 🧩 Oyun Mekanikleri

### 🏆 Seviye Sistemi
- Düşmanları yenerek deneyim puanı (XP) kazanın.
- Belirli XP miktarına ulaştığınızda seviye atlayarak karakterinizi güçlendirin.
- Seviye atladıkça maksimum can, mana, saldırı ve savunma değerleriniz artar.
- Maksimum seviye 50’dir.

### 🎒 Envanter Yönetimi
- En fazla 20 eşya taşıyabilirsiniz.
- Envanterdeki eşyaları kullanabilir veya atabilirsiniz.
- Nadir eşyalar karakterinize kalıcı bonuslar ve özel yetenekler kazandırır.

### ⚔️ Savaş Sistemi
- Sıra tabanlı dövüş mekanizması ile stratejik kararlar alın.
- Üç saldırı türü vardır: Fiziksel saldırı, büyü kullanımı ve özel yetenekler.
- Savaşta %33 kaçma şansınız bulunur.
- Düşmanlar farklı türlerde ve zorluk seviyelerinde olup, boss savaşları ekstra zorluk ve ödüller sunar.

### 🛒 Mağaza Sistemi
- Kazandığınız altınlarla çeşitli ekipman ve iksirler satın alabilirsiniz.
- Satın aldığınız silahlar karakterinizin saldırı gücünü artırır.
- İksirler ve büyüler savaşta avantaj sağlar.

### 🏆 Görev ve Ödül Mekanikleri
- Farklı görevler tamamlayarak XP, altın ve nadir eşyalar kazanabilirsiniz.
- Görevler, canavar öldürme, özel eşya bulma, seviye atlama gibi çeşitli hedefler içerir.
- Tamamlanan görevler karakter gelişiminize katkı sağlar.

### 🧙 Büyü ve Özel Yetenekler
- Seviye atladıkça yeni büyüler öğrenebilirsiniz.
- Büyüler mana kullanır ve savaşta çeşitli etkiler yaratır (hasar, iyileştirme, savunma artırma vb.).
- Mana sınırsız modu hile menüsünden açılabilir.

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! İşte adımlar:

1. Repoyu fork'layın
2. Yeni branch oluşturun (`git checkout -b feature/awesome-feature`)
3. Değişikliklerinizi commit'leyin
4. Branch'inizi push'layın
5. Pull Request açın

## 📜 Lisans

MIT Lisansı - Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 📞 İletişim

Memati - [@Memati8383](https://github.com/Memati8383) - memati@example.com

Proje Linki: [https://github.com/Memati8383/PyQuest-RPG](https://github.com/Memati8383/PyQuest-RPG)

## 🙏 Teşekkürler

- Tüm beta testçiler
- Python topluluğu
- Open source katkıcıları

---

> "Bir kod satırı, bin söze bedeldir." - Bilge Programcı
