import random
import string

def _rastgele_bit_cevir_bytes(b: bytes, adet: int = 1) -> bytes:
    ba = bytearray(b)
    if not ba:
        return b
    for _ in range(adet):
        i = random.randrange(len(ba))
        bit = 1 << random.randrange(8)
        ba[i] ^= bit
    return bytes(ba)

def bit_cevir(veri: str) -> str:
    b = veri.encode("utf-8", errors="replace")
    return _rastgele_bit_cevir_bytes(b, 1).decode("utf-8", errors="replace")

def coklu_bit_cevir(veri: str, adet: int = 3) -> str:
    b = veri.encode("utf-8", errors="replace")
    return _rastgele_bit_cevir_bytes(b, max(1, adet)).decode("utf-8", errors="replace")

def karakter_degistir(veri: str) -> str:
    if not veri:
        return veri
    i = random.randrange(len(veri))
    ch = random.choice(string.ascii_uppercase)
    return veri[:i] + ch + veri[i+1:]

def karakter_sil(veri: str) -> str:
    if len(veri) < 2:
        return veri
    i = random.randrange(len(veri))
    return veri[:i] + veri[i+1:]

def karakter_ekle(veri: str) -> str:
    i = random.randrange(len(veri) + 1)
    ch = random.choice(string.ascii_letters)
    return veri[:i] + ch + veri[i:]

def karakter_takas(veri: str) -> str:
    if len(veri) < 2:
        return veri
    i = random.randrange(len(veri) - 1)
    return veri[:i] + veri[i+1] + veri[i] + veri[i+2:]

def burst_hatasi(veri: str, min_len: int = 3, max_len: int = 8) -> str:
    if not veri:
        return veri
    n = len(veri)
    L = min(n, random.randint(min_len, max_len))
    bas = random.randrange(0, n - L + 1)
    parca = list(veri[bas:bas+L])
    for j in range(len(parca)):
        parca[j] = random.choice(string.ascii_letters)
    return veri[:bas] + "".join(parca) + veri[bas+L:]

BOZMA_YONTEMLERI = {
    "Yok": lambda s: s,
    "Bit Çevir": bit_cevir,
    "Karakter Değiştir": karakter_degistir,
    "Karakter Sil": karakter_sil,
    "Karakter Ekle": karakter_ekle,
    "Karakter Takas": karakter_takas,
    "Çoklu Bit Çevir": coklu_bit_cevir,
    "Burst Hatası": burst_hatasi,
}
