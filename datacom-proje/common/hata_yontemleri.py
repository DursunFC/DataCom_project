import binascii
from typing import Tuple

def _bytes_to_bits(b: bytes) -> str:
    return "".join(f"{x:08b}" for x in b)

def _bits_to_bytes(bits: str) -> bytes:
    if len(bits) % 8 != 0:
        bits = bits + "0" * (8 - (len(bits) % 8))
    out = bytearray()
    for i in range(0, len(bits), 8):
        out.append(int(bits[i:i+8], 2))
    return bytes(out)

def _ascii_bits(metin: str) -> str:
    b = metin.encode("latin-1", errors="replace")
    return _bytes_to_bits(b)

def parite_kontrol(metin: str, tur: str = "CIFT") -> str:
    bits = _ascii_bits(metin)
    ones = bits.count("1")
    tur = tur.upper()
    if tur == "CIFT":
        bit = "0" if ones % 2 == 0 else "1"
        return f"CIFT:{bit}"
    bit = "0" if ones % 2 == 1 else "1"
    return f"TEK:{bit}"

def iki_b_parite_kontrol(metin: str, satir: int = 8, sutun: int = 8) -> str:
    bits = _ascii_bits(metin)
    blok = satir * sutun
    if len(bits) % blok != 0:
        bits += "0" * (blok - (len(bits) % blok))
    kontroller = []
    for k in range(0, len(bits), blok):
        b = bits[k:k+blok]
        mat = [list(b[r*sutun:(r+1)*sutun]) for r in range(satir)]
        sat_par = []
        for r in range(satir):
            sat_par.append("0" if mat[r].count("1") % 2 == 0 else "1")
        sut_par = []
        for c in range(sutun):
            s = sum(1 for r in range(satir) if mat[r][c] == "1")
            sut_par.append("0" if s % 2 == 0 else "1")
        ctrl_bits = "".join(sat_par) + "".join(sut_par)
        kontroller.append(f"{int(ctrl_bits, 2):04X}")
    return ",".join(kontroller)

def crc16_kontrol(metin: str) -> str:
    crc = binascii.crc_hqx(metin.encode("utf-8", errors="replace"), 0xFFFF)
    return f"{crc:04X}"

def crc32_kontrol(metin: str) -> str:
    crc = binascii.crc32(metin.encode("utf-8", errors="replace")) & 0xFFFFFFFF
    return f"{crc:08X}"

def ip_saglama_kontrol(metin: str) -> str:
    data = metin.encode("utf-8", errors="replace")
    if len(data) % 2 == 1:
        data += b"\x00"
    s = 0
    for i in range(0, len(data), 2):
        w = (data[i] << 8) + data[i+1]
        s += w
        s = (s & 0xFFFF) + (s >> 16)
    checksum = (~s) & 0xFFFF
    return f"{checksum:04X}"

DATA_POS = [3,5,6,7,9,10,11,12]
PAR_POS = [1,2,4,8]

def _hamming_parite4(byte_val: int) -> str:
    data_bits = f"{byte_val:08b}"
    code = ["0"] * 13
    for bit, pos in zip(data_bits, DATA_POS):
        code[pos] = bit
    for p in PAR_POS:
        x = 0
        for i in range(1, 13):
            if i & p and i != p:
                x ^= int(code[i])
        code[p] = str(x)
    return "".join(code[p] for p in PAR_POS)

def hamming_kontrol(metin: str) -> str:
    b = metin.encode("latin-1", errors="replace")
    parity_bits = "".join(_hamming_parite4(x) for x in b)
    if len(parity_bits) % 8 != 0:
        parity_bits += "0" * (8 - (len(parity_bits) % 8))
    packed = _bits_to_bytes(parity_bits)
    return packed.hex().upper()

def _hamming_duzelt_byte(byte_val: int, p4: str) -> Tuple[int, int]:
    data_bits = f"{byte_val:08b}"
    code = ["0"] * 13
    for bit, pos in zip(data_bits, DATA_POS):
        code[pos] = bit
    for bit, pos in zip([p4[0], p4[1], p4[2], p4[3]], PAR_POS):
        code[pos] = bit
    sendrom = 0
    for p in PAR_POS:
        x = 0
        for i in range(1, 13):
            if i & p:
                x ^= int(code[i])
        if x != 0:
            sendrom |= p
    if sendrom != 0 and 1 <= sendrom <= 12:
        code[sendrom] = "0" if code[sendrom] == "1" else "1"
    duzeltilmis = "".join(code[pos] for pos in DATA_POS)
    return int(duzeltilmis, 2), sendrom

def hamming_kontrol_ve_duzelt(alinan_metin: str, gelen_kontrol_hex: str):
    gelen_kontrol_hex = gelen_kontrol_hex.strip().upper()
    tam_eslesme = (hamming_kontrol(alinan_metin) == gelen_kontrol_hex)
    try:
        ctrl_bytes = bytes.fromhex(gelen_kontrol_hex)
    except Exception:
        return False, alinan_metin, "Hamming kontrol hex geçersiz."
    ctrl_bits = _bytes_to_bits(ctrl_bytes)
    rb = alinan_metin.encode("latin-1", errors="replace")
    gereken = len(rb) * 4
    if len(ctrl_bits) < gereken:
        return False, alinan_metin, "Hamming kontrol veriye göre kısa."
    sendrom_say = 0
    out = bytearray()
    for i, byte_val in enumerate(rb):
        p4 = ctrl_bits[i*4:(i+1)*4]
        duz, syn = _hamming_duzelt_byte(byte_val, p4)
        out.append(duz)
        if syn != 0:
            sendrom_say += 1
    duzeltilmis_metin = out.decode("latin-1", errors="replace")
    sonra_ok = (hamming_kontrol(duzeltilmis_metin) == gelen_kontrol_hex)
    if tam_eslesme:
        return True, alinan_metin, "Hata yok."
    if sonra_ok:
        return False, duzeltilmis_metin, f"Düzeltildi. duzeltilen_blok={sendrom_say}"
    return False, alinan_metin, f"Hata var, düzeltilemedi. duzeltilen_blok={sendrom_say}"
