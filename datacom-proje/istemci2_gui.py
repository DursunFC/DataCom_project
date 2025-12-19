import sys
import socket
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QMessageBox
)

from common.protokol import paket_coz
from common import hata_yontemleri as hy

class Dinleyici(QThread):
    alindi = Signal(str)
    durum = Signal(str)

    def __init__(self, host: str, port: int):
        super().__init__()
        self.host = host
        self.port = port
        self._dur = False

    def dur(self):
        self._dur = True
        try:
            socket.create_connection((self.host, self.port), timeout=0.3).close()
        except:
            pass

    def run(self):
        self.durum.emit("Dinleniyor...")
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((self.host, self.port))
        srv.listen(5)

        while not self._dur:
            try:
                conn, _ = srv.accept()
            except Exception:
                continue
            if self._dur:
                break
            raw = conn.recv(65535)
            conn.close()
            self.alindi.emit(raw.decode("utf-8", errors="replace"))

        srv.close()
        self.durum.emit("Durduruldu.")

class Istemci2(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("İstemci 2 - Alıcı + Denetleyici")
        self.isparcasi = None

        ana = QVBoxLayout()

        s1 = QHBoxLayout()
        s1.addWidget(QLabel("Dinleme IP:"))
        self.host = QLineEdit("127.0.0.1")
        s1.addWidget(self.host)
        s1.addWidget(QLabel("Port:"))
        self.port = QLineEdit("6000")
        self.port.setFixedWidth(90)
        s1.addWidget(self.port)
        ana.addLayout(s1)

        b = QHBoxLayout()
        self.baslat = QPushButton("Dinlemeyi Başlat")
        self.durdur = QPushButton("Durdur")
        self.durdur.setEnabled(False)
        b.addWidget(self.baslat)
        b.addWidget(self.durdur)
        ana.addLayout(b)

        self.durum = QLabel("Durum: Hazır")
        ana.addWidget(self.durum)

        ana.addWidget(QLabel("Çıktı:"))
        self.cikti = QTextEdit()
        self.cikti.setReadOnly(True)
        ana.addWidget(self.cikti)

        self.setLayout(ana)

        self.baslat.clicked.connect(self.basla)
        self.durdur.clicked.connect(self.dur)

    def basla(self):
        if self.isparcasi and self.isparcasi.isRunning():
            return
        try:
            h = self.host.text().strip()
            p = int(self.port.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Hata", "Port sayı olmalı.")
            return

        self.isparcasi = Dinleyici(h, p)
        self.isparcasi.alindi.connect(self.paket_geldi)
        self.isparcasi.durum.connect(lambda s: self.durum.setText(f"Durum: {s}"))
        self.isparcasi.start()

        self.baslat.setEnabled(False)
        self.durdur.setEnabled(True)

    def dur(self):
        if self.isparcasi:
            self.isparcasi.dur()
            self.isparcasi.wait(1000)
        self.baslat.setEnabled(True)
        self.durdur.setEnabled(False)

    def paket_geldi(self, paket: str):
        self.cikti.append(f"--- Paket ---\n{paket}\n")
        try:
            veri, yontem, gelen = paket_coz(paket)
        except Exception as e:
            self.cikti.append(f"Çözümleme hatası: {e}\n")
            return

        self.cikti.append(f"Alınan Veri      : {veri}")
        self.cikti.append(f"Yöntem           : {yontem}")
        self.cikti.append(f"Gelen Kontrol    : {gelen}")

        hesap = ""
        durum = "BILINMIYOR"
        ek = ""

        yu = yontem.strip().upper()

        if yu == "PARITE_CIFT":
            hesap = hy.parite_kontrol(veri, "CIFT")
            durum = "DOĞRU" if hesap == gelen else "BOZUK"
        elif yu == "PARITE_TEK":
            hesap = hy.parite_kontrol(veri, "TEK")
            durum = "DOĞRU" if hesap == gelen else "BOZUK"
        elif yu == "IKI_B_PARITE_8X8":
            hesap = hy.iki_b_parite_kontrol(veri, 8, 8)
            durum = "DOĞRU" if hesap == gelen.strip() else "BOZUK"
        elif yu == "CRC16":
            hesap = hy.crc16_kontrol(veri)
            durum = "DOĞRU" if hesap == gelen.strip().upper() else "BOZUK"
        elif yu == "CRC32":
            hesap = hy.crc32_kontrol(veri)
            durum = "DOĞRU" if hesap == gelen.strip().upper() else "BOZUK"
        elif yu == "IP_SAGLAMA":
            hesap = hy.ip_saglama_kontrol(veri)
            durum = "DOĞRU" if hesap == gelen.strip().upper() else "BOZUK"
        elif yu == "HAMMING_12_8":
            tam, duz, bilgi = hy.hamming_kontrol_ve_duzelt(veri, gelen)
            hesap = hy.hamming_kontrol(veri)
            if tam:
                durum = "DOĞRU"
            else:
                if duz != veri:
                    durum = "BOZUK (DÜZELTİLDİ)"
                    ek = f"Düzeltilmiş Veri : {duz}\n{bilgi}"
                else:
                    durum = "BOZUK"
                    ek = bilgi
        else:
            durum = "BILINMEYEN_YONTEM"

        self.cikti.append(f"Hesaplanan Kontrol: {hesap}")
        self.cikti.append(f"Durum            : {durum}")
        if ek:
            self.cikti.append(ek)
        self.cikti.append("")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Istemci2()
    w.resize(820, 560)
    w.show()
    sys.exit(app.exec())
