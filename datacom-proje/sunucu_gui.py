import sys
import socket
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTextEdit, QMessageBox, QSpinBox
)

from common.protokol import paket_coz, paket_olustur
from common.bozucu import BOZMA_YONTEMLERI

class SunucuIsParcasi(QThread):
    log = Signal(str)
    durum = Signal(str)

    def __init__(self, dinle_host: str, dinle_port: int, ilet_host: str, ilet_port: int,
                 bozma_adi: str, bit_adet: int):
        super().__init__()
        self.dinle_host = dinle_host
        self.dinle_port = dinle_port
        self.ilet_host = ilet_host
        self.ilet_port = ilet_port
        self.bozma_adi = bozma_adi
        self.bit_adet = bit_adet
        self._dur = False

    def dur(self):
        self._dur = True
        try:
            socket.create_connection((self.dinle_host, self.dinle_port), timeout=0.3).close()
        except:
            pass

    def run(self):
        self.durum.emit("Dinleniyor...")
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((self.dinle_host, self.dinle_port))
        srv.listen(5)

        while not self._dur:
            try:
                conn, _ = srv.accept()
            except Exception:
                continue
            if self._dur:
                break

            try:
                raw = conn.recv(65535)
                conn.close()
                pkt = raw.decode("utf-8", errors="replace")
                self.log.emit(f"[GELEN] {pkt}")

                veri, yontem, kontrol = paket_coz(pkt)

                fn = BOZMA_YONTEMLERI.get(self.bozma_adi, BOZMA_YONTEMLERI["Yok"])
                if self.bozma_adi == "Çoklu Bit Çevir":
                    bozuk = fn(veri, self.bit_adet)
                else:
                    bozuk = fn(veri)

                cikis = paket_olustur(bozuk, yontem, kontrol)
                self.log.emit(f"[GIDEN] {cikis}")

                fw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                fw.connect((self.ilet_host, self.ilet_port))
                fw.sendall(cikis.encode("utf-8", errors="replace"))
                fw.close()

                self.durum.emit(f"İletildi: {self.ilet_host}:{self.ilet_port}")

            except Exception as e:
                self.log.emit(f"[HATA] {e}")

        srv.close()
        self.durum.emit("Durduruldu.")

class Sunucu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sunucu - Ara Düğüm + Bozucu")
        self.isparcasi = None

        ana = QVBoxLayout()

        s1 = QHBoxLayout()
        s1.addWidget(QLabel("Dinleme IP:"))
        self.dinle_host = QLineEdit("127.0.0.1")
        s1.addWidget(self.dinle_host)
        s1.addWidget(QLabel("Port:"))
        self.dinle_port = QLineEdit("5000")
        self.dinle_port.setFixedWidth(90)
        s1.addWidget(self.dinle_port)
        ana.addLayout(s1)

        s2 = QHBoxLayout()
        s2.addWidget(QLabel("İletim IP (İstemci 2):"))
        self.ilet_host = QLineEdit("127.0.0.1")
        s2.addWidget(self.ilet_host)
        s2.addWidget(QLabel("Port:"))
        self.ilet_port = QLineEdit("6000")
        self.ilet_port.setFixedWidth(90)
        s2.addWidget(self.ilet_port)
        ana.addLayout(s2)

        s3 = QHBoxLayout()
        s3.addWidget(QLabel("Bozma:"))
        self.bozma = QComboBox()
        self.bozma.addItems(list(BOZMA_YONTEMLERI.keys()))
        s3.addWidget(self.bozma)

        s3.addWidget(QLabel("Bit Adedi:"))
        self.bit_adet = QSpinBox()
        self.bit_adet.setRange(1, 64)
        self.bit_adet.setValue(3)
        s3.addWidget(self.bit_adet)
        ana.addLayout(s3)

        b = QHBoxLayout()
        self.baslat = QPushButton("Başlat")
        self.durdur = QPushButton("Durdur")
        self.durdur.setEnabled(False)
        b.addWidget(self.baslat)
        b.addWidget(self.durdur)
        ana.addLayout(b)

        self.durum = QLabel("Durum: Hazır")
        ana.addWidget(self.durum)

        ana.addWidget(QLabel("Kayıt:"))
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        ana.addWidget(self.log)

        self.setLayout(ana)

        self.baslat.clicked.connect(self.sunucu_baslat)
        self.durdur.clicked.connect(self.sunucu_durdur)

    def sunucu_baslat(self):
        if self.isparcasi and self.isparcasi.isRunning():
            return
        try:
            lh = self.dinle_host.text().strip()
            lp = int(self.dinle_port.text().strip())
            fh = self.ilet_host.text().strip()
            fp = int(self.ilet_port.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Hata", "Port sayı olmalı.")
            return

        bozma_adi = self.bozma.currentText()
        bit_adet = int(self.bit_adet.value())

        self.isparcasi = SunucuIsParcasi(lh, lp, fh, fp, bozma_adi, bit_adet)
        self.isparcasi.log.connect(self.log.append)
        self.isparcasi.durum.connect(lambda s: self.durum.setText(f"Durum: {s}"))
        self.isparcasi.start()

        self.baslat.setEnabled(False)
        self.durdur.setEnabled(True)
        self.durum.setText("Durum: Başlatılıyor...")

    def sunucu_durdur(self):
        if self.isparcasi:
            self.isparcasi.dur()
            self.isparcasi.wait(1000)
        self.baslat.setEnabled(True)
        self.durdur.setEnabled(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Sunucu()
    w.resize(800, 560)
    w.show()
    sys.exit(app.exec())
