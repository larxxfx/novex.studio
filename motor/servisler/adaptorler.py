"""Kling, Higgsfield ve GPT Images adaptörleri — birbirinden bağımsız.
Fiyatlar üçüncü taraf kaynaklardan (Kasım 2026); birincil fiyat sayfasıyla doğrulanmadan bütçe kararı verilmez.
Gerçek HTTP çağrıları (_gonder) yazılmadı: anahtar ve resmi doküman olmadan istek biçimi uydurulmaz.
"""
from .temel import Adaptor, Is


class KlingAdaptor(Adaptor):
    """Kling AI (Kuaishou). Resmî API: başvuru + onay ile anahtar; ayrı kredi havuzu. Image-to-video öncelikli."""
    ad = "kling"
    anahtar_degiskeni = "KLING_API_KEY"
    fiyat_kaynagi = "EvoLink yönlendirmesi, Nisan 2026: Kling 3.0 ≈ $0.075/sn, Turbo ≈ $0.106/sn (resmî fiyat doğrulanmadı)"
    USD_SN = 0.075

    def tahmini_maliyet_usd(self, is_: Is) -> float:
        return round(self.USD_SN * max(is_.sure_sn, 5) * is_.adet, 4)  # klipler genelde ≥5 sn faturalanır (varsayım)


class HiggsfieldAdaptor(Adaptor):
    """Higgsfield API: kendi kendine kayıt, ön ödemeli dolar bakiyesi, 50+ model (Kling, Seedance, Wan, DoP…).
    Web planı API erişimi vermez; API ayrı bakiye ister."""
    ad = "higgsfield"
    anahtar_degiskeni = "HIGGSFIELD_API_KEY"
    fiyat_kaynagi = "Higgsfield blogu, 2026: ör. DoP $0.125/üretim, PixVerse 6 $0.115/sn, LTX 2.5 Pro $0.17/sn"
    USD_SN = 0.115

    def tahmini_maliyet_usd(self, is_: Is) -> float:
        if is_.ek.get("model") == "dop":
            return round(0.125 * is_.adet, 4)
        return round(self.USD_SN * max(is_.sure_sn, 5) * is_.adet, 4)


class GptGorselAdaptor(Adaptor):
    """OpenAI GPT Images (gpt-image-2). Token bazlı faturalama; şeffaf arka plan gpt-image-2'de önizleme (preview).
    Karakter tutarlılığı: referans görsel + düzenleme uç noktası ile poz üretimi."""
    ad = "gpt-image"
    anahtar_degiskeni = "OPENAI_API_KEY"
    fiyat_kaynagi = "Üçüncü taraf özetleri, 2026: 1024px görsel ≈ $0.006 (düşük) – $0.21 (yüksek kalite)"
    USD_GORSEL = {"dusuk": 0.006, "orta": 0.053, "yuksek": 0.211}

    def tahmini_maliyet_usd(self, is_: Is) -> float:
        return round(self.USD_GORSEL[is_.ek.get("kalite", "orta")] * is_.adet, 4)


def tum_adaptorler(**kw):
    return {a.ad: a for a in (KlingAdaptor(**kw), HiggsfieldAdaptor(**kw), GptGorselAdaptor(**kw))}
