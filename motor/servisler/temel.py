"""Harici üretim servisleri için ortak adaptör (yalnızca sunucu/yerel tarafta çalışır; tarayıcıya anahtar gitmez).

Güvenlik kuralları (kodla uygulanır):
  - API anahtarı yalnızca ortam değişkeninden okunur; dosyaya, loga, rapora yazılmaz (repr'de maskelenir).
  - Ücretli çağrı iki kilitle korunur: NOVEX_HARCAMA_ONAYI=evet ve iş başına tahmini maliyet ≤ NOVEX_IS_BASINA_MAKS_USD.
  - Doğrulanmamış bir API için sahte başarı dönülmez: _gonder() uygulanmamışsa EntegrasyonYok fırlatılır.
  - Geçici hatalarda (429, 5xx, zaman aşımı) üstel bekleme ile yeniden deneme; kalıcı hatada hemen durur.
"""
import os, time
from dataclasses import dataclass, field


class ServisHatasi(Exception): ...
class Yapilandirilmadi(ServisHatasi): ...
class HarcamaKilidi(ServisHatasi): ...
class EntegrasyonYok(ServisHatasi): ...
class GeciciHata(ServisHatasi): ...


@dataclass
class Is:
    tur: str                       # "image_to_video" | "text_to_video" | "gorsel" | "gorsel_duzenle"
    sure_sn: float = 0.0
    adet: int = 1
    en_boy: str = "9:16"
    cozunurluk: str = "1080p"
    girdi_gorsel: str | None = None
    istem: str = ""
    ek: dict = field(default_factory=dict)


@dataclass
class Sonuc:
    durum: str                     # "tamam" | "hata"
    dosyalar: list
    gercek_maliyet_usd: float | None
    servis: str
    ayrinti: str = ""


class Adaptor:
    ad = "temel"
    anahtar_degiskeni = ""          # ör. KLING_API_KEY
    fiyat_kaynagi = ""              # fiyatın nereden alındığı + tarih
    fiyat_dogrulandi = False        # birincil kaynaktan doğrulandı mı?

    def __init__(self, ortam=os.environ, bekleme=time.sleep):
        self._ortam, self._bekle = ortam, bekleme

    def __repr__(self):
        return f"<{self.ad} yapılandırıldı={self.yapilandirildi_mi()} anahtar=***>"

    def yapilandirildi_mi(self):
        return bool(self._ortam.get(self.anahtar_degiskeni))

    def tahmini_maliyet_usd(self, is_: Is) -> float:
        raise NotImplementedError

    def harcama_kontrol(self, is_: Is):
        if not self.yapilandirildi_mi():
            raise Yapilandirilmadi(f"{self.ad}: {self.anahtar_degiskeni} ortam değişkeni yok")
        if self._ortam.get("NOVEX_HARCAMA_ONAYI") != "evet":
            raise HarcamaKilidi(f"{self.ad}: ücretli çağrı kilitli (NOVEX_HARCAMA_ONAYI=evet değil)")
        tahmin = self.tahmini_maliyet_usd(is_)
        sinir = float(self._ortam.get("NOVEX_IS_BASINA_MAKS_USD", "0"))
        if tahmin > sinir:
            raise HarcamaKilidi(f"{self.ad}: tahmini ${tahmin:.3f} > iş başına sınır ${sinir:.2f}")
        return tahmin

    def _gonder(self, is_: Is, anahtar: str) -> Sonuc:
        raise EntegrasyonYok(f"{self.ad}: istek biçimi birincil API dokümanıyla doğrulanmadı; "
                             "anahtar + doküman gelince yazılacak (sahte başarı dönülmez)")

    def uret(self, is_: Is, deneme=3, ilk_bekleme=2.0) -> Sonuc:
        self.harcama_kontrol(is_)
        anahtar = self._ortam[self.anahtar_degiskeni]
        son = None
        for i in range(deneme):
            try:
                return self._gonder(is_, anahtar)
            except GeciciHata as e:
                son = e
                self._bekle(ilk_bekleme * (2 ** i))
        raise ServisHatasi(f"{self.ad}: {deneme} denemede başarısız — {son}")
