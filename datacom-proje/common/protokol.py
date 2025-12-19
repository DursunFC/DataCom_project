def paket_olustur(veri: str, yontem: str, kontrol: str) -> str:
    return f"{veri}|{yontem}|{kontrol}"

def paket_coz(paket: str):
    parcalar = paket.split("|")
    if len(parcalar) < 3:
        raise ValueError("Geçersiz paket. DATA|METHOD|CONTROL bekleniyor.")
    veri = parcalar[0]
    yontem = parcalar[1]
    kontrol = "|".join(parcalar[2:])
    return veri, yontem, kontrol
