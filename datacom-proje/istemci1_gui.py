import sys
import socket
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QComboBox, QMessageBox
)

from common.protokol import paket_olustur
from common import hata_yontemleri as hy

SECENEKLER = [
    "Parite (Çift)",
    "Parite (Tek)",
    "2B Parite (8x8)",
    "CRC16",
    "CRC32",
    "Hamming(12,8)",
    "IP Sağlama Toplamı",
]

class Istemci1(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("İstemci 1 - Gönderici")

        ana = QVBoxLayout()

        satir = QHBoxLayout()
        satir.addWidget(QLabel("Sunucu IP:"))
        self.host = QLineEdit("127.0.0.1")
        satir.addWidget(self.host)
        satir.addWidget(QLabel("Port:"))
        self.port = QLineEdit("5000")
        self.port.setFixedWidth(90)
        satir.addWidget(self.port)
        ana.addLayout(satir)

        ana.addWidget(QLabel("Metin:"))
        self.metin = QTextEdit()
        self.metin.setPlaceholderText("Örn: HELLO")
        ana.addWidget(self.metin)

        satir2 = QHBoxLayout()
        satir2.addWidget(QLabel("Yöntem:"))
        self.yontem = QComboBox()
        self.yontem.addItems(SECENEKLER)
        satir2.addWidget(self.yontem)
        ana.addLayout(satir2)

        ana.addWidget(QLabel("Kontrol Bilgisi:"))
        self.kontrol = QLineEdit()
        self.kontrol.setReadOnly(True)
        ana.addWidget(self.kontrol)

        butonlar = QHBoxLayout()
        self.uret = QPushButton("Kontrol Üret")
        self.gonder = QPushButton("Paketi Gönder")
        butonlar.addWidget(self.uret)
        butonlar.addWidget(self.gonder)
        ana.addLayout(butonlar)

        ana.addWidget(QLabel("Paket:"))
        self.paket = QLineEdit()
        self.paket.setReadOnly(True)
        ana.addWidget(self.paket)

        self.setLayout(ana)

        self.uret.clicked.connect(self.kontrol_uret)
        self.gonder.clicked.connect(self.paket_gonder)

    def kontrol_uret(self):
        metin = self.metin.toPlainText()
        secim = self.yontem.currentText()

        if secim == "Parite (Çift)":
            kod = "PARITE_CIFT"
            ctrl = hy.parite_kontrol(metin, "CIFT")
        elif secim == "Parite (Tek)":
            kod = "PARITE_TEK"
            ctrl = hy.parite_kontrol(metin, "TEK")
        elif secim == "2B Parite (8x8)":
            kod = "IKI_B_PARITE_8X8"
            ctrl = hy.iki_b_parite_kontrol(metin, 8, 8)
        elif secim == "CRC16":
            kod = "CRC16"
            ctrl = hy.crc16_kontrol(metin)
        elif secim == "CRC32":
            kod = "CRC32"
            ctrl = hy.crc32_kontrol(metin)
        elif secim == "Hamming(12,8)":
            kod = "HAMMING_12_8"
            ctrl = hy.hamming_kontrol(metin)
        elif secim == "IP Sağlama Toplamı":
            kod = "IP_SAGLAMA"
            ctrl = hy.ip_saglama_kontrol(metin)
        else:
            kod = "BILINMIYOR"
            ctrl = ""

        pkt = paket_olustur(metin, kod, ctrl)
        self.kontrol.setText(ctrl)
        self.paket.setText(pkt)

    def paket_gonder(self):
        if not self.paket.text():
            self.kontrol_uret()

        host = self.host.text().strip()
        try:
            port = int(self.port.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Hata", "Port sayı olmalı.")
            return

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            s.sendall(self.paket.text().encode("utf-8", errors="replace"))
            s.close()
            QMessageBox.information(self, "OK", "Paket gönderildi.")
        except Exception as e:
            QMessageBox.critical(self, "Gönderilemedi", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Istemci1()
    w.resize(640, 520)
    w.show()
    sys.exit(app.exec())
