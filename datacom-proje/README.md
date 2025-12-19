# Hata Tespit/Düzeltme (PySide6 + Socket)

Projemiz 3 parçadan oluşuyor:

- **İstemci 1 (Gönderici):** Metin + yöntem seç, kontrol bilgisini üret, paketi gönder.
- **Sunucu (Bozucu):** Paketi alır, sadece veriyi bozar, İstemci 2’ye iletir.
- **İstemci 2 (Alıcı):** Paketi alır, kontrolü tekrar hesaplar, sonucu gösterir. Hamming seçiliyse tek-bit düzeltmeyi dener.

## Paket

`VERI|YONTEM|KONTROL`

## Kurulum

```bash
pip install -r requirements.txt
```

## Çalıştırma (3 terminal)

1) `python istemci2_gui.py`  
2) `python sunucu_gui.py`  
3) `python istemci1_gui.py`

Varsayılan portlar: 5000 (İstemci1→Sunucu), 6000 (Sunucu→İstemci2)
