
# Python Terminal RPG Oyunu

## Proje Hakkında

Python 3 ile geliştirilmiş, terminal tabanlı, renkli ve metin tabanlı RPG (Rol Yapma Oyunu). Oyuncu karakteri ile düşmanlarla savaşır, görevler yapar, envanter yönetir, seviye atlar ve çeşitli eşyalar toplar.

---

## Özellikler

- Renkli terminal arayüzü (Colorama ile)
- Seviye atlama ve deneyim kazanma sistemi
- Çok sayıda düşman türü ve zorluk seviyeleri
- Envanter ve eşya yönetimi (silahlar, büyüler, sağlık paketleri)
- Mağaza sistemi ile eşya satın alma
- Görev sistemi
- Hile modu (cheats)
- Savaş, kaçma ve eşya kullanma seçenekleri
- Detaylı ve açıklayıcı kullanıcı mesajları
- Kaydetme/yükleme (ileride eklenebilir)

---

## Gereksinimler

- Python 3.6 veya üzeri
- colorama kütüphanesi

### Kurulum

```bash
pip install colorama
```

---

## Nasıl Çalıştırılır?

Terminal veya komut satırından:

```bash
python main.py
```

---

## Oynanış

- Menüden seçim yaparak savaşabilir, mağazaya girebilir, envanteri görüntüleyebilir veya oyundan çıkabilirsiniz.
- Savaşta düşmana saldırabilir, büyü kullanabilir veya kaçabilirsiniz.
- Envantere yeni eşyalar eklenir, bunları kullanabilirsiniz.
- Seviye atladıkça oyuncu güçlenir.
- Mağazada altın karşılığı eşya alabilirsiniz.

---

## Kullanılan Komutlar / Menü

| Komut           | Açıklama                          |
|-----------------|---------------------------------|
| Savaş           | Düşmanlarla savaşa gir           |
| Envanter        | Sahip olduğun eşyaları gör       |
| Mağaza          | Eşya satın al                    |
| Hile Menüsü     | Oyun içi özel özellikler (aktif) |
| Çıkış           | Oyunu kapat                      |

---

## Oyun Mekanikleri

### Seviye Sistemi

- Deneyim puanı kazanılır.
- Belirli XP değerlerine ulaşıldığında seviye atlanır.
- Seviye artınca HP, mana, saldırı gücü gibi değerler yükselir.

### Envanter

- Maksimum 20 eşya tutabilir.
- Eşyalar farklı türde olabilir: silah, iksir, büyü kitabı vb.
- Envanterde eşya seçilerek kullanılabilir veya atılabilir.

### Savaş

- Düşmanlarla sıra tabanlı savaş sistemi.
- Oyuncu saldırabilir, büyü kullanabilir veya kaçabilir.
- Düşman türüne göre farklı saldırılar olabilir.
- Kaçma şansı %33.

### Hile Modu

- Aktif edilirse oyuncuya özel güçler verir.
- Örneğin, sınırsız mana veya çok güçlü silah.

---

## Sıkça Sorulan Sorular (SSS)

**S: Oyun neden açılmıyor?**  
C: Python 3 ve colorama yüklü olduğundan emin olun.

**S: Envanter neden dolu gözüküyor?**  
C: Maksimum 20 eşya taşıyabilirsiniz.

**S: Hile menüsünü nasıl açarım?**  
C: `CHEATS` değişkenini `True` yapmalısınız.

---

## Katkıda Bulunma

1. Fork yapın  
2. Yeni özellikler ekleyin veya hata düzeltin  
3. Pull request gönderin  

Her türlü katkı memnuniyetle karşılanır!

---

## Lisans

MIT Lisansı — dilediğiniz gibi kullanabilir, değiştirebilir ve dağıtabilirsiniz.

---

## Sürüm Notları

- v1.0 - Temel oyun mekanikleri tamamlandı  
- v1.1 - Envanter sistemi eklendi  
- v1.2 - Hile modu aktif edildi  
- v1.3 - Mağaza ve görev sistemi geliştirildi  

---

## İletişim

- E-posta: example@example.com  
- GitHub: [github.com/kullaniciadi](https://github.com/kullaniciadi)  

---

## Teşekkürler

- Python topluluğu  
- Colorama geliştiricileri  
- Beta test kullanıcıları  

