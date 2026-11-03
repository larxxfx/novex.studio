"""Plan dosyasındaki her slot için standart video klasörü oluşturur (var olanın üzerine yazmaz).
Kullanım: python3 araclar/video_klasoru_olustur.py
Klasör adı: videolar/YYYY-AA-GG_SSDD_kisa-ad/
"""
import os, shutil, re

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SABLON = os.path.join(KOK, "sablonlar")

# (tarih, saat, kısa ad, slot adı, başlık, seri bölümü)
SLOTLAR = [
    ("2026-11-04", "0800", "en-uzun-duz-rota", "Harita Şoku", "Dümeni hiç kırmadan 32 bin kilometre", ""),
    ("2026-11-04", "1100", "akdeniz-kurudugunda", "Ya Şöyle Olsaydı?", "Cebelitarık kapansaydı Akdeniz kururdu", ""),
    ("2026-11-04", "1400", "gobeklitepe", "Tarih Dosyası", "Piramitlerden 7.000 yıl önce", ""),
    ("2026-11-04", "1700", "son-sinyal-b01", "SON SİNYAL", "Bölüm 1 — 03.17", "B01"),
    ("2026-11-04", "2000", "tokyo-artik-en-buyuk-degil", "Dünya Düzeni", "Tokyo artık dünyanın en büyük şehri değil", ""),
    ("2026-11-05", "0800", "diomede-21-saat", "Harita Şoku", "3,8 kilometre, 21 saat", ""),
    ("2026-11-05", "1100", "everest-cukurda", "Ya Şöyle Olsaydı?", "Everest'i okyanusun en derin yerine koysak", ""),
    ("2026-11-05", "1400", "ayasofya-kubbe-558", "Tarih Dosyası", "Ayasofya'nın kubbesi neden çöktü?", ""),
    ("2026-11-05", "1700", "son-sinyal-b02", "SON SİNYAL", "Bölüm 2 — İlk Sinyal", "B02"),
    ("2026-11-05", "2000", "bolivya-donanmasi", "Dünya Düzeni", "Denizi olmayan ülkenin donanması", ""),
    ("2026-11-06", "0800", "nemo-noktasi", "Harita Şoku", "En yakın insanlar uzayda", ""),
    ("2026-11-06", "1100", "yesil-sahra", "Ya Şöyle Olsaydı?", "Sahra yeniden yeşerseydi", ""),
    ("2026-11-06", "1400", "truva-dokuz-katman", "Tarih Dosyası", "Truva'nın dokuz katmanı", ""),
    ("2026-11-06", "1700", "son-sinyal-b03", "SON SİNYAL", "Bölüm 3 — Karşı Kıyı", "B03"),
    ("2026-11-06", "2000", "kaliningrad", "Dünya Düzeni", "Rusya'nın Avrupa'nın ortasındaki parçası", ""),
    ("2026-11-07", "0800", "cin-tek-saat", "Harita Şoku", "Bir ülke, tek saat", ""),
    ("2026-11-07", "1100", "karadeniz-gol", "Ya Şöyle Olsaydı?", "Karadeniz bir göl olarak kalsaydı", ""),
    ("2026-11-07", "1400", "derinkuyu", "Tarih Dosyası", "Yer altında 20.000 kişi", ""),
    ("2026-11-07", "1700", "son-sinyal-b04", "SON SİNYAL", "Bölüm 4 — Kayıt", "B04"),
    ("2026-11-07", "2000", "svalbard-tohum-kasasi", "Dünya Düzeni", "Kıyamet günü tohum kasası", ""),
    ("2026-11-08", "0800", "kanada-golleri", "Harita Şoku", "Dünyadaki göllerin %62'si tek ülkede", ""),
    ("2026-11-08", "1100", "malakka-kapanirsa", "Ya Şöyle Olsaydı?", "Malakka kapanırsa", ""),
    ("2026-11-08", "1400", "istanbul-1509", "Tarih Dosyası", "İstanbul'un Küçük Kıyameti: 1509", ""),
    ("2026-11-08", "1700", "son-sinyal-b05", "SON SİNYAL", "Bölüm 5 — Eksik Kişi", "B05"),
    ("2026-11-08", "2000", "afrikanin-gercek-boyutu", "Dünya Düzeni", "Afrika'nın gerçek boyutu", ""),
]

ASAMALAR = ["01_brief.md:brief.md", "02_kaynaklar.md:kaynaklar.md", "03_senaryo.md:senaryo.md",
            "04_sahne_plani.md:sahne_plani.md", "05_seslendirme.txt:seslendirme.txt",
            "06_paket.md:paket.md", "inceleme_chatgpt.md:inceleme_chatgpt.md"]

for tarih, saat, ad, slot, baslik, bolum in SLOTLAR:
    d = os.path.join(KOK, "videolar", f"{tarih}_{saat}_{ad}")
    os.makedirs(os.path.join(d, "qc"), exist_ok=True)
    os.makedirs(os.path.join(d, "kapak"), exist_ok=True)
    for pair in ASAMALAR:
        hedef, kaynak = pair.split(":")
        p = os.path.join(d, hedef)
        if os.path.exists(p):
            continue
        txt = open(os.path.join(SABLON, kaynak), encoding="utf-8").read()
        if kaynak == "brief.md":
            txt = txt.replace("YYYY-AA-GG_SSDD_kisa-ad", f"{tarih}_{saat}_{ad}") \
                     .replace('slot: "08.00"', f'slot: "{saat[:2]}.{saat[2:]}"') \
                     .replace('seri: ""', f'seri: "{"son-sinyal/" + bolum if bolum else ""}"') \
                     .replace("# Brief", f"# {slot} — {baslik}\n\nPlan: `plan/2026-11-04_08_plan.md`")
        open(p, "w", encoding="utf-8").write(txt)
    keep = os.path.join(d, "qc", ".gitkeep")
    open(keep, "a").close(); open(os.path.join(d, "kapak", ".gitkeep"), "a").close()
print(len(SLOTLAR), "video klasörü hazır")
