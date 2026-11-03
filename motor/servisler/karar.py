"""Hibrit üretim karar motoru: her sahne için en düşük maliyetli ama yeterli yöntemi seçer.

Yöntemler: "yerel" (Canvas PNG motoru, $0) · "yeni_kare" (GPT Images ile eksik hareket kareleri, sonra yerel) ·
"kling" (image-to-video) · "higgsfield" (sinematik kamera). Varsayılan her zaman yerel; harici servis yalnızca gerekçeyle.

Sahne özeti (dict):
  hareketler: ["idle","run",...]           karakterin bu sahnede yapacağı hareketler
  mevcut_hareketler: ["idle","run","jump"]  manifestte karesi olan hareketler
  kamera: "sabit"|"kaydirma"|"zoom"|"takip"|"orbit"|"dolly"|"vinç"|"el_kamerasi"
  karmasik_beden: bool                     dans, dövüş, nesneyle ayrıntılı etkileşim vb.
  sure_sn: float
  tekrar_kullanim: int                     bu eksik hareket kaç videoda daha kullanılacak (kare üretmeyi amorti eder)
"""
from .temel import Is

YEREL_KAMERA = {"sabit", "kaydirma", "zoom", "takip"}
SINEMATIK_KAMERA = {"orbit", "dolly", "vinç", "el_kamerasi"}


def karar_ver(sahne: dict, adaptorler: dict) -> dict:
    eksik = [h for h in sahne.get("hareketler", []) if h not in sahne.get("mevcut_hareketler", [])]
    kamera = sahne.get("kamera", "sabit")
    sure = float(sahne.get("sure_sn", 5))
    gerekce, uyari = [], []

    def hazir(ad):
        a = adaptorler.get(ad)
        return a is not None and a.yapilandirildi_mi()

    if not eksik and kamera in YEREL_KAMERA and not sahne.get("karmasik_beden"):
        return {"yontem": "yerel", "tahmini_usd": 0.0, "gerekce": ["tüm hareketlerin karesi var", f"kamera '{kamera}' yerelde yapılır"], "uyari": []}

    secenekler = []
    if eksik and not sahne.get("karmasik_beden"):
        # eksik hareket için kare üretmek tek seferlik maliyettir; tekrar kullanımda en ucuz yol
        adet = 6 * len(eksik)  # hareket başına ~6 kare (varsayım)
        usd = adaptorler["gpt-image"].tahmini_maliyet_usd(Is(tur="gorsel", adet=adet, ek={"kalite": "orta"})) if "gpt-image" in adaptorler else None
        secenekler.append(("yeni_kare", usd, f"eksik hareket(ler) {eksik}: ~{adet} kare üretilir, sonra yerel motorla tekrar tekrar kullanılır"))
    if sahne.get("karmasik_beden") or (eksik and sahne.get("tekrar_kullanim", 0) == 0):
        usd = adaptorler["kling"].tahmini_maliyet_usd(Is(tur="image_to_video", sure_sn=sure)) if "kling" in adaptorler else None
        secenekler.append(("kling", usd, "karmaşık/tek seferlik beden hareketi → image-to-video"))
    if kamera in SINEMATIK_KAMERA:
        usd = adaptorler["higgsfield"].tahmini_maliyet_usd(Is(tur="image_to_video", sure_sn=sure)) if "higgsfield" in adaptorler else None
        secenekler.append(("higgsfield", usd, f"sinematik kamera '{kamera}'"))

    secenekler = [s for s in secenekler if s[1] is not None]
    secenekler.sort(key=lambda s: s[1])
    servis = {"yeni_kare": "gpt-image", "kling": "kling", "higgsfield": "higgsfield"}
    for yontem, usd, neden in secenekler:
        if hazir(servis[yontem]):
            return {"yontem": yontem, "tahmini_usd": usd, "gerekce": [neden], "uyari": uyari,
                    "onay_gerekli": True, "alternatifler": [(y, u) for y, u, _ in secenekler if y != yontem]}
        uyari.append(f"{yontem} uygun olurdu (~${usd:.2f}) ama {servis[yontem]} yapılandırılmadı")

    # hiçbir harici servis hazır değil → yerel motorla en yakın karşılık (sahte üretim yok)
    yedek = [h if h in sahne.get("mevcut_hareketler", []) else "idle" for h in sahne.get("hareketler", [])]
    kam = kamera if kamera in YEREL_KAMERA else "zoom"
    return {"yontem": "yerel_yedek", "tahmini_usd": 0.0, "hareket_yerine": dict(zip(sahne.get("hareketler", []), yedek)),
            "kamera_yerine": kam, "gerekce": ["harici servis yok → yerel motorla basitleştirildi"], "uyari": uyari}
